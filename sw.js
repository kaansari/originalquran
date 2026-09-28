const CACHE_NAME = 'originalquran-v6';
const BASE_URL = new URL('./', self.location.href);

const APP_ASSETS = [
  './',
  'app.js', 'app_quran.js', 'app_writing.js', 'common.js', 'favicon.ico',
  'fonts/Qahiri-Regular.ttf', 'fonts/Raqq.ttf',
  'fonts/UthmanicHafs1Ver09.woff', 'fonts/UthmanicHafs1Ver09.woff2',
  'fonts/UthmanicWarsh.otf', 'fonts/hafs/hafs.eot', 'fonts/hafs/hafs.otf',
  'fonts/hafs/hafs.woff', 'fonts/hafs/hafs.woff2', 'icon.png',
  'icon-192.png', 'icon-512.png', 'icons.css',
  'json/combined_harakat_quran.json', 'json/combined_quran.json',
  'json/en-word.json', 'json/pagination_map.json', 'json/quran_harakat_words.json',
  'json/quran_morphology.json', 'json/quran_words.json', 'json/quran_words_unique.json',
  'json/quranic_warsh_words.json', 'json/quranic_words.json', 'json/root_words.json',
  'json/sura.json', 'manifest.webmanifest', 'page.html', 'quran.html', 'random.html',
  'raqq.html', 'root.css', 'root.html', 'styles.css', 'styles_page.css',
  'styles_warsh.css', 'warsh.html', 'writing.css', 'writing.html',
  'writing_v2.html', 'writing_v2.js'
].map(path => new URL(path, BASE_URL).href);

const OFFLINE_PAGE = BASE_URL.href;

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_ASSETS)));
});

self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const requestURL = new URL(event.request.url);
  if (requestURL.origin !== self.location.origin) return;

  event.respondWith((async () => {
    const freshFirst = event.request.mode === 'navigate' || ['style', 'script', 'worker'].includes(event.request.destination);

    if (freshFirst) {
      try {
        const response = await fetch(event.request);
        if (response && response.ok) {
          const copy = response.clone();
          event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy)));
        }
        return response;
      } catch (error) {
        const cached = await caches.match(event.request);
        if (cached) return cached;
        if (event.request.mode === 'navigate') {
          const fallback = await caches.match(OFFLINE_PAGE);
          if (fallback) return fallback;
        }
        throw error;
      }
    }

    const cached = await caches.match(event.request);
    if (cached) return cached;

    const response = await fetch(event.request);
    if (response && response.ok) {
      const copy = response.clone();
      event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy)));
    }
    return response;
  })());
});
