const CACHE_NAME = 'financial-monitor-v1';
const STATIC_CACHE = 'financial-monitor-static-v1';
const DATA_CACHE = 'financial-monitor-data-v1';

const STATIC_FILES = [
    '/',
    '/index.html',
    '/css/style.css',
    '/css/components.css',
    '/css/responsive.css',
    '/js/api.js',
    '/js/app.js',
    '/manifest.json'
];

const API_CACHE_TIME = 60 * 1000;

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => {
            return cache.addAll(STATIC_FILES.map((url) => new Request(url, { cache: 'reload' })));
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((cacheName) => {
                        return cacheName !== STATIC_CACHE && cacheName !== DATA_CACHE;
                    })
                    .map((cacheName) => {
                        return caches.delete(cacheName);
                    })
            );
        })
    );
    return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    if (url.pathname.startsWith('/api/')) {
        handleAPIRequest(event, request);
    } else {
        handleStaticRequest(event, request);
    }
});

function handleAPIRequest(event, request) {
    event.respondWith(
        caches.open(DATA_CACHE).then((cache) => {
            return cache.match(request).then((cachedResponse) => {
                const fetchPromise = fetch(request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        cache.put(request, networkResponse.clone());
                    }
                    return networkResponse;
                }).catch((error) => {
                    console.log('API request failed, returning cached response:', error);
                    return cachedResponse;
                });

                if (cachedResponse) {
                    const cachedDate = cachedResponse.headers.get('date');
                    const cacheAge = cachedDate ? Date.now() - new Date(cachedDate).getTime() : Infinity;
                    
                    if (cacheAge < API_CACHE_TIME) {
                        return cachedResponse;
                    }
                }

                return fetchPromise;
            });
        })
    );
}

function handleStaticRequest(event, request) {
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
                return cachedResponse;
            }

            return fetch(request).then((networkResponse) => {
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                    return networkResponse;
                }

                const responseToCache = networkResponse.clone();
                caches.open(STATIC_CACHE).then((cache) => {
                    cache.put(request, responseToCache);
                });

                return networkResponse;
            }).catch((error) => {
                console.log('Fetch failed:', error);
                return caches.match('/index.html');
            });
        })
    );
}

self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-data') {
        event.waitUntil(syncData());
    }
});

self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : '有新的价格更新',
        icon: '/assets/icons/icon-192.png',
        badge: '/assets/icons/icon-72.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/'
        }
    };

    event.waitUntil(
        self.registration.showNotification('金融价格监控', options)
    );
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/')
    );
});

async function syncData() {
    try {
        const response = await fetch('/api/market/precious-metals');
        if (response.ok) {
            console.log('Data synced successfully');
        }
    } catch (error) {
        console.error('Sync failed:', error);
    }
}
