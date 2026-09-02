const CACHE_NAME = "trip-expense-tracker-v1";

const FILES_TO_CACHE = [
    "/",
    "/static/css/style.css",
    "/static/js/script.js",
    "/static/manifest.json"
];

self.addEventListener("install", function (event) {

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function (cache) {
                return cache.addAll(FILES_TO_CACHE);
            })
    );

});


self.addEventListener("fetch", function (event) {

    event.respondWith(
        caches.match(event.request)
            .then(function (cachedResponse) {

                if (cachedResponse) {
                    return cachedResponse;
                }

                return fetch(event.request);

            })
    );

});


self.addEventListener("activate", function (event) {

    event.waitUntil(
        caches.keys()
            .then(function (cacheNames) {

                return Promise.all(
                    cacheNames
                        .filter(function (cacheName) {
                            return cacheName !== CACHE_NAME;
                        })
                        .map(function (cacheName) {
                            return caches.delete(cacheName);
                        })
                );

            })
    );

});