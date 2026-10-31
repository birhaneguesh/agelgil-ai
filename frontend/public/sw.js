// Stub SW: proves SW registration on a real HTTPS origin (P1.03).
// Replaced by vite-plugin-pwa / Workbox at P3.05.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));
self.addEventListener("fetch", () => { /* pass-through */ });
