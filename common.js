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

  function externalNetworkRequired(url) {
    return /^https?:\/\//i.test(String(url || "")) && !navigator.onLine;
  }

  function notifyOnlineFeature(feature = "This feature") {
    window.alert(`${feature} requires an internet connection. The Quran text, search, navigation, fonts, and morphology data remain available offline.`);
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
        banner.textContent = "Offline mode — Quran text, search, fonts and morphology are available. Audio and external manuscript links need internet.";
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
    externalNetworkRequired,
    notifyOnlineFeature,
  });

  document.addEventListener("DOMContentLoaded", installOfflineIndicator);
})();

// Browser/PWA support: the Go app remains a normal website, while the browser can
// install it and keep the Quran assets available offline.
(() => {
  "use strict";

  let installPrompt = null;
  let serviceWorkerRegistration = null;
  let reloadForUpdate = false;
  let installedThisSession = false;

  const isStandalone = () =>
    window.matchMedia?.("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  const getUI = () => ({
    installButton: document.getElementById("pwa-install-button"),
    updateButton: document.getElementById("pwa-update-button"),
    status: document.getElementById("pwa-status"),
  });

  function setStatus(message) {
    const { status } = getUI();
    if (status) status.textContent = message || "";
  }

  function refreshInstallUI() {
    const { installButton } = getUI();
    if (!installButton) return;

    installButton.hidden = isStandalone() || installedThisSession;
    installButton.disabled = false;
    installButton.textContent = "Install App";
  }

  function showUpdateAvailable(registration) {
    serviceWorkerRegistration = registration || serviceWorkerRegistration;
    const { updateButton } = getUI();
    if (updateButton) updateButton.hidden = false;
    setStatus("A new version is ready.");
  }

  function hideUpdateAvailable() {
    const { updateButton } = getUI();
    if (updateButton) updateButton.hidden = true;
  }

  async function installApp() {
    if (isStandalone()) {
      refreshInstallUI();
      return;
    }

    if (installPrompt) {
      installPrompt.prompt();
      const choice = await installPrompt.userChoice;
      installPrompt = null;
      if (choice?.outcome === "accepted") {
        setStatus("Installing Original Quran…");
      } else {
        setStatus("Installation was cancelled.");
      }
      refreshInstallUI();
      return;
    }

    // Safari/iOS do not expose beforeinstallprompt; unsupported or not-yet-eligible
    // browsers still get useful instructions instead of a disappearing button.
    const ua = navigator.userAgent || "";
    const isiOS = /iPad|iPhone|iPod/.test(ua);
    const isSafari = /Safari/.test(ua) && !/Chrome|Chromium|Edg/.test(ua);

    if (isiOS) {
      setStatus("On iPhone/iPad: tap Share, then Add to Home Screen.");
    } else if (isSafari) {
      setStatus("In Safari, use File > Add to Dock (or Share > Add to Home Screen where available).");
    } else {
      setStatus("Install is not available yet. Use HTTPS or localhost, then reload after the page finishes loading.");
    }
  }

  async function applyUpdate() {
    const registration = serviceWorkerRegistration;
    if (!registration?.waiting) {
      try {
        await registration?.update();
      } catch (error) {
        console.warn("PWA update check failed:", error);
      }
    }

    if (registration?.waiting) {
      reloadForUpdate = true;
      setStatus("Updating…");
      registration.waiting.postMessage({ type: "SKIP_WAITING" });
    } else {
      hideUpdateAvailable();
      setStatus("You already have the latest version.");
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    const { installButton, updateButton } = getUI();
    installButton?.addEventListener("click", installApp);
    updateButton?.addEventListener("click", applyUpdate);
    refreshInstallUI();
  });

  window.addEventListener("beforeinstallprompt", event => {
    event.preventDefault();
    installPrompt = event;
    refreshInstallUI();
    setStatus("Ready to install for offline use.");
  });

  window.addEventListener("appinstalled", () => {
    installPrompt = null;
    installedThisSession = true;
    refreshInstallUI();
    setStatus("Original Quran is installed.");
  });

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", async () => {
      try {
        const registration = await navigator.serviceWorker.register("./sw.js");
        serviceWorkerRegistration = registration;

        // If an update was already waiting when this page opened, expose it.
        if (registration.waiting && navigator.serviceWorker.controller) {
          showUpdateAvailable(registration);
        }

        registration.addEventListener("updatefound", () => {
          const worker = registration.installing;
          if (!worker) return;
          worker.addEventListener("statechange", () => {
            if (worker.state === "installed" && navigator.serviceWorker.controller) {
              showUpdateAvailable(registration);
            }
          });
        });

        // Check for a newer deployed service worker whenever the app loads.
        registration.update().catch(() => undefined);
      } catch (err) {
        console.warn("Offline service worker registration failed:", err);
        setStatus("Offline support could not be enabled in this browser.");
      }
    });

    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (reloadForUpdate) {
        reloadForUpdate = false;
        window.location.reload();
      }
    });
  }
})();
