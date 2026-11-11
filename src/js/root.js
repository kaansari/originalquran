// Root selection, verse display and search. Shared interactions live in common.js.
// Global Variables

let suraData, combinedQuranData, quranWordsData, morphology, enData;
let rootWordsData = {}; // To store the root_words.json data
let paginationData = [];


let verseIdToSuraAyah = null;
let suraRanges = null;
let searchTimer = null;


let quranDataLoaded = false;
let rootsLoaded = false;

function tryInitSearch() {
  if (quranDataLoaded && rootsLoaded) initSearch();
}


Promise.all([
  QuranUtils.loadJSON("json/sura.json"),
  QuranUtils.loadJSON("json/combined_harakat_quran.json"),
  QuranUtils.loadJSON("json/quran_harakat_words.json"),
  QuranUtils.loadJSON("json/quran_morphology.json"),
  QuranUtils.loadJSON("json/en-word.json"),
  QuranUtils.loadJSON("json/pagination_map.json"),
])
  .then((data) => {
    [suraData, combinedQuranData, quranWordsData, morphology, enData, paginationData] = data;
    quranDataLoaded = true;
    tryInitSearch();
  })
  .catch((error) => {
    console.error("Error loading JSON files:", error);
    window.SiteUI.reportError(error);
  });


// Fetch the root_words.json data
QuranUtils.loadJSON('json/root_words.json')
  .then(data => {
    rootWordsData = data;
    rootsLoaded = true;
    bindSelectListenersOnce();
    populateLetterLabels();
    loadSavedSelections();
    tryInitSearch();
  })
  .catch(error => { console.error('Error loading root_words.json:', error); window.SiteUI.reportError(error); });

// Populate the clickable letters as labels
function populateLetterLabels() {
  const letterContainer = document.getElementById('letter-container');
  letterContainer.innerHTML = ''; // Clear any existing labels
  const uniqueLetters = new Set();

  // Extract the first letter of each root word and add it to the Set
  for (const root in rootWordsData) {
    uniqueLetters.add(root.charAt(0));
  }

  // Sort the letters and create clickable labels
  const sortedLetters = Array.from(uniqueLetters).sort();
  sortedLetters.forEach(letter => {
    const letterLabel = document.createElement('span');
    letterLabel.textContent = letter;
    letterLabel.classList.add('letter-label'); // Add some styling class
    letterLabel.style.cursor = 'pointer'; // Make it look clickable

    // Add click event to each label
    letterLabel.addEventListener('click', () => {
      populateRootSelectorByLetter(letter);
      saveSelections(); // Save the selected letter
    });

    // Append the label to the container
    letterContainer.appendChild(letterLabel);
  });

  // Automatically populate root selector for the first letter by default
  if (!localStorage.getItem("selectedRoot") && sortedLetters.length > 0) {
    populateRootSelectorByLetter(sortedLetters[0]);
  }

}


let listenersBound = false;

function bindSelectListenersOnce() {
  if (listenersBound) return;
  listenersBound = true;

  const rootSelectEl = document.getElementById("root-select");
  const wordSelectEl = document.getElementById("word-select");

  rootSelectEl.addEventListener("change", () => {
    populateWordSelector();   // must still happen
    saveSelections();
  });

  wordSelectEl.addEventListener("change", () => {
    saveSelections();
    displayVerseData();
  });
}


// Populate the root selector based on the selected letter
function populateRootSelectorByLetter(letter) {
  const rootSelect = document.getElementById('root-select');
  rootSelect.innerHTML = '';

  // Filter and sort the root words that start with the selected letter
  const filteredRoots = Object.keys(rootWordsData).filter(root => root.startsWith(letter)).sort();

  // Populate root selector with filtered roots
  filteredRoots.forEach(root => {
    const option = document.createElement('option');
    option.value = root;
    option.textContent = root;
    rootSelect.appendChild(option);
  });

  // Populate word selector for the first root word by default
  if (filteredRoots.length > 0) {
    rootSelect.value = filteredRoots[0]; // Default to the first root word
    populateWordSelector();
  }
}

// Populate the word selector based on the selected root word
function populateWordSelector() {
  const rootSelect = document.getElementById('root-select').value;
  window.RootDictionary.show(rootSelect);
  const wordSelect = document.getElementById('word-select');
  wordSelect.innerHTML = '';

  const wordList = rootWordsData[rootSelect].Word;

  // Sort the words in ascending order
  const sortedWords = Object.keys(wordList).sort();

  // Populate word selector with sorted child words
  sortedWords.forEach((word) => {
    const option = document.createElement('option');
    option.value = word;
    option.textContent = word;
    wordSelect.appendChild(option);
  });


  displayVerseData(); // Display verse data for the first word initially
}

function displayVerseData() {
  const wordSelect = document.getElementById('word-select').value;
  const rootSelect = document.getElementById('root-select').value;
  window.RootStatistics.show(rootWordsData[rootSelect], wordSelect);
  const verseData = rootWordsData[rootSelect].Word[wordSelect].Verses;

  const showTranslation = localStorage.getItem("translate") === "en";

  const verseContainer = document.getElementById('verse-data');

  verseContainer.innerHTML = `
   <h2 class="verse-results-heading">Quran Verse(s): ${verseData.length}</h2>
    <ul>
${verseData.map(verse => {
    const verseContent = buildVerse(verse, showTranslation);
    return `<li class="arabic">${verseContent}</li>`;
  }).join('')}
    </ul>
  `;

  // Apply translation visibility based on current state
  const translationElements = verseContainer.querySelectorAll(".translation");
  translationElements.forEach((element) => {
    element.style.display = showTranslation ? "block" : "none";
  });
}

// Call populateLetterLabels after the JSON data is loaded
function saveSelections() {
  const rootSelect = document.getElementById('root-select').value;
  const wordSelect = document.getElementById('word-select').value;
  localStorage.setItem('selectedRoot', rootSelect);
  localStorage.setItem('selectedWord', wordSelect);
}

function loadSavedSelections() {
  const savedRoot = localStorage.getItem('selectedRoot');
  const savedWord = localStorage.getItem('selectedWord');

  if (!savedRoot || !rootWordsData[savedRoot]) return;

  const firstLetter = savedRoot.charAt(0);

  // Step 1: populate roots for the correct letter
  populateRootSelectorByLetter(firstLetter);

  const rootSelect = document.getElementById('root-select');
  rootSelect.value = savedRoot;

  // Step 2: populate words
  populateWordSelector();

  const wordSelect = document.getElementById('word-select');
  if (savedWord && rootWordsData[savedRoot].Word[savedWord]) {
    wordSelect.value = savedWord;
  }

  displayVerseData();
}


// This function gets the sura data based on sura number
function getSuraData(suraNumber) {
  return suraData[suraNumber];
}

// This function gets the verse data based on index (calculated from sura start)
function getVerseData(verseIndex) {
  return combinedQuranData[verseIndex];
}

// This function gets words from quran_words.json between the start and end word positions
function getWordsFromRange(start, end) {
  const words = [];
  for (let i = start; i <= end; i++) {


    const wordData = quranWordsData[i.toString()];
    const enWordData = enData[i.toString()];
    const span = document.createElement("span");
    span.className = "word";
    span.dataset.wordId = i;
    span.dataset.en = enWordData;
    span.textContent = wordData; // Prevent XSS

    // wordEle = `<span>${quranWordsData[i.toString()]}</span>`
    words.push(span.outerHTML);  // Convert the word position to string since keys are strings
  }
  return words;
}

function buildVerse(verseObject, showTranslation = false) {
  const { Key, ID } = verseObject;

  // Extract sura number, verse number, and word position from ID
  const [suraNumber, verseNumber] = ID.split(":").map(Number);

  // Fetch sura data from json/sura.json
  const suraInfo = getSuraData(suraNumber);

  // Calculate the verse index from combined_quran.json
  const verseIndex = suraInfo.start + (verseNumber - 1);

  // Fetch the verse from combined_quran.json using verseIndex
  const verseData = getVerseData(verseIndex);

  // Build the verse using words from quran_words.json
  const words = getWordsFromRange(verseData.start_word, verseData.end_word);

  // Highlight the word with ID matching the Key
  const highlightedWords = words.map((word, index) => {
    const wordPosition = verseData.start_word + index;
    if (wordPosition === Number(Key)) {
      return `<span class="highlight">${word}</span>`;
    }
    return word;
  });

  // English translation - conditionally include based on showTranslation
  const translation = showTranslation ?
    `<div class="translation" style="display: block;">${QuranUtils.escapeHTML(verseData.en || "")}</div>` :
    `<div class="translation" style="display: none;">${QuranUtils.escapeHTML(verseData.en || "")}</div>`;

  const verseLink = `<span class="verseid" style="cursor:pointer; color:blue; text-decoration: underline;" verse=${verseIndex} sura=${suraNumber}>${suraNumber}:${verseNumber}</span>`

  // Return the verse as a string of words followed by sura:verse (e.g., "2:12")
  return `${highlightedWords.join(" ")} ${verseLink} ${translation}`;
}

function parseRef(ref) {
  const [sura, verse] = ref.split(":").map(Number);
  return { sura, verse };
}

function findPageByVerse(sura, verse) {
  for (const page of paginationData) {
    const fromRef = parseRef(page.from);
    const toRef = parseRef(page.to);

    if (
      sura > fromRef.sura || (sura === fromRef.sura && verse >= fromRef.verse)
    ) {
      if (
        sura < toRef.sura || (sura === toRef.sura && verse <= toRef.verse)
      ) {
        return page.page;
      }
    }
  }
  return 1;
}

// Show Morphology Popup
function showWordMorphologyPopup(wordId, wordElement) {
  return QuranUtils.showWordMorphologyPopup(wordId, wordElement, morphology);
}






// Play Audio
function playAudio(audioSrc) { return QuranUtils.playAudio(audioSrc); }

// Event Delegation for navigation.
const _verseDataEl = document.getElementById("verse-data");
if (_verseDataEl) {
  _verseDataEl.addEventListener("click", (event) => {
    if (event.target.matches(".word")) {
      const wordId = event.target.dataset.wordId;
      showWordMorphologyPopup(wordId, event.target);
    }
    if (event.target.matches(".verseid")) {
      try {
        const suraNumber = parseInt(event.target.getAttribute("sura"));

        // verseIndex is global index → convert to ayah number
        const verseIndex = parseInt(event.target.getAttribute("verse"));
        const suraInfo = suraData[suraNumber];
        const verseNumber = verseIndex - suraInfo.start + 1;

        const pageNumber = findPageByVerse(suraNumber, verseNumber);

        // Save everything the Hafs home page expects
        localStorage.setItem("selectedSura", suraNumber);
        localStorage.setItem("selectedVerse", verseNumber);
        localStorage.setItem("currentPage", pageNumber);

        QuranUtils.openInNewTab("index.html");
      } catch (error) {
        console.error("Navigation error:", error);
      }
    }

  });
}

document.addEventListener("DOMContentLoaded", () => {

  const translationToggleBtn = document.getElementById("translation-toggle");

  const currentTranslate = localStorage.getItem("translate") || "notrans";

  // Apply the saved translation status on page load
  if (translationToggleBtn) translationToggleBtn.checked = (currentTranslate === "en");

  // Toggle the translation visibility without page reload
  if (translationToggleBtn) {
    translationToggleBtn.addEventListener("change", () => {
      const showTranslation = translationToggleBtn.checked;

      // Save the current translation setting in localStorage
      localStorage.setItem("translate", showTranslation ? "en" : "notrans");

      // Toggle translation display in the DOM
      const translationElements = document.querySelectorAll(".translation");
      translationElements.forEach((element) => {
        element.style.display = showTranslation ? "block" : "none";
      });

      // Re-render the verse data with the new translation setting
      const wordSelectEl = document.getElementById('word-select');
      if (wordSelectEl && wordSelectEl.value) {
        displayVerseData();
      }
    });
  }

  // Load saved selections after the toggles are initialized
  loadSavedSelections();
});


const _searchVerseDataEl = document.getElementById("search-verse-data");
if (_searchVerseDataEl) {
  _searchVerseDataEl.addEventListener("click", (event) => {
    if (event.target.matches(".word")) {
      const wordId = event.target.dataset.wordId;
      showWordMorphologyPopup(wordId, event.target);
    }
    if (event.target.matches(".verseid")) {
      try {
        const suraNumber = parseInt(event.target.getAttribute("sura"));
        const verseIndex = parseInt(event.target.getAttribute("verse"));
        const suraInfo = suraData[suraNumber];
        const verseNumber = verseIndex - suraInfo.start + 1;

        const pageNumber = findPageByVerse(suraNumber, verseNumber);

        localStorage.setItem("selectedSura", suraNumber);
        localStorage.setItem("selectedVerse", verseNumber);
        localStorage.setItem("currentPage", pageNumber);

        QuranUtils.openInNewTab("index.html");
      } catch (error) {
        console.error("Navigation error:", error);
      }
    }
  });
}

function initSearch() {
  // Must have data loaded
  if (!suraData || !combinedQuranData || !rootWordsData) return;

  buildSuraRangesForSearch();
  buildVerseRefIndexForSearch();

  const modeEl = document.getElementById("search-mode");
  const inputEl = document.getElementById("search-input");
  const clearEl = document.getElementById("search-clear");

  if (!modeEl || !inputEl || !clearEl) return;

  inputEl.addEventListener("input", () => {
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(runSearch, 180);
  });

  modeEl.addEventListener("change", runSearch);

  clearEl.addEventListener("click", () => {
    inputEl.value = "";
    setSearchStatus("");
    const svd = document.getElementById("search-verse-data");
    if (svd) svd.innerHTML = "";
  });
}

function buildSuraRangesForSearch() {
  suraRanges = Object.keys(suraData).map(k => ({
    suraNum: parseInt(k, 10),
    start: suraData[k].start,
    end: suraData[k].end,
    nAyah: suraData[k].nAyah,
    name: suraData[k].name
  })).sort((a, b) => a.suraNum - b.suraNum);
}

function findSuraForVerseIndex(verseIndex) {
  // verseIndex is global verse id (1..6236)
  let lo = 0, hi = suraRanges.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const s = suraRanges[mid];
    if (verseIndex < s.start) hi = mid - 1;
    else if (verseIndex > s.end) lo = mid + 1;
    else return s;
  }
  return null;
}

function buildVerseRefIndexForSearch() {
  // verseIdToSuraAyah[globalVerseId] -> {sura, ayah, name}
  verseIdToSuraAyah = {};
  for (const vidStr of Object.keys(combinedQuranData)) {
    const vid = parseInt(vidStr, 10);
    const s = findSuraForVerseIndex(vid);
    if (!s) continue;
    const ayah = (vid - s.start) + 1;
    verseIdToSuraAyah[vidStr] = { sura: s.suraNum, ayah, name: s.name };
  }
}

function runSearch() {
  const mode = document.getElementById("search-mode").value;
  const q = (document.getElementById("search-input").value || "").trim();

  if (!q) {
    setSearchStatus("");
    document.getElementById("search-verse-data").innerHTML = "";
    return;
  }

  const t0 = performance.now();
  let verseObjects = [];

  if (mode === "ref") {
    verseObjects = searchRefToVerseObjects(q);
  } else if (mode === "root") {
    verseObjects = searchRootWordsRootToVerseObjects(q);
  } else if (mode === "word") {
    verseObjects = searchRootWordsWordToVerseObjects(q);
  } else if (mode === "arabic") {
    verseObjects = searchArabicToVerseObjects(q);
  } else if (mode === "english") {
    verseObjects = searchEnglishToVerseObjects(q);
  }

  const ms = Math.round(performance.now() - t0);
  setSearchStatus(`${verseObjects.length} result(s)`);
  renderSearchVerses(verseObjects);
}

// Render using your existing buildVerse()
function renderSearchVerses(verseObjects) {
  const showTranslation = localStorage.getItem("translate") === "en";
  const container = document.getElementById("search-verse-data");

  if (!verseObjects.length) {
    container.innerHTML = "<div>No results.</div>";
    return;
  }

  container.innerHTML = `
    <ul>
${verseObjects.map(v => {
    const verseContent = buildVerse(v, showTranslation);
    return `<li class="arabic">${verseContent}</li>`;
  }).join("")}
    </ul>
  `;

  // Apply translation visibility same as your main display
  const translationElements = container.querySelectorAll(".translation");
  translationElements.forEach((el) => {
    el.style.display = showTranslation ? "block" : "none";
  });
}

// ---------- Search Modes ----------
function searchRefToVerseObjects(q) {
  // q like "2:255"
  const m = q.match(/^\s*(\d{1,3})\s*:\s*(\d{1,3})\s*$/);
  if (!m) return [];
  const sura = parseInt(m[1], 10);
  const ayah = parseInt(m[2], 10);

  const s = suraData[String(sura)];
  if (!s) return [];
  if (ayah < 1 || ayah > s.nAyah) return [];

  const globalVerseId = String(s.start + (ayah - 1));
  const verseData = combinedQuranData[globalVerseId];
  if (!verseData) return [];

  // buildVerse() expects {Key, ID}
  // Choose Key as verseData.start_word to highlight the first word (simple + safe)
  return [{
    Key: "0",
    ID: `${sura}:${ayah}:1`
  }];
}

function searchRootWordsRootToVerseObjects(rootQuery) {
  // Exact root key match (fast)
  const root = rootQuery.trim();
  const rootObj = rootWordsData[root];
  if (!rootObj || !rootObj.Word) return [];

  const verseHits = [];
  const seen = new Set();

  for (const w of Object.keys(rootObj.Word)) {
    const verses = rootObj.Word[w]?.Verses || [];
    for (const hit of verses) {
      // hit.Key = global verse id, hit.ID = "sura:ayah:wordPos"
      if (!hit?.Key || !hit?.ID) continue;
      const unique = `${hit.Key}|${hit.ID}`;
      if (seen.has(unique)) continue;
      seen.add(unique);
      verseHits.push({ Key: hit.Key, ID: hit.ID });
    }
  }

  // Sort by global verse id
  verseHits.sort((a, b) => parseInt(a.Key, 10) - parseInt(b.Key, 10));
  return verseHits.slice(0, 500); // UI cap
}

function searchRootWordsWordToVerseObjects(wordQuery) {
  const qTrim = (wordQuery || "").trim().replace(/[\u064B-\u0652\u0670\u0640]/g, "");;
  if (!qTrim) return [];

  const qLen = qTrim.length;
  const verseHits = [];
  const seen = new Set();

  for (const root of Object.keys(rootWordsData)) {
    const wordsObj = rootWordsData[root]?.Word || {};
    for (const w of Object.keys(wordsObj)) {
      const isMatch = (qLen < 3) ? (w === qTrim) : w.includes(qTrim);
      if (!isMatch) continue;

      const verses = wordsObj[w]?.Verses || [];
      for (const hit of verses) {
        if (!hit?.Key || !hit?.ID) continue;

        // de-dupe
        const unique = `${hit.Key}|${hit.ID}`;
        if (seen.has(unique)) continue;
        seen.add(unique);

        verseHits.push({ Key: hit.Key, ID: hit.ID });
      }
    }
  }

  verseHits.sort((a, b) => parseInt(a.Key, 10) - parseInt(b.Key, 10));
  return verseHits.slice(0, 500);
}


function searchArabicToVerseObjects(q) {
  const qn = normalizeArabic(q);
  const hits = [];

  for (const globalVerseId of Object.keys(combinedQuranData)) {
    const a = combinedQuranData[globalVerseId].arabic || "";
    if (!normalizeArabic(a).includes(qn)) continue;

    const ref = verseIdToSuraAyah[globalVerseId];
    if (!ref) continue;

    const verseData = combinedQuranData[globalVerseId];
    hits.push({
      Key: "0",
      ID: `${ref.sura}:${ref.ayah}:1`
    });
  }

  return hits.slice(0, 500);
}

function searchEnglishToVerseObjects(q) {
  const ql = q.toLowerCase();
  const hits = [];

  for (const globalVerseId of Object.keys(combinedQuranData)) {
    const e = combinedQuranData[globalVerseId].en || "";
    if (!e.toLowerCase().includes(ql)) continue;

    const ref = verseIdToSuraAyah[globalVerseId];
    if (!ref) continue;

    const verseData = combinedQuranData[globalVerseId];
    hits.push({
      Key: "0",
      ID: `${ref.sura}:${ref.ayah}:1`
    });
  }

  return hits.slice(0, 500);
}

// Arabic normalization similar to earlier suggestions
function normalizeArabic(s) {
  return String(s)
    .replace(/[\u064B-\u0652\u0670\u0640]/g, "") // tashkeel + tatweel
    .replace(/[أإآ]/g, "ا")
    .replace(/ى/g, "ي")
    .replace(/ؤ/g, "و")
    .replace(/ئ/g, "ي")
    .replace(/ة/g, "ه")
    .trim();
}

// Arabic normalization similar to earlier suggestions
function removeTashkeel(s) {
  return String(s)
    .replace(/[\u064B-\u0652\u0670\u0640]/g, "") // tashkeel + tatweel
    .trim();
}

function setSearchStatus(msg) {
  document.getElementById("search-status").textContent = msg;
}
