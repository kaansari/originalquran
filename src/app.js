let suraData, combinedData, wordsData, morphology;

// Fetch all JSON data (sura.json, combined_quran.json, quran_words.json)
Promise.all([
  fetch("json/sura.json").then((response) => response.json()),
  fetch("json/combined_quran.json").then((response) => response.json()),
  fetch("json/quran_words.json").then((response) => response.json()),
  fetch("json/quran_morphology.json").then((response) => response.json()),
])
  .then((data) => {
    suraData = data[0];
    combinedData = data[1];
    wordsData = data[2];
    morphology = data[3];
    // console.log("Sura Data:", suraData); // Log the data to make sure it loads
    //  console.log("Combined Data:", combinedData);
    console.log("Words Data:", wordsData);
    populateSuraSelector();
    loadSelections(); // Load the saved selections when the page reloads
  })
  .catch((error) => {
    console.error("Error loading JSON files:", error);
  });

// Populate Sura Selector
function populateSuraSelector() {
  const suraSelect = document.getElementById("sura-select");
  suraSelect.innerHTML = "";
  for (let suraNumber in suraData) {
    const option = document.createElement("option");
    option.value = suraNumber;
    option.textContent = suraNumber + ". " + suraData[suraNumber].name;
    suraSelect.appendChild(option);
  }
  suraSelect.addEventListener("change", () => {
    saveSelections(); // Save the selections whenever Sura is changed
    populateVerseSelector();
    goToSelectedVerse(); // Automatically display verses when Sura changes
  });
  populateVerseSelector(); // Populate verses for the first sura initially
}

// Populate Verse Selector based on selected sura with local verse numbering
function populateVerseSelector() {
  const suraNumber = document.getElementById("sura-select").value;
  const verseSelect = document.getElementById("verse-select");
  const sura = suraData[suraNumber];
  verseSelect.innerHTML = "";

  // Loop through the verses of the sura and show local verse numbers
  for (let verseNumber = sura.start; verseNumber <= sura.end; verseNumber++) {
    const option = document.createElement("option");
    const localVerseNumber = verseNumber - sura.start + 1; // Calculate local verse number
    option.value = verseNumber; // Use global verse number
    option.textContent = localVerseNumber; // Display the local verse number in the selector
    verseSelect.appendChild(option);
  }

  verseSelect.addEventListener("change", () => {
    saveSelections(); // Save the selections when Verse is changed
    goToSelectedVerse(); // Automatically display the selected verse
  });
}

// Display the selected sura and its verses with local verse numbering
function displaySura(suraNumber, targetVerse = null) {
  const sura = suraData[suraNumber];
  const container = document.getElementById("quran-container");
  container.innerHTML = `<h3>${suraNumber}. ${sura.name}</h3>`;

  let verseToScroll = null; // To store the element we need to scroll to

  // Loop through the verses in the sura
  for (let verseNumber = sura.start; verseNumber <= sura.end; verseNumber++) {
    const verseData = combinedData[verseNumber];
    const constructedArabic = buildVerseFromWords(
      verseData.start_word,
      verseData.end_word
    );

    // Calculate the local verse number
    const localVerseNumber = verseNumber - sura.start + 1;

    // Format sura and verse numbers to be three digits each
    const formattedSuraNumber = String(suraNumber).padStart(3, "0"); // Sura as 3 digits
    const formattedVerseNumber = String(localVerseNumber).padStart(3, "0"); // Verse as 3 digits

    // Combine formatted sura and verse to create the id, e.g., 001001
    const combinedId = `${formattedSuraNumber}${formattedVerseNumber}`;

    // Define the path to the audio file
    const audioSrc = `https://everyayah.com/data/Husary_64kbps/${combinedId}.mp3`;

    // Display the verse
    const verseDiv = document.createElement("div");
    verseDiv.className = "verse";
    verseDiv.innerHTML = `
      <div class="verse-container" id="verse-${combinedId}">
        <div class="verse-header">
  

          <h5 class="verse-number">
  <a href="#" onclick="navigateToExternalVerse(${localVerseNumber},${suraNumber})" target="_blank" class="verse-link">${localVerseNumber}</a>
</h5>

          <button class="play-button" data-audio-src="${audioSrc}"></button> <!-- Simple play button -->
        </div>
        <div id="${combinedId}" class="arabic verse-text">${constructedArabic}</div> <!-- Arabic verse right-aligned -->
      </div>
    `;
    container.appendChild(verseDiv);

    // If targetVerse is provided and matches the current global verse number
    if (targetVerse && parseInt(targetVerse) === verseNumber) {
      verseToScroll = verseDiv;
    }
  }

  // Scroll to the selected verse, if specified
  if (verseToScroll) {
    verseToScroll.scrollIntoView({ behavior: "smooth" });
  }

  // Add event listeners for play buttons
  document.querySelectorAll(".play-button").forEach((button) => {
    button.addEventListener("click", function () {
      const audioSrc = this.getAttribute("data-audio-src");
      playAudio(audioSrc);
    });
  });
}

function navigateToExternalVerse(verseNumber, sura) {
  const baseURL = 'https://corpuscoranicum.de/en/verse-navigator/';
  const fullURL = `${baseURL}sura/${sura}/verse/${verseNumber}/manuscripts`;
  window.open(fullURL, '_blank');
}

// Function to play the audio for the selected verse
let currentAudio = null; // Global reference to the current playing audio

function playAudio(audioSrc) {
  if (currentAudio) {
    currentAudio.pause(); // Pause any currently playing audio
  }

  currentAudio = new Audio(audioSrc); // Create a new audio instance
  currentAudio.play(); // Play the audio
}

// Navigate to the selected sura and verse
function goToSelectedVerse() {
  const suraNumber = document.getElementById("sura-select").value;
  const verseNumber = document.getElementById("verse-select").value;
  displaySura(suraNumber, verseNumber);
}

// Build a verse using the word indices from quran_words.json
function buildVerseFromWords(startIndex, endIndex) {
  const words = [];
  for (let i = startIndex; i <= endIndex; i++) {
    const wordData = wordsData[i]; // Get the word data from quran_words.json
    const wordId = i; // Use the word index as the ID

    // Create a word element with a click for the popup
    words.push(`
      <span class="word" onclick="showWordMorphologyPopup(${wordId},this)">
        ${wordData}
      </span>
    `);
  }
  return words.join(" ");
}

// Save selected Sura and Verse to localStorage
function saveSelections() {
  const suraSelect = document.getElementById("sura-select");
  const verseSelect = document.getElementById("verse-select");
  localStorage.setItem("selectedSura", suraSelect.value);
  localStorage.setItem("selectedVerse", verseSelect.value);
}

// Load the saved selections from localStorage when the page reloads
function loadSelections() {
  const savedSura = localStorage.getItem("selectedSura");
  const savedVerse = localStorage.getItem("selectedVerse");

  const suraSelect = document.getElementById("sura-select");
  const verseSelect = document.getElementById("verse-select");

  if (savedSura) {
    suraSelect.value = savedSura;
    populateVerseSelector(); // Update verse selector based on saved Sura
    if (savedVerse) {
      verseSelect.value = savedVerse;
    }
  }

  // Automatically display the saved sura and verse
  displaySura(suraSelect.value, verseSelect.value);
}

function showWordMorphologyPopup(wordId, wordElement) {
  const wordData = wordsData[wordId]; // Get the word data from quran_words.json
  const wordMorphology = morphology[wordId]; // Get the specific morphology data

  if (!wordData || !wordMorphology) {
    console.error("No data found for wordId:", wordId);
    return; // Avoid proceeding if no data is found
  }

  // If a popup already exists, remove it before showing a new one
  removeExistingPopup();

  const wordObjects = wordMorphology.words; // Extract words for the given verse

  // Generate the table content using the buildMorphologyTable function
  const tableContent = buildMorphologyTable(wordObjects);

  // Create the popup content
  const popupContent = `
  <span>
${wordData}
    <table>
     ${tableContent}
    </table>
</span>
  `;

  // Create the popup element
  const popup = document.createElement("div");
  popup.className = "morphology-popup";
  popup.innerHTML = popupContent;

  // Position the popup relative to the word
  const rect = wordElement.getBoundingClientRect();
  popup.style.top = `${rect.bottom + window.scrollY}px`;
  popup.style.left = `${rect.left + window.scrollX}px`;

  document.body.appendChild(popup);

  // Add a click listener to remove the popup when clicking outside
  document.addEventListener("click", handleOutsideClick);
}

// Function to traverse the JSON object and build the table rows
function buildMorphologyTable(wordObjects) {
  let tableContent = "";

  // Loop through each sub-object in "words"
  for (let wordId in wordObjects) {
    const wordMorphology = wordObjects[wordId];

    // Append table rows for each property in the word object
    tableContent += `
      <tr><th>Word</th><td>${wordMorphology.word || "N/A"}</td></tr>
      <tr><th>POS</th><td>${wordMorphology.pos || "N/A"}</td></tr>
      <tr><th>Root</th><td>${wordMorphology.root || "N/A"}</td></tr>
      <tr><th>Lemma</th><td>${wordMorphology.lemma || "N/A"}</td></tr>
      <tr><th>Morphology</th><td>${wordMorphology.morphology || "N/A"}</td></tr>
      <tr><td colspan="2"><hr></td></tr> <!-- Add a separator between words -->
    `;
  }

  // Return the built HTML string for the table content
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
  if (
    !event.target.closest(".morphology-popup") &&
    !event.target.closest(".word")
  ) {
    removeExistingPopup();
  }
}

// Function to show the image popup
function showVerseImages(verseId) {
  const directory = `media/images/${verseId}`;

  // Fetch verse from combinedData
  const verseText = combinedData[verseId]?.arabic || "Verse not found"; // Get the Arabic verse text

  // Set the verse text in the popup
  const verseElement = document.getElementById("verse-text");
  verseElement.innerText = verseText; // Set the verse text on the element

  // Fetch images for the grid
  //fetchImagesFromDirectory(directory, verseId)
  //  .then((files) => {
 //     const imageGrid = document.getElementById("image-grid");
 //     imageGrid.innerHTML = ""; // Clear previous images

  //    files.forEach((file) => {
 //       const imgElement = document.createElement("img");
 //       imgElement.src = `${directory}/${file}`; // Full image path
  //      imageGrid.appendChild(imgElement);
   //   });

//      // Show the image popup
//     document.getElementById("image-popup").style.display = "block";
 //   })
 //   .catch((error) => {
 //    console.error("Error loading images:", error);
  //  });

  document.getElementById("image-popup").style.display = "block";
}

// Function to close the image popup
function closeImagePopup() {
  document.getElementById("image-popup").style.display = "none";
}

// Function to fetch images (mock)
function fetchImagesFromDirectory(directory, verseId) {
  return new Promise((resolve, reject) => {
    // Simulating fetching image files
    resolve([`1.png`, `2.png`, `3.png`, `4.png`]); // Example: 4 PNG files
  });
}

// Function to close the image popup
function closeImagePopup() {
  document.getElementById("image-popup").style.display = "none";
}

// Function to fetch images (mock)
function fetchImagesFromDirectory(directory, verseId) {
  return new Promise((resolve, reject) => {
    // Simulating fetching image files
    resolve([`1.png`, `2.png`, `3.png`, `4.png`]); // Example: 4 PNG files
  });
}
