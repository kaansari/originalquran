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
