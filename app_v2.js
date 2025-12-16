(() => {
  // Constants
  const AUDIO_BASE_URL = "https://audios.quranwbw.com/words/";
  const EXTERNAL_VERSE_BASE_URL =
    "https://corpuscoranicum.de/en/verse-navigator/";

  // Global Variables
  let suraData, combinedData, wordsData, morphology, enWords, paginationData;
  let currentAudio = null;
  let showTranslation =
    localStorage.getItem("translate") === "en" ? true : false;
  let currentPage = parseInt(localStorage.getItem("currentPage")) || 1;
  let currentSura = parseInt(localStorage.getItem("selectedSura")) || 1;
  let currentVerse = parseInt(localStorage.getItem("selectedVerse")) || 1;
  let isPageView = true; // We'll use page view by default

  // Fetch all JSON data
  Promise.all([
    fetch("json/sura.json").then((response) => response.json()),
    fetch("json/combined_quran.json").then((response) => response.json()),
    fetch("json/quran_harakat_words.json").then((response) => response.json()),
    fetch("json/quran_morphology.json").then((response) => response.json()),
    fetch("json/en-word.json").then((response) => response.json()),
    fetch("json/pagination_map.json").then((response) => response.json())
  ])
    .then((data) => {
      [suraData, combinedData, wordsData, morphology, enWords, paginationData] = data;
      populateSuraSelector();
      loadSelections();
      updatePageButtons();
    })
    .catch((error) => {
      console.error("Error loading JSON files:", error);
      alert("Failed to load data. Please try refreshing the page.");
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
      if (sura > fromRef.sura || (sura === fromRef.sura && verse >= fromRef.verse)) {
        if (sura < toRef.sura || (sura === toRef.sura && verse <= toRef.verse)) {
          return page.page;
        }
      }
    }
    return 1; // Default to first page
  }

  // Get page data by page number
  function getPageData(pageNumber) {
    return paginationData.find(page => page.page === pageNumber);
  }


  // Display Page (updated with Sura names)
function displayPage(pageNumber, highlightSura = null, highlightVerse = null) {
  const pageData = getPageData(pageNumber);
  if (!pageData) {
    console.error("Page not found:", pageNumber);
    return;
  }

  const fromRef = parseRef(pageData.from);
  const toRef = parseRef(pageData.to);
  
  const container = document.getElementById("quran-container");
  container.className = "page";
  container.innerHTML = `<div class="page-header">Page ${pageNumber} (${pageData.word_count} words)</div>`;
  
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
      // Add sura name separator
 
      
      // Add sura name in bold
      const suraNameElem = document.createElement("span");
      suraNameElem.className = "sura-name";
      suraNameElem.innerHTML = `<strong>${suraMeta.name} (${currentSura})</strong>`;
      arabicFragment.appendChild(suraNameElem);
      
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
    verseLink.href = "#";
    verseLink.target = "_blank";
    verseLink.className = "verse-link";
    verseLink.textContent = `﴿${currentVerse}﴾`;
    verseLink.addEventListener("click", (e) => {
      e.preventDefault();
      navigateToExternalVerse(currentVerse, currentSura);
    });
    
    verseNumberElem.appendChild(verseLink);

    // Create Arabic text container for this verse
    const verseArabicContainer = document.createElement("span");
    verseArabicContainer.className = "verse-arabic";
    verseArabicContainer.id = `verse-${combinedId}`;
    
    // Check if this verse should be highlighted
    if (highlightSura && highlightVerse && 
        currentSura === highlightSura && currentVerse === highlightVerse) {
      verseArabicContainer.classList.add("highlighted");
      verseToScroll = verseArabicContainer;
    }
    
    // Create Arabic text element
    const verseText = document.createElement("span");
    verseText.className = "arabic verse-text";
    verseText.innerHTML = constructedArabic;
    
    // Append Arabic text and verse number to Arabic container
    verseArabicContainer.appendChild(verseText);
    verseArabicContainer.appendChild(document.createTextNode(" ")); // Space between text and number
    verseArabicContainer.appendChild(verseNumberElem);
    verseArabicContainer.appendChild(document.createTextNode(" ")); // Space after number
    
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
    transContent.innerHTML = verseData.en;
    
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
  
  // Update current page
  currentPage = pageNumber;
  localStorage.setItem("currentPage", currentPage);
  updatePageButtons();
}

  // Navigate to External Verse
  function navigateToExternalVerse(verseNumber, sura) {
    const fullURL = `${EXTERNAL_VERSE_BASE_URL}sura/${sura}/verse/${verseNumber}/manuscripts`;
    window.open(fullURL, "_blank");
  }

  // Play Audio
  function playAudio(audioSrc) {
    if (!audioSrc) {
      console.error("Invalid audio source.");
      return;
    }

    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
    }

    currentAudio = new Audio(audioSrc);

    currentAudio.addEventListener("play", () => {
      // Optional: Visual feedback
    });

    currentAudio.addEventListener("ended", () => {
      currentAudio = null;
      // Optional: Remove visual feedback
    });

    currentAudio.addEventListener("error", (e) => {
      console.error("Error playing audio:", e);
      alert("Failed to play audio.");
      currentAudio = null;
    });

    currentAudio.play().catch((error) => {
      console.error("Playback failed:", error);
      alert("Unable to play the selected audio.");
    });
  }

  // Go To Selected Verse (and display its page)
  function goToSelectedVerse() {
    const suraNumber = parseInt(document.getElementById("sura-select").value);
    const verseNumber = parseInt(document.getElementById("verse-select").value);
    
    // Update current sura/verse
    currentSura = suraNumber;
    currentVerse = verseNumber;
    localStorage.setItem("selectedSura", currentSura);
    localStorage.setItem("selectedVerse", currentVerse);
    
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
    const savedPage = localStorage.getItem("currentPage");

    if (savedSura && savedVerse) {
      currentSura = parseInt(savedSura);
      currentVerse = parseInt(savedVerse);

      currentPage = savedPage
        ? parseInt(savedPage)
        : findPageByVerse(currentSura, currentVerse);

      const suraSelect = document.getElementById("sura-select");
      const verseSelect = document.getElementById("verse-select");

      suraSelect.value = currentSura;

      populateVerseSelector();        // ✅ populate once
      verseSelect.value = currentVerse; // ✅ then set value

      displayPage(currentPage, currentSura, currentVerse);
    } else {
      displayPage(1);
    }
  } catch (error) {
    console.error("Error loading selections:", error);
    displayPage(1);
  }
}

  // Update Page Navigation Buttons
  function updatePageButtons() {
    const prevButton = document.getElementById("prev-page");
    const nextButton = document.getElementById("next-page");
    
    if (prevButton) {
      prevButton.disabled = currentPage <= 1;
    }
    
    if (nextButton) {
      nextButton.disabled = currentPage >= paginationData.length;
    }
  }

  // Show Morphology Popup
  function showWordMorphologyPopup(wordId, wordElement) {
    const wordData = wordElement.innerHTML;
    const enData = wordElement.getAttribute('data-en');
    const wordMorphology = morphology[wordId];

    if (!wordData || !wordMorphology) {
      console.error("No data found for wordId:", wordId);
      return;
    }

    removeExistingPopup();

    const wordObjects = wordMorphology.words;
    playAudio(generateAudioUrl(wordMorphology.id));

    const tableContent = buildMorphologyTable(wordObjects);

    const popupContent = `
      <span id="morphology-popup-title">
        ${wordData}, ${enData}
        <table>
          ${tableContent}
        </table>
      </span>
    `;

    const popup = document.createElement("div");
    popup.className = "morphology-popup";
    popup.setAttribute("role", "dialog");
    popup.setAttribute("aria-modal", "true");
    popup.setAttribute("aria-labelledby", "morphology-popup-title");
    popup.innerHTML = popupContent;

    document.body.appendChild(popup);

    // Add a click listener to remove the popup when clicking outside
    document.addEventListener("click", handleOutsideClick);

    const rect = wordElement.getBoundingClientRect();
    const popupRect = popup.getBoundingClientRect();

    let top = rect.bottom + window.scrollY;
    let left = rect.left + window.scrollX;

    // Adjust position if popup goes beyond viewport
    if (left + popupRect.width > window.innerWidth) {
      left = window.innerWidth - popupRect.width - 10;
    }

    if (top + popupRect.height > window.innerHeight + window.scrollY) {
      top = rect.top + window.scrollY - popupRect.height;
    }

    popup.style.top = `${top}px`;
    popup.style.left = `${left}px`;
    popup.setAttribute("tabindex", "-1");
    popup.focus();
    popup.dataset.triggerId = wordId;
  }

  // Build Morphology Table
function buildMorphologyTable(wordObjects) {
  let tableContent = "";

  for (let wordId in wordObjects) {
      const wordMorphology = wordObjects[wordId];

      tableContent += `
      <tr><th>Word</th><td>${wordMorphology.word || "N/A"}</td></tr>
      <tr><th>POS</th><td>${wordMorphology.pos || "N/A"}</td></tr>
      <tr><th>Root</th><td>${wordMorphology.root && wordMorphology.root !== "N/A" ? 
          `<span class="clickable-root" style="cursor:pointer; color:blue; text-decoration: underline;">${wordMorphology.root}</span>` : 
          "N/A"
      }</td></tr>
      <tr><th>Lemma</th><td>${wordMorphology.lemma || "N/A"}</td></tr>
      <tr><th>Morphology</th><td>${wordMorphology.morphology || "N/A"}</td></tr>
      <tr><td colspan="2"><hr></td></tr>
      `;
  }

  // After generating the table content, attach the event listeners for root clicks
  setTimeout(() => {
      const clickableRoots = document.querySelectorAll('.clickable-root');
      
      clickableRoots.forEach(rootElement => {
          rootElement.addEventListener('click', () => {
              const rootWord = rootElement.textContent;

              // Save the root word to localStorage
              localStorage.setItem('selectedRoot', rootWord);

              // Open the root.html page in a new tab
              window.open('root.html', '_blank');
          });
      });
  }, 0);  // Small delay to ensure the DOM elements are rendered before attaching the event listeners

  return tableContent;
}


  // Remove existing popups if any
  function removeExistingPopup() {
    const existingPopup = document.querySelector(".morphology-popup");
    if (existingPopup) {
      existingPopup.remove();
      document.removeEventListener("click", handleOutsideClick);
    }
  }

  // Handle clicking outside of the popup to close it
  function handleOutsideClick(event) {
    // Check if the clicked target is neither inside the popup nor a word element
    if (
      !event.target.closest(".morphology-popup") &&
      !event.target.closest(".word")
    ) {
      removeExistingPopup(); // Close the popup
    }
  }

  // Generate Audio URL
  function generateAudioUrl(key) {
    if (typeof key !== "string" || !key.includes(":")) {
      console.error("Invalid key format:", key);
      return null;
    }

    const parts = key.split(":");
    if (parts.length !== 3) {
      console.error("Invalid key parts:", key);
      return null;
    }

    const [surah, ayah, word] = parts.map(Number);
    if (isNaN(surah) || isNaN(ayah) || isNaN(word)) {
      console.error("Invalid numerical values in key:", key);
      return null;
    }

    const surahStr = String(surah).padStart(3, "0");
    const ayahStr = String(ayah).padStart(3, "0");
    const wordStr = String(word).padStart(3, "0");

    const url = `${AUDIO_BASE_URL}${surah}/${surahStr}_${ayahStr}_${wordStr}.mp3`;
    return url;
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
    populateVerseSelector();
    goToSelectedVerse();
  });

  document.getElementById("verse-select").addEventListener("change", () => {
    goToSelectedVerse();
  });

  // Page Navigation Event Listeners
  document.getElementById("prev-page").addEventListener("click", () => {
    if (currentPage > 1) {
      displayPage(currentPage - 1);
    }
  });

  document.getElementById("next-page").addEventListener("click", () => {
    if (currentPage < paginationData.length) {
      displayPage(currentPage + 1);
    }
  });


 // Predefined default fonts for each page
const pageDefaultFonts = {
  "/originalquran/": "Qahiri",
  "/originalquran/index.html": "Qahiri",
  "/originalquran/root.html": "Amiri Quran",
  "/originalquran/quran.html": "Raqq" // Add more pages and their default fonts here
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
    } 
    else if (selectedFont === "Qahiri") {
      element.classList.add("font-qahiri", "is-italic");
    } 
    else if (selectedFont === "Amiri Quran") {
      element.classList.add("font-amiri");
    }
  });
}

// Function to load the default font for the page
function loadDefaultFont() {
  const page = window.location.pathname; // Get the current page path
  const savedFont = localStorage.getItem(`selectedFont_${page}`);
  let fontToApply;

  if (savedFont) {
    fontToApply = savedFont;
  } else {
    // If no font is saved, set the predefined default for the page
    fontToApply = pageDefaultFonts[page] || "Amiri Quran"; // Fallback to Amiri if not defined
    localStorage.setItem(`selectedFont_${page}`, fontToApply); // Save the default font to localStorage
  }

  console.log(fontToApply);
  // Apply the font by setting the class
  updateFontClass(fontToApply);

  // Set the dropdown to reflect the applied font
  const fontSelectElement = document.getElementById("font-select");
  if (fontSelectElement) {
    fontSelectElement.value = fontToApply;
  }
}


// Font Selection Event Listener
document.getElementById("font-select").addEventListener("change", (event) => {
  const selectedFont = event.target.value;
  updateFontClass(selectedFont);
  vpage = window.location.pathname;
  localStorage.setItem(`selectedFont_${vpage}`, selectedFont); // Save the selected font to local storage
});



document.addEventListener("DOMContentLoaded", () => {
  const themeToggleBtn = document.getElementById("theme-toggle");
  const translationToggleBtn = document.getElementById("translation-toggle");

  const currentTheme = localStorage.getItem("theme") || "light";
  const currentTranslate = localStorage.getItem("translate") || "notrans";

  // Apply the saved theme on page load
  if (currentTheme === "dark") {
    document.body.classList.add("dark-theme");
    themeToggleBtn.checked = true;
  } else {
    themeToggleBtn.checked = false;
  }

  // Apply the saved translation status on page load
  if (currentTranslate === "en") {
    showTranslation = true;
    translationToggleBtn.checked = true;
  } else {
    showTranslation = false;
    translationToggleBtn.checked = false;
  }

  // Toggle the theme when the button is clicked
  themeToggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme");

    // Save the current theme in localStorage
    const newTheme = document.body.classList.contains("dark-theme")
      ? "dark"
      : "light";
    localStorage.setItem("theme", newTheme);
  });

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

})();