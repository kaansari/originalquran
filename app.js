(() => {
  // Constants

  const EXTERNAL_VERSE_BASE_URL =
    "https://corpuscoranicum.de/en/verse-navigator/";
  const wordsDataMeta = document.querySelector('meta[name="quran-words-file"]');
  const wordsDataPath =
    wordsDataMeta?.content?.trim() || "json/quran_words.json";

  const isChapterView = document.querySelector('meta[name="quran-view"]')?.content === 'chapter';
  const combinedDataPath = document.querySelector('meta[name="quran-combined-file"]')?.content || 'json/combined_quran.json';

  const paginationDataPath = document.querySelector('meta[name="quran-pagination-file"]')?.content || 'json/pagination_map.json';
  const pageStorageKey = document.querySelector('meta[name="quran-page-storage-key"]')?.content || 'currentPage';
  const linesDataPath = document.querySelector('meta[name="quran-lines-file"]')?.content;
  const requiredFont = document.querySelector('meta[name="quran-required-font"]')?.content;
  const readerView = document.getElementById('reader-view');
  const verseEndSelect = document.getElementById('verse-end-select');
  const isSelectedRange = () => readerView?.value === 'verses';

  // Preserve the same button nodes and listeners when a new page is rendered.
  const pageHeading = document.getElementById('reader-page-heading');
  const pageSuraTitle = document.getElementById('page-sura-title');

  // Global Variables
  let suraData, combinedData, wordsData, morphology, enWords, paginationData;
  let printedLayout;

  let showTranslation =
    localStorage.getItem("translate") === "en" ? true : false;
  let currentPage = parseInt(localStorage.getItem(pageStorageKey)) || 1;
  let currentSura = parseInt(localStorage.getItem("selectedSura")) || 1;
  let currentVerse = parseInt(localStorage.getItem("selectedVerse")) || 1;

  // Fetch all JSON data
  Promise.all([
    QuranUtils.loadJSON("json/sura.json"),
    QuranUtils.loadJSON(combinedDataPath),
    QuranUtils.loadJSON(wordsDataPath),
    QuranUtils.loadJSON("json/quran_morphology.json"),
    QuranUtils.loadJSON("json/en-word.json"),
    isChapterView ? Promise.resolve([]) : QuranUtils.loadJSON(paginationDataPath),
    linesDataPath ? QuranUtils.loadJSON(linesDataPath) : Promise.resolve(null),
    requiredFont ? document.fonts.load(`32px "${requiredFont}"`).then(faces => {
      if (!faces.length) throw new Error('The reading font could not be loaded. Please check your connection and try again.');
    }) : Promise.resolve()
  ])
    .then(async (data) => {
      [suraData, combinedData, wordsData, morphology, enWords, paginationData, printedLayout] =
        data;
      await migrateLegacyPage();
      populateSuraSelector();
      loadSelections();
      updatePageButtons();
      window.dispatchEvent(new Event("quran:ready"));
    })
    .catch((error) => {
      console.error("Error loading JSON files:", error);
      window.dispatchEvent(new Event("quran:error"));
      window.SiteUI.reportError(error);
    });

  // Populate Sura Selector
  function populateSuraSelector() {
    const suraSelect = document.getElementById("sura-select");
    suraSelect.innerHTML = "";
    for (let suraNumber in suraData) {
      const option = document.createElement("option");
      option.value = suraNumber;
      option.textContent = `${suraNumber}. ${suraData[suraNumber].name}`;
      suraSelect.appendChild(option);
    }
    suraSelect.value = currentSura;
  }

  // Populate Verse Selector
  function populateVerseSelector() {
    const suraNumber = document.getElementById("sura-select").value;
    const verseSelect = document.getElementById("verse-select");
    const sura = suraData[suraNumber];
    verseSelect.innerHTML = "";

    for (let verseNumber = 1; verseNumber <= sura.nAyah; verseNumber++) {
      const option = document.createElement("option");
      option.value = verseNumber;
      option.textContent = verseNumber;
      verseSelect.appendChild(option);
    }
    if (currentVerse > sura.nAyah) {
      currentVerse = 1;
    }

    verseSelect.value = currentVerse;
    if (verseEndSelect) {
      const end = Math.min(sura.nAyah, Math.max(currentVerse, Number(verseEndSelect.value) || currentVerse));
      verseEndSelect.replaceChildren();
      for (let verse = 1; verse <= sura.nAyah; verse++) {
        const option = document.createElement('option');
        option.value = verse;
        option.textContent = verse;
        verseEndSelect.appendChild(option);
      }
      verseEndSelect.value = end;
      verseEndSelect.disabled = !isSelectedRange();
    }
  }

  // Parse sura:verse reference
  function parseRef(ref) {
    const [sura, verse] = ref.split(":").map(Number);
    return { sura, verse };
  }

  // Find page containing a specific sura:verse
  function findPageByVerse(sura, verse) {
    for (const page of paginationData) {
      const fromRef = parseRef(page.from);
      const toRef = parseRef(page.to);

      // Check if verse is within page range
      if (
        sura > fromRef.sura ||
        (sura === fromRef.sura && verse >= fromRef.verse)
      ) {
        if (sura < toRef.sura || (sura === toRef.sura && verse <= toRef.verse)) {
          return page.page;
        }
      }
    }
    return 1; // Default to first page
  }

  async function migrateLegacyPage() {
    if (isChapterView || pageStorageKey !== 'currentPageMadinah'
      || localStorage.getItem(pageStorageKey)) return;
    const legacyNumber = Number(localStorage.getItem('currentPage'));
    if (!Number.isInteger(legacyNumber) || legacyNumber < 1) return;
    try {
      const legacyPages = await QuranUtils.loadJSON('json/pagination_map.json');
      const legacyPage = legacyPages.find(page => page.page === legacyNumber);
      if (!legacyPage) return;
      const position = ref => ref.sura * 1000 + ref.verse;
      const from = parseRef(legacyPage.from), to = parseRef(legacyPage.to);
      const selected = {sura:Number(localStorage.getItem('selectedSura')), verse:Number(localStorage.getItem('selectedVerse'))};
      const valid = suraData[selected.sura] && selected.verse >= 1
        && selected.verse <= suraData[selected.sura].nAyah;
      const target = valid && position(selected) >= position(from) && position(selected) <= position(to)
        ? selected : from;
      currentPage = findPageByVerse(target.sura, target.verse);
      localStorage.setItem(pageStorageKey, currentPage);
      localStorage.setItem('selectedSura', target.sura);
      localStorage.setItem('selectedVerse', target.verse);
    } catch (error) {
      console.warn('Could not migrate the old page bookmark:', error);
    }
  }

  // Get page data by page number
  function getPageData(pageNumber) {
    return paginationData.find((page) => page.page === pageNumber);
  }

  // Display Page (updated with Sura names)
  function displayPage(pageNumber, highlightSura = null, highlightVerse = null) {
    const pageData = getPageData(pageNumber);
    if (!pageData) {
      console.error("Page not found:", pageNumber);
      return;
    }

    displayRange(parseRef(pageData.from), parseRef(pageData.to),
      printedLayout ? null : highlightSura, printedLayout ? null : highlightVerse);
    if (printedLayout) {
      const arabic = document.querySelector('#quran-container .arabic-text-container');
      const highlightRef = highlightSura && highlightVerse ? `${highlightSura}:${highlightVerse}` : null;
      arabic.replaceChildren();
      if (pageHeading) arabic.appendChild(pageHeading);
      arabic.appendChild(ReaderLayout.renderPage(document, printedLayout, pageNumber, suraData,
        (sura, verse) => navigateToExternalVerse(verse, sura), highlightRef, enWords));
      ReaderLayout.fitLines(arabic);
      if (highlightRef) arabic.querySelector('.highlighted')?.scrollIntoView({behavior: 'smooth', block: 'center'});
    }
    const pageLabel = document.getElementById("page-number");
    if (pageLabel) pageLabel.textContent = readerView ? `Page ${pageNumber} of ${paginationData.length}` : `Page ${pageNumber}`;
    currentPage = pageNumber;
    localStorage.setItem(pageStorageKey, currentPage);
    updatePageButtons();
  }

  function displayChapter(suraNumber, verseNumber) {
    displayRange({sura:suraNumber, verse:1}, {sura:suraNumber, verse:suraData[suraNumber].nAyah}, suraNumber, verseNumber);
  }

  // Both views share word rendering, verse links, translations, font and popup behavior.
  function displayRange(fromRef, toRef, highlightSura = null, highlightVerse = null) {
    const container = document.getElementById("quran-container");
    container.className = "page";
    container.replaceChildren();

    const currentTranslate = localStorage.getItem("translate") || "notrans";

    // Create main Arabic text container
    const arabicContainer = document.createElement("div");
    arabicContainer.className = "arabic-text-container";

    // Create translations container
    const translationsContainer = document.createElement("div");
    translationsContainer.className = "translations-container";

    // Variables to track verse positions
    let verseToScroll = null;
    let currentSura = fromRef.sura;
    let currentVerse = fromRef.verse;
    let lastSura = null; // Track the last sura we displayed

    // Create document fragment for Arabic text
    const arabicFragment = document.createDocumentFragment();
    // Create document fragment for translations
    const translationsFragment = document.createDocumentFragment();

    while (true) {
      // Get global verse ID
      const suraMeta = suraData[currentSura];
      const globalVerseId = suraMeta.start + currentVerse - 1;

      if (!combinedData[globalVerseId]) {
        console.error("Verse not found:", currentSura, currentVerse);
        break;
      }

      // Add Sura name if this is a new Sura
      if (lastSura !== currentSura) {
        // Add sura name in bold
        const suraNameElem = document.createElement("span");
        suraNameElem.className = "sura-name";
        const strong = document.createElement("strong");
        strong.textContent = `${suraMeta.name} (${currentSura})`;
        suraNameElem.appendChild(strong);
        if (lastSura === null && pageHeading) {
          pageSuraTitle.textContent = strong.textContent;
          arabicFragment.appendChild(pageHeading);
        } else {
          arabicFragment.appendChild(suraNameElem);
        }

        lastSura = currentSura;
      }

      const verseData = combinedData[globalVerseId];
      const constructedArabic = buildVerseFromWords(
        verseData.start_word,
        verseData.end_word
      );

      const formattedSuraNumber = String(currentSura).padStart(3, "0");
      const formattedVerseNumber = String(currentVerse).padStart(3, "0");
      const combinedId = `${formattedSuraNumber}${formattedVerseNumber}`;

      // Create verse number element
      const verseNumberElem = document.createElement("span");
      verseNumberElem.className = "verse-number-inline";

      const verseLink = document.createElement("a");
      verseLink.href = navigateToExternalVerse(currentVerse, currentSura);
      verseLink.target = "_blank";
      verseLink.rel = "noopener noreferrer";
      verseLink.className = "verse-link";
      verseLink.textContent = isChapterView
        ? `۝${String(currentVerse).replace(/\d/g, digit => '٠١٢٣٤٥٦٧٨٩'[digit])}`
        : `﴿${currentVerse}﴾`;
      verseNumberElem.appendChild(verseLink);

      // Create Arabic text container for this verse
      const verseArabicContainer = document.createElement("span");
      verseArabicContainer.className = "verse-arabic";
      verseArabicContainer.id = `verse-${combinedId}`;

      // Check if this verse should be highlighted
      if (
        highlightSura &&
        highlightVerse &&
        currentSura === highlightSura &&
        currentVerse === highlightVerse
      ) {
        verseArabicContainer.classList.add("highlighted");
        verseToScroll = verseArabicContainer;
      }

      // Create Arabic text element
      const verseText = document.createElement("span");
      verseText.className = "arabic verse-text";
      verseText.innerHTML = constructedArabic;

      // Append Arabic text and verse number to Arabic container
      verseArabicContainer.appendChild(verseText);
      verseArabicContainer.appendChild(document.createTextNode(" "));
      verseArabicContainer.appendChild(verseNumberElem);
      verseArabicContainer.appendChild(document.createTextNode(" "));

      // Create translation element
      const verseTransText = document.createElement("div");
      verseTransText.id = `trans-${combinedId}`;
      verseTransText.className = "translation";

      // Create translation header with verse reference
      const transHeader = document.createElement("div");
      transHeader.className = "translation-header";
      transHeader.textContent = `(${currentSura}:${currentVerse})`;

      const transContent = document.createElement("div");
      transContent.className = "translation-content";
      transContent.textContent = verseData.en || "";

      verseTransText.appendChild(transHeader);
      verseTransText.appendChild(transContent);

      // Show/hide translation based on toggle
      if (currentTranslate === "en") {
        verseTransText.style.display = "block";
      } else {
        verseTransText.style.display = "none";
      }

      // Append to fragments
      arabicFragment.appendChild(verseArabicContainer);
      translationsFragment.appendChild(verseTransText);

      // Break if we reached the end of the page
      if (currentSura === toRef.sura && currentVerse === toRef.verse) {
        break;
      }

      // Move to next verse
      currentVerse++;
      if (currentVerse > suraMeta.nAyah) {
        currentSura++;
        currentVerse = 1;
      }
    }

    // Append fragments to containers
    arabicContainer.appendChild(arabicFragment);
    translationsContainer.appendChild(translationsFragment);

    // Append containers to main container
    container.appendChild(arabicContainer);
    container.appendChild(translationsContainer);

    loadDefaultFont();

    if (verseToScroll) {
      verseToScroll.scrollIntoView({ behavior: "smooth", block: "center" });
    }

  }

  // Navigate to External Verse
  function navigateToExternalVerse(verseNumber, sura) {
    const fullURL = `${EXTERNAL_VERSE_BASE_URL}sura/${sura}/verse/${verseNumber}/manuscripts`;
    return fullURL;
  }

  // Play Audio
  function playAudio(audioSrc) { return QuranUtils.playAudio(audioSrc); }

  // Go To Selected Verse (and display its page)
  function goToSelectedVerse() {
    const suraNumber = parseInt(document.getElementById("sura-select").value);
    const verseNumber = parseInt(document.getElementById("verse-select").value);

    // Update current sura/verse
    currentSura = suraNumber;
    currentVerse = verseNumber;
    localStorage.setItem("selectedSura", currentSura);
    localStorage.setItem("selectedVerse", currentVerse);

    if (isSelectedRange()) {
      const end = Math.max(verseNumber, Math.min(suraData[suraNumber].nAyah, Number(verseEndSelect.value) || verseNumber));
      verseEndSelect.value = end;
      // Keep the normal page bookmark aligned with the range's first verse.
      currentPage = findPageByVerse(suraNumber, verseNumber);
      localStorage.setItem(pageStorageKey, currentPage);
      displayRange({sura:suraNumber, verse:verseNumber}, {sura:suraNumber, verse:end});
      const label = document.getElementById('page-number');
      if (label) label.textContent = `Verses ${suraNumber}:${verseNumber}–${end}`;
      updatePageButtons();
      return;
    }
    if (isChapterView) {
      displayChapter(suraNumber, verseNumber);
      return;
    }
    // Find and display the page containing this verse
    const pageNumber = findPageByVerse(suraNumber, verseNumber);
    displayPage(pageNumber, suraNumber, verseNumber);
  }

  // Build Verse From Words
  function buildVerseFromWords(startIndex, endIndex) {
    const fragment = document.createDocumentFragment();

    for (let i = startIndex; i <= endIndex; i++) {
      const wordData = wordsData[i];
      const enWordData = enWords[i];

      const span = document.createElement("span");
      span.className = "word";
      span.textContent = wordData;
      span.dataset.wordId = i;
      span.dataset.en = enWordData;

      fragment.appendChild(span);
      fragment.appendChild(document.createTextNode(" "));
    }

    const div = document.createElement("span");
    div.appendChild(fragment);
    return div.innerHTML;
  }

  // Save Selections to Local Storage
  function saveSelections() {
    try {
      const suraSelect = document.getElementById("sura-select");
      const verseSelect = document.getElementById("verse-select");
      localStorage.setItem("selectedSura", suraSelect.value);
      localStorage.setItem("selectedVerse", verseSelect.value);
    } catch (error) {
      console.error("Error saving selections to localStorage:", error);
    }
  }

  function loadSelections() {
    try {
      const savedSura = localStorage.getItem("selectedSura");
      const savedVerse = localStorage.getItem("selectedVerse");
      const savedPage = localStorage.getItem(pageStorageKey);

      if (isChapterView) {
        currentSura = suraData[savedSura] ? Number(savedSura) : 1;
        currentVerse = Number(savedVerse) || 1;
        // The former chapter reader stored global verse IDs; accept unambiguous values.
        const sura = suraData[currentSura];
        if (currentVerse > sura.nAyah && currentVerse >= sura.start && currentVerse <= sura.end) {
          currentVerse -= sura.start - 1;
        }
        if (currentVerse < 1 || currentVerse > sura.nAyah) currentVerse = 1;
        document.getElementById("sura-select").value = currentSura;
        populateVerseSelector();
        displayChapter(currentSura, currentVerse);
        return;
      }
      if (savedSura && savedVerse) {
        currentSura = parseInt(savedSura);
        currentVerse = parseInt(savedVerse);

        currentPage = savedPage
          ? parseInt(savedPage)
          : findPageByVerse(currentSura, currentVerse);

        const suraSelect = document.getElementById("sura-select");
        const verseSelect = document.getElementById("verse-select");

        suraSelect.value = currentSura;

        populateVerseSelector();
        verseSelect.value = currentVerse;

        displayPage(currentPage, currentSura, currentVerse);
      } else {
        populateVerseSelector();
        const savedPageNumber = Number(savedPage);
        displayPage(getPageData(savedPageNumber) ? savedPageNumber : 1);
      }
    } catch (error) {
      console.error("Error loading selections:", error);
      if (isChapterView) displayChapter(1, 1);
      else displayPage(1);
    }
  }

  // Update Page Navigation Buttons
  function updatePageButtons() {
    const prevButton = document.getElementById("prev-page");
    const nextButton = document.getElementById("next-page");

    if (prevButton) {
      prevButton.disabled = isSelectedRange() || currentPage <= 1;
    }

    if (nextButton) {
      nextButton.disabled = isSelectedRange() || currentPage >= paginationData.length;
    }
  }

  // Show Morphology Popup
  function showWordMorphologyPopup(wordId, wordElement) {
  return QuranUtils.showWordMorphologyPopup(wordId, wordElement, morphology);
}









  // Event Delegation for Play Buttons and Words
  document
    .getElementById("quran-container")
    .addEventListener("click", (event) => {
      if (event.target.matches(".play-button")) {
        const audioSrc = event.target.getAttribute("data-audio-src");
        playAudio(audioSrc);
      } else if (event.target.matches(".word")) {
        const wordId = event.target.dataset.wordId;
        showWordMorphologyPopup(wordId, event.target);
      }
    });

  // Initialize Event Listeners
  document.getElementById("sura-select").addEventListener("change", () => {
    if (isChapterView || readerView) currentVerse = 1;
    populateVerseSelector();
    goToSelectedVerse();
  });

  document.getElementById("verse-select").addEventListener("change", () => {
    goToSelectedVerse();
  });

  readerView?.addEventListener('change', () => {
    verseEndSelect.disabled = !isSelectedRange();
    goToSelectedVerse();
  });
  verseEndSelect?.addEventListener('change', () => {
    const start = document.getElementById('verse-select');
    if (Number(verseEndSelect.value) < Number(start.value)) start.value = verseEndSelect.value;
    goToSelectedVerse();
  });

  // Page Navigation Event Listeners
  document.getElementById("prev-page")?.addEventListener("click", () => {
    if (!isSelectedRange() && currentPage > 1) {
      displayPage(currentPage - 1);
    }
  });

  document.getElementById("next-page")?.addEventListener("click", () => {
    if (!isSelectedRange() && currentPage < paginationData.length) {
      displayPage(currentPage + 1);
    }
  });

  // Predefined default fonts for each page
  const pageDefaultFonts = {
    "home": "Amiri Quran",
    "index.html": "Amiri Quran",
    "simple.html": "Qahiri",
    "page.html": "Amiri Quran",
    "warsh.html": "Amiri Quran",
    "quran.html": "Amiri Quran",
    "writing.html": "Qahiri"
  };

  function updateFontClass(selectedFont) {
    const arabicElements = document.querySelectorAll(".arabic");

    arabicElements.forEach((element) => {
      // Reset font classes
      element.classList.remove(
        "font-raqq",
        "font-qahiri",
        "font-amiri",
        "is-italic"
      );

      if (selectedFont === "Raqq") {
        element.classList.add("font-raqq");
      } else if (selectedFont === "Qahiri") {
        element.classList.add("font-qahiri", "is-italic");
      } else if (selectedFont === "Amiri Quran") {
        element.classList.add("font-amiri");
      }
    });
  }

  // Function to load the default font for the page
  function loadDefaultFont() {
    const page = window.location.pathname.split("/").pop() || "home";
    const savedFont = localStorage.getItem(`selectedFont_${page}`)
      || (isChapterView ? localStorage.getItem(`selectedFont_${window.location.pathname}`) : null);
    const fontSelectElement = document.getElementById("font-select");
    const validSavedFont = savedFont && (!fontSelectElement?.options
      || Array.from(fontSelectElement.options).some(option => option.value === savedFont));
    let fontToApply;

    if (validSavedFont) {
      fontToApply = savedFont;
    } else {
      // If no font is saved, set the predefined default for the page
      fontToApply = document.querySelector('meta[name="quran-default-font"]')?.content || pageDefaultFonts[page] || "Amiri Quran";
      localStorage.setItem(`selectedFont_${page}`, fontToApply);
    }

    console.log(fontToApply);
    updateFontClass(fontToApply);

    // Set the dropdown to reflect the applied font
    if (fontSelectElement) {
      fontSelectElement.value = fontToApply;
    }
  }

  // Font Selection Event Listener
  document.getElementById("font-select").addEventListener("change", (event) => {
    const selectedFont = event.target.value;
    updateFontClass(selectedFont);
    const page = window.location.pathname.split("/").pop() || "home";
    localStorage.setItem(`selectedFont_${page}`, selectedFont);
  });

  document.addEventListener("DOMContentLoaded", () => {

    const translationToggleBtn = document.getElementById("translation-toggle");

    const currentTranslate = localStorage.getItem("translate") || "notrans";

    // Apply the saved translation status on page load
    if (currentTranslate === "en") {
      showTranslation = true;
      translationToggleBtn.checked = true;
    } else {
      showTranslation = false;
      translationToggleBtn.checked = false;
    }

    // Toggle the translation visibility without page reload
    translationToggleBtn.addEventListener("change", () => {
      showTranslation = translationToggleBtn.checked;

      // Save the current translation setting in localStorage
      localStorage.setItem("translate", showTranslation ? "en" : "notrans");

      // Toggle translation display in the DOM
      const translationElements = document.querySelectorAll(".translation");
      translationElements.forEach((element) => {
        element.style.display = showTranslation ? "block" : "none";
      });
    });
  });
  if (linesDataPath && typeof window.addEventListener === 'function') {
    ReaderLayout.watchSize(document.getElementById('quran-container'), window,
      typeof ResizeObserver !== 'undefined' ? ResizeObserver : null);
  }
})();
