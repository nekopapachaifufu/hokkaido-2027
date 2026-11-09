// 離線快取：第一次開啟後，沒有網路也能看行程
const CACHE = "hk27-v1";
const CORE = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  const isFont = url.hostname.endsWith("googleapis.com") || url.hostname.endsWith("gstatic.com");
  if (url.origin !== location.origin && !isFont) return;
  // 網頁本身：先抓最新版，沒網路時用快取
  if (e.request.mode === "navigate") {
    e.respondWith(fetch(e.request).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put("./index.html", cp)); return r; }).catch(() => caches.match("./index.html")));
    return;
  }
  // 其他檔案與字型：先用快取
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); return r; })));
});
