(() => {
  // Constants
  const AUDIO_BASE_URL = "https://audios.quranwbw.com/words/";
  const EXTERNAL_VERSE_BASE_URL =
    "https://corpuscoranicum.de/en/verse-navigator/";

  // Global Variables
  let suraData, combinedData, wordsData, morphology;
  let currentAudio = null;
  let showTranslation =
    localStorage.getItem("translate") === "en" ? true : false; // Load translation setting from local storage

  // Fetch all JSON data
  Promise.all([
    fetch("json/sura.json").then((response) => response.json()),
    fetch("json/combined_quran.json").then((response) => response.json()),
    fetch("json/quran_words.json").then((response) => response.json()),
    fetch("json/quran_morphology.json").then((response) => response.json()),
  ])
    .then((data) => {
      [suraData, combinedData, wordsData, morphology] = data;
      populateSuraSelector();
      loadSelections();
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
    populateVerseSelector(); // Populate verses for the first sura initially
  }

  // Populate Verse Selector
  function populateVerseSelector() {
    const suraNumber = document.getElementById("sura-select").value;
    const verseSelect = document.getElementById("verse-select");
    const sura = suraData[suraNumber];
    verseSelect.innerHTML = "";

    for (let verseNumber = sura.start; verseNumber <= sura.end; verseNumber++) {
      const option = document.createElement("option");
      const localVerseNumber = verseNumber - sura.start + 1;
      option.value = verseNumber;
      option.textContent = localVerseNumber;
      verseSelect.appendChild(option);
    }
  }

  // Display Sura
  function displaySura(suraNumber, targetVerse = null) {
    const sura = suraData[suraNumber];
    const container = document.getElementById("quran-container");
    container.innerHTML = `<h3 class="arabic">${suraNumber}. ${sura.name}</h3>`;

    const fragment = document.createDocumentFragment();
    let verseToScroll = null;

    for (let verseNumber = sura.start; verseNumber <= sura.end; verseNumber++) {
      const verseData = combinedData[verseNumber];
      const constructedArabic = buildVerseFromWords(
        verseData.start_word,
        verseData.end_word
      );

      const localVerseNumber = verseNumber - sura.start + 1;
      const formattedSuraNumber = String(suraNumber).padStart(3, "0");
      const formattedVerseNumber = String(localVerseNumber).padStart(3, "0");
      const combinedId = `${formattedSuraNumber}${formattedVerseNumber}`;
      const audioSrc = `https://everyayah.com/data/Husary_64kbps/${combinedId}.mp3`;

      const verseDiv = document.createElement("div");
      verseDiv.className = "verse";

      const verseContainer = document.createElement("div");
      verseContainer.className = "verse-container";
      verseContainer.id = `verse-${combinedId}`;

      const verseHeader = document.createElement("div");
      verseHeader.className = "verse-header";

      const verseNumberElem = document.createElement("h5");
      verseNumberElem.className = "verse-number";

      const verseLink = document.createElement("a");
      verseLink.href = "#";
      verseLink.target = "_blank";
      verseLink.className = "verse-link";
      verseLink.textContent = localVerseNumber;
      verseLink.addEventListener("click", (e) => {
        e.preventDefault();
        navigateToExternalVerse(localVerseNumber, suraNumber);
      });

      verseNumberElem.appendChild(verseLink);

      const playButton = document.createElement("button");
      playButton.className = "play-button";
      playButton.setAttribute("data-audio-src", audioSrc);
      playButton.setAttribute("aria-label", `Play Verse ${localVerseNumber}`);
      // Play button handled via event delegation

      verseHeader.appendChild(verseNumberElem);
      verseHeader.appendChild(playButton);
      verseContainer.appendChild(verseHeader);

      const verseTransText = document.createElement("div");
      verseTransText.id = combinedId;
      verseTransText.className = "translation";
      verseTransText.style.display = "none";
      verseTransText.innerHTML = verseData.en; // English translation

      const verseText = document.createElement("div");
      verseText.id = combinedId;
      verseText.className = "arabic verse-text";
      verseText.innerHTML = constructedArabic; // Ensure sanitization

      verseContainer.appendChild(verseText);
      verseDiv.appendChild(verseContainer);
      verseDiv.appendChild(verseTransText);
      fragment.appendChild(verseDiv);

      if (targetVerse && parseInt(targetVerse) === verseNumber) {
        verseToScroll = verseDiv;
      }
    }

    container.appendChild(fragment);
    loadDefaultFont();
 
    if (verseToScroll) {
      verseToScroll.scrollIntoView({ behavior: "smooth" });
    }
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

  // Go To Selected Verse
  function goToSelectedVerse() {
    const suraNumber = document.getElementById("sura-select").value;
    const verseNumber = document.getElementById("verse-select").value;
    displaySura(suraNumber, verseNumber);
  }

  // Build Verse From Words
  function buildVerseFromWords(startIndex, endIndex) {
    const fragment = document.createDocumentFragment();

    for (let i = startIndex; i <= endIndex; i++) {
      const wordData = wordsData[i];

      const span = document.createElement("span");
      span.className = "word";
      span.textContent = wordData; // Prevent XSS
      span.dataset.wordId = i;

      fragment.appendChild(span);
      fragment.appendChild(document.createTextNode(" "));
    }

    const div = document.createElement("div");
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

  // Load Selections from Local Storage
  function loadSelections() {
    try {
      console.log("loading verse");
      const savedSura = localStorage.getItem("selectedSura");
      const savedVerse = localStorage.getItem("selectedVerse");

      const suraSelect = document.getElementById("sura-select");
      const verseSelect = document.getElementById("verse-select");

      if (savedSura && suraData[savedSura]) {
        suraSelect.value = savedSura;
        populateVerseSelector();

        if (savedVerse && combinedData[savedVerse]) {
          verseSelect.value = savedVerse;
        } else {
          verseSelect.selectedIndex = 0;
        }
      } else {
        suraSelect.selectedIndex = 0;
        populateVerseSelector();
        verseSelect.selectedIndex = 0;
      }
     
      goToSelectedVerse();
    } catch (error) {
      console.error("Error loading selections from localStorage:", error);
    }
  }

  // Show Morphology Popup
  function showWordMorphologyPopup(wordId, wordElement) {
    const wordData = wordsData[wordId];
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
        ${wordData}
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

  // Initialize Event Listeners for Selectors
  document.getElementById("sura-select").addEventListener("change", () => {
    saveSelections();
    populateVerseSelector();
    goToSelectedVerse();
  });

  document.getElementById("verse-select").addEventListener("change", () => {
    saveSelections();
    goToSelectedVerse();
  });


 // Predefined default fonts for each page
const pageDefaultFonts = {
  "/originalquran/": "Qahiri",
  "originalquran/index.html": "Qahiri",
  "originalquran/root.html": "Amiri Quran",
  "originalquran/quran.html": "Raqq" // Add more pages and their default fonts here
};

// Function to update the font by applying the correct class
function updateFontClass(selectedFont) {
  const arabicElements = document.querySelectorAll(".arabic");

  // Remove any previously applied font classes
  arabicElements.forEach((element) => {
    element.classList.remove("font-raqq", "font-qahiri", "font-amiri");

    // Apply the correct font class based on the selection
    if (selectedFont === "Raqq") {
      element.classList.add("font-raqq");
    } else if (selectedFont === "Qahiri") {
      element.classList.add("font-qahiri");
    } else if (selectedFont === "Amiri Quran") {
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
  console.log("saving font"+selectedFont);
  vpage = window.location.pathname;
  localStorage.setItem(`selectedFont_${vpage}`, selectedFont); // Save the selected font to local storage
});


// Load the default font when the page is loaded
//window.addEventListener("load", loadDefaultFont);


// Initialize Font on Page Load
document.addEventListener("DOMContentLoaded", () => {
  vpage = window.location.pathname;
  const savedFont = localStorage.getItem(`selectedFont_${vpage}`) || pageDefaultFonts[window.location.pathname];
  updateFontClass(savedFont);
});





document.addEventListener("DOMContentLoaded", () => {
  const themeToggleBtn = document.getElementById("theme-toggle");
  const translationToggleBtn = document.getElementById("translation-toggle"); // Make sure this element exists

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
    translationToggleBtn.checked = true; // Set the toggle button to checked if translation is enabled
  } else {
    showTranslation = false;
    translationToggleBtn.checked = false; // Set it to unchecked if no translation is set
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
    showTranslation = translationToggleBtn.checked; // Update based on checkbox status

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




