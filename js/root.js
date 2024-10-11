// Fetch root words JSON file and initialize selectors
fetch('json/root_words.json')
  .then((response) => response.json())
  .then((rootWordsData) => {
    populateRootSelect(rootWordsData);
    loadSelections(rootWordsData); // Load saved selections on page load
  })
  .catch((error) => console.error('Error loading root words data:', error));

// Populate the root selector with root words in ascending order
function populateRootSelect(rootWordsData) {
  const rootSelect = document.getElementById('root-select');
  rootSelect.innerHTML = '';

  // Sort the root words in ascending order
  const sortedRoots = Object.keys(rootWordsData).sort();

  sortedRoots.forEach((root) => {
    const option = document.createElement('option');
    option.value = root;
    option.textContent = root;
    rootSelect.appendChild(option);
  });

  rootSelect.addEventListener('change', () => {
    saveSelections(); // Save the root selection
    populateWordSelect(rootWordsData);
  });

  populateWordSelect(rootWordsData); // Populate child words for the first root initially
}

// Populate the word selector with words for the selected root in ascending order
function populateWordSelect(rootWordsData) {
  const rootSelect = document.getElementById('root-select');
  const wordSelect = document.getElementById('word-select');
  const selectedRoot = rootSelect.value;
  const words = rootWordsData[selectedRoot].Word;

  wordSelect.innerHTML = '';

  // Sort the child words in ascending order
  const sortedWords = Object.keys(words).sort();

  sortedWords.forEach((word) => {
    const option = document.createElement('option');
    option.value = word;
    option.textContent = word;
    wordSelect.appendChild(option);
  });

  wordSelect.addEventListener('change', () => {
    saveSelections(); // Save the word selection
    displayVerses(rootWordsData);
  });

  displayVerses(rootWordsData); // Display verses for the first word initially
}

// Display verses and counts for the selected word
function displayVerses(rootWordsData) {
  const rootSelect = document.getElementById('root-select');
  const wordSelect = document.getElementById('word-select');
  const selectedRoot = rootSelect.value;
  const selectedWord = wordSelect.value;
  const verseContainer = document.getElementById('verse-container');

  const wordData = rootWordsData[selectedRoot].Word[selectedWord];
  const rootCount = rootWordsData[selectedRoot].RootCount;
  const wordCount = wordData.WordCount;
  const verseCount = wordData.VerseCount;
  const verses = wordData.Verses;

  // Display root, word, and verse counts
  verseContainer.innerHTML = `
    <h3>Root Count: ${rootCount}</h3>
    <h3>Word Count: ${wordCount}</h3>
    <h3>Verse Count: ${verseCount}</h3>
  `;

  // Display the verses
  verses.forEach((verse) => {
    const verseElement = document.createElement('div');
    verseElement.textContent = `Verse Key: ${verse.Key}, Verse ID: ${verse.ID}`;
    verseContainer.appendChild(verseElement);
  });
}

// Save selected root and word to localStorage
function saveSelections() {
  const rootSelect = document.getElementById('root-select');
  const wordSelect = document.getElementById('word-select');
  localStorage.setItem('selectedRoot', rootSelect.value);
  localStorage.setItem('selectedWord', wordSelect.value);
}

// Load saved root and word selections from localStorage
function loadSelections(rootWordsData) {
  const savedRoot = localStorage.getItem('selectedRoot');
  const savedWord = localStorage.getItem('selectedWord');
  const rootSelect = document.getElementById('root-select');
  const wordSelect = document.getElementById('word-select');

  if (savedRoot && rootWordsData[savedRoot]) {
    rootSelect.value = savedRoot;
    populateWordSelect(rootWordsData); // Update word select based on saved root
    if (savedWord && rootWordsData[savedRoot].Word[savedWord]) {
      wordSelect.value = savedWord;
    }
  }

  // Automatically display the verses for the saved word
  displayVerses(rootWordsData);
}
