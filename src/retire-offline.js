// Retire this site's former offline app without touching preferences or other apps.
(async () => {
  if (!('serviceWorker' in navigator)) return;
  const workerURL = new URL('sw.js', document.baseURI).href;
  const ownsWorker = worker => worker?.scriptURL === workerURL;
  try {
    const controlled = ownsWorker(navigator.serviceWorker.controller);
    const registrations = await navigator.serviceWorker.getRegistrations();
    await Promise.all(registrations.filter(registration =>
      [registration.active, registration.waiting, registration.installing].some(ownsWorker)
    ).map(registration => registration.unregister()));
    if ('caches' in window) {
      const keys = await caches.keys();
      await Promise.all(keys.filter(key => key.startsWith('originalquran-')).map(key => caches.delete(key)));
    }
    if (controlled) window.location.reload();
  } catch (error) {
    console.warn('Could not remove the previous offline cache:', error);
  }
})();
