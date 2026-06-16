// Service Worker for Macro Timeline v1.02
// Network-first strategy: always fetch fresh data first

const CACHE_NAME = 'macro-timeline-v1.02';
const DATA_FILE = 'data/calendar_data.js';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './' + DATA_FILE
];

// Install: cache all assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: network-first for data, cache-first for app shell
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const isData = url.pathname.includes(DATA_FILE);

  if (isData) {
    // Network-first: always try to get fresh data
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first: fast loading for app shell
    event.respondWith(
      caches.match(event.request).then((cached) => {
        const fetchPromise = fetch(event.request).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, clone);
            });
          }
          return response;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    );
  }
});
