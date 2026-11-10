(() => {
  "use strict";

  async function loadJSON(url) {
    const response = await fetch(url, { cache: "default" });
    if (!response.ok) {
      throw new Error(`Failed to load ${url}: HTTP ${response.status}`);
    }
    return response.json();
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

  window.QuranUtils = Object.freeze({
    loadJSON,
    escapeHTML,
    openInNewTab,
    rootNotesRow,
    externalNetworkRequired,
    notifyOnlineFeature,
  });

  document.addEventListener("DOMContentLoaded", installOfflineIndicator);
})();

// The header control shares the existing theme preference and settings checkbox.
(() => {
  function initTheme() {
    const button = document.getElementById("site-theme-button");
    const checkbox = document.getElementById("theme-toggle");
    function syncTheme() {
      const dark = document.body.classList.contains("dark-theme");
      button?.setAttribute("aria-pressed", String(dark));
      button?.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
      if (checkbox) checkbox.checked = dark;
    }
    let saved;
    try { saved = localStorage.getItem("theme"); } catch {}
    const dark = saved ? saved === "dark" : window.matchMedia?.("(prefers-color-scheme: dark)").matches;
    document.body.classList.toggle("dark-theme", Boolean(dark));
    syncTheme();
    button?.addEventListener("click", () => {
      const dark = !document.body.classList.contains("dark-theme");
      document.body.classList.toggle("dark-theme", dark);
      try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch {}
      syncTheme();
    });
    // Existing settings controls can still change the body's theme class.
    new MutationObserver(syncTheme).observe(document.body, { attributes: true, attributeFilter: ["class"] });
    window.addEventListener("storage", event => {
      if (event.key !== "theme") return;
      document.body.classList.toggle("dark-theme", event.newValue === "dark");
      syncTheme();
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initTheme);
  else initTheme();
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
