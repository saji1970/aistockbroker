const CACHE_NAME = `ai-stock-trading-v${Date.now()}-bot-status-fix-${Math.random().toString(36).substr(2, 9)}`;
const urlsToCache = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  '/apple-touch-icon.png',
  '/icon-192.png',
  '/icon-512.png',
  '/icon-96.png',
  '/sw.js'
];

// Install event - cache resources
self.addEventListener('install', event => {
  console.log('Service worker installing with COMPLETE CACHE RESET...');
  event.waitUntil(
    // First, clear ALL existing caches aggressively
    caches.keys().then(cacheNames => {
      console.log('Found caches to delete:', cacheNames);
      return Promise.all(
        cacheNames.map(cacheName => {
          console.log('DELETING CACHE:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('All caches deleted, creating new cache...');
      // Then create new cache
      return caches.open(CACHE_NAME);
    }).then(cache => {
      console.log('Opened new cache:', CACHE_NAME);
      return cache.addAll(urlsToCache).catch(error => {
        console.log('Cache addAll failed:', error);
        // Cache individual files if addAll fails
        return Promise.all(
          urlsToCache.map(url => 
            cache.add(url).catch(err => 
              console.log(`Failed to cache ${url}:`, err)
            )
          )
        );
      });
    }).then(() => {
      console.log('Cache setup complete, forcing immediate activation...');
      // Force activation immediately
      return self.skipWaiting();
    })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // For API requests, always go to network and don't intercept CORS errors
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request).catch(error => {
        console.log('API fetch failed:', error);
        // Don't return 503 for API requests - let the browser handle CORS errors
        throw error;
      })
    );
    return;
  }

  // For JavaScript files, always fetch from network to ensure latest version
  if (event.request.url.includes('/static/js/') || event.request.url.includes('.js')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-cache' }).catch(error => {
        console.log('Network fetch failed for JS file:', error);
        return caches.match(event.request);
      })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version if available
        if (response) {
          return response;
        }
        
        // Fetch from network
        return fetch(event.request).catch(error => {
          console.log('Fetch failed:', error);
          
          // For navigation requests, return the cached index.html
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
          
          // For other requests, return a fallback response
          return new Response('Offline - Resource not available', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain'
            })
          });
        });
      })
  );
});

// Activate event - clean up old caches aggressively
self.addEventListener('activate', event => {
  console.log('Service worker activating with COMPLETE CACHE RESET...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      console.log('Found caches to delete during activation:', cacheNames);
      return Promise.all(
        cacheNames.map(cacheName => {
          console.log('DELETING CACHE:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('All caches deleted during activation, claiming clients...');
      // Force clients to reload immediately
      return self.clients.claim().then(() => {
        // Send message to all clients to reload
        return self.clients.matchAll().then(clients => {
          console.log('Found clients to reload:', clients.length);
          clients.forEach(client => {
            console.log('Sending FORCE_RELOAD to client');
            client.postMessage({ type: 'FORCE_RELOAD' });
            // Also try to navigate the client to force a reload
            client.navigate(client.url);
          });
        });
      });
    })
  );
});

// Background sync for offline data
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Handle background sync logic here
  console.log('Background sync triggered');
  return Promise.resolve();
}

// Push notification handling
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'New stock analysis available!',
    icon: '/icon-192.png',
    badge: '/icon-96.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Analysis',
        icon: '/icon-96.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icon-96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('AI Stock Trading', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/ai-assistant')
    );
  }
});
