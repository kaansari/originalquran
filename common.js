(() => {
  "use strict";

  async function loadJSON(url) {
    const finish = window.SiteUI?.beginLoading() || (() => {});
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(url, { cache: "default", signal: controller.signal });
      if (!response.ok) throw new Error(`Failed to load ${url}: HTTP ${response.status}`);
      const data = await response.json();
      finish();
      return data;
    } catch (error) {
      finish(error);
      throw error;
    } finally {
      window.clearTimeout(timeout);
    }
  }

  function escapeHTML(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function openInNewTab(url) {
    const opened = window.open(url, "_blank", "noopener,noreferrer");
    if (opened) opened.opener = null;
  }

  let rootNotesRequest;

  function rootNotesRow(root) {
    if (!root || root === "N/A") return "";
    if (!rootNotesRequest) {
      rootNotesRequest = loadJSON("json/root_notes.json").catch(error => {
        console.warn("Root notes are unavailable:", error);
        rootNotesRequest = null;
        return {};
      });
    }
    // Runs after the caller has appended the popup, without delaying morphology.
    rootNotesRequest.then(index => {
      document.querySelectorAll(".root-notes-row").forEach(row => {
        const root = row.dataset.notesRoot;
        const source = index[root]?.source;
        if (typeof source !== "string" || !/^notes\/[^/]+\.md$/.test(source)) return;
        const link = document.createElement("a");
        link.href = source;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `Read notes for ${root}`;
        const cell = row.querySelector("td");
        cell.textContent = "";
        cell.appendChild(link);
        row.hidden = false;
      });
    });
    return `<tr class="root-notes-row" data-notes-root="${escapeHTML(root)}" hidden><th>Notes</th><td></td></tr>`;
  }

  function externalNetworkRequired(url) {
    return /^https?:\/\//i.test(String(url || "")) && !navigator.onLine;
  }

  function notifyOnlineFeature(feature = "This feature") {
    window.alert(`${feature} requires an internet connection. Reconnect to continue using the site.`);
  }

  function installOfflineIndicator() {
    if (document.getElementById("offline-status")) return;
    const banner = document.createElement("div");
    banner.id = "offline-status";
    banner.setAttribute("role", "status");
    banner.setAttribute("aria-live", "polite");
    document.body.appendChild(banner);

    const update = () => {
      if (navigator.onLine) {
        banner.hidden = true;
        banner.textContent = "";
      } else {
        banner.hidden = false;
        banner.textContent = "You are offline. Reconnect to load Quran pages and other site content.";
      }
    };

    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    update();
  }

  // Shared audio and word details for paginated, chapter and root readers.
  let currentAudio = null;
  function playAudio(audioSrc) {
    if (!audioSrc) {
      console.error("Invalid audio source.");
      return;
    }

    if (externalNetworkRequired(audioSrc)) {
      notifyOnlineFeature("Audio playback");
      return;
    }

    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
    }

    const audio = new Audio(audioSrc);
    currentAudio = audio;

    audio.addEventListener("play", () => {
      // Optional: Visual feedback
    });

    audio.addEventListener("ended", () => {
      if (currentAudio === audio) currentAudio = null;
      // Optional: Remove visual feedback
    });

    audio.addEventListener("error", (e) => {
      console.error("Error playing audio:", e);
      window.alert("Failed to play audio.");
      if (currentAudio === audio) currentAudio = null;
    });

    audio.play().catch((error) => {
      console.error("Playback failed:", error);
      window.alert("Unable to play the selected audio.");
    });
  }

  function showWordMorphologyPopup(wordId, wordElement, morphology) {
    const wordData = wordElement.textContent;
    const enData = wordElement.getAttribute("data-en");
    const wordMorphology = morphology[wordId];

    if (!wordData || !wordMorphology) {
      console.error("No data found for wordId:", wordId);
      return;
    }

    removeExistingPopup();

    const wordObjects = wordMorphology.words;
    playAudio(wordAudioURL(wordMorphology.id));

    const tableContent = buildMorphologyTable(wordObjects);

    const popupContent = `
      <span id="morphology-popup-title">
        ${escapeHTML(wordData)}, ${escapeHTML(enData)}
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

  function buildMorphologyTable(wordObjects) {
    let tableContent = "";

    for (let wordId in wordObjects) {
      const wordMorphology = wordObjects[wordId];

      tableContent += `
      <tr><th>Word</th><td>${escapeHTML(wordMorphology.word || "N/A")}</td></tr>
      <tr><th>POS</th><td>${escapeHTML(wordMorphology.pos || "N/A")}</td></tr>
      <tr><th>Root</th><td>${
        wordMorphology.root && wordMorphology.root !== "N/A"
          ? `<span class="clickable-root" style="cursor:pointer; color:blue; text-decoration: underline;">${escapeHTML(wordMorphology.root)}</span>`
          : "N/A"
      }</td></tr>
      ${rootNotesRow(wordMorphology.root)}
      <tr><th>Lemma</th><td>${escapeHTML(wordMorphology.lemma || "N/A")}</td></tr>
      <tr><th>Morphology</th><td>${escapeHTML(wordMorphology.morphology || "N/A")}</td></tr>
      <tr><td colspan="2"><hr></td></tr>
      `;
    }

    // After generating the table content, attach the event listeners for root clicks
    setTimeout(() => {
      const clickableRoots = document.querySelectorAll(".clickable-root");

      clickableRoots.forEach((rootElement) => {
        rootElement.addEventListener("click", () => {
          const rootWord = rootElement.textContent;

          // Save the root word to localStorage
          localStorage.setItem("selectedRoot", rootWord);

          // Open the root.html page in a new tab
          openInNewTab("root.html");
        });
      });
    }, 0);

    return tableContent;
  }

  function removeExistingPopup() {
    const existingPopup = document.querySelector(".morphology-popup");
    if (existingPopup) {
      existingPopup.remove();
      document.removeEventListener("click", handleOutsideClick);
    }
  }

  function handleOutsideClick(event) {
    // Check if the clicked target is neither inside the popup nor a word element
    if (
      !event.target.closest(".morphology-popup") &&
      !event.target.closest(".word")
    ) {
      removeExistingPopup();
    }
  }

  function wordAudioURL(key) {
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

    const url = `https://audios.quranwbw.com/words/${surah}/${surahStr}_${ayahStr}_${wordStr}.mp3`;
    return url;
  }

  window.QuranUtils = Object.freeze({
    playAudio,
    wordAudioURL,
    showWordMorphologyPopup,
    loadJSON,
    escapeHTML,
    openInNewTab,
    rootNotesRow,
    externalNetworkRequired,
    notifyOnlineFeature,
  });

  document.addEventListener("DOMContentLoaded", installOfflineIndicator);
})();

// Page metadata supplies the small label above the site name.
(() => {
  function showPageInfo() {
    const label = document.querySelector(".site-eyebrow");
    const info = document.querySelector('meta[name="page-info"]');
    if (label) label.textContent = info?.content || document.title;
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", showPageInfo);
  else showPageInfo();
})();
