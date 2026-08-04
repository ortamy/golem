const CACHE_NAME = 'golem-cache-v9';
const PRECACHE_URLS = ['index.html', 'css/admin.css', 'css/agent-map.css', 'css/agent-server.css', 'css/block-renderer.css', 'css/board-generator.css', 'css/board.css', 'css/cartography.css', 'css/dashboard.css', 'css/davar-checker.css', 'css/tree-checker.css', 'css/etymology-lab.css', 'css/exposure-editor.css', 'css/heraldry.css', 'css/investigation.css', 'css/lab-hero.css', 'css/lab.css', 'css/language-map.css', 'css/linguistic-tensor.css', 'css/learn.css', 'css/load-researches.js', 'css/methodology.css', 'css/paleo-glossary.css', 'css/paleo-linguistics.css', 'css/prompt-generator.css', 'css/religionisms.css', 'css/research-library.css', 'css/section-renderer.css', 'css/root-dictionary.css', 'css/scripture-reader.css', 'css/states.css', 'css/translation-comparator.css', 'css/word-analyzer.css', 'js/access-gate.js', 'js/admin-settings.js', 'js/agent-map.js', 'js/agent-server.js', 'js/board-generator.js', 'js/board-library.js', 'js/board.js', 'js/cartography.js', 'js/dashboard.js', 'js/davar-checker.js', 'js/tree-checker.js', 'js/ed-chat.js', 'js/etymology-lab.js', 'js/exposure-editor.js', 'js/heraldry.js', 'js/investigation.js', 'js/lab-hero.js', 'js/language-map.js', 'js/linguistic-tensor.js', 'js/learn.js', 'js/load-researches.js', 'js/methodology.js', 'js/paleo-glossary.js', 'js/paleo-keyboard.js', 'js/paleo-letters.js', 'js/paleo-linguistics.js', 'js/prompt-generator.js', 'js/religionism-checker.js', 'js/root-dictionary.js', 'js/router.js', 'js/scripture-reader.js', 'js/states.js', 'js/translation-comparator.js', 'js/vision-ui.js', 'js/vision.js', 'js/modules/block-renderer.js', 'js/modules/exposure-case.js', 'js/modules/section-renderer.js', 'js/modules/religionisms.js', 'data/cartography.json', 'data/dictionaries.json', 'data/lab-config.json', 'data/methodology.json', 'data/paleo-glossary/roots.json', 'data/paleo-mechanics.json', 'data/qumran-books.json', 'data/states.json', 'data/timeline.json', 'data/witnesses.json', 'data/exposures/documents.json', 'data/exposures/index.json', 'data/heraldry/heraldry.json', 'data/language-map/languages.json', 'data/learn/alphabet.json', 'data/methodology/cards.json', 'data/paleo-linguistics/akkadian.json', 'data/paleo-linguistics/arabic.json', 'data/paleo-linguistics/aramaic.json', 'data/paleo-linguistics/eblaite.json', 'data/paleo-linguistics/evolution.json', 'data/paleo-linguistics/languages.json', 'data/paleo-linguistics/paleo-hebrew.json', 'data/paleo-linguistics/phoenician.json', 'data/paleo-linguistics/proto-canaanite.json', 'data/paleo-linguistics/ugaritic.json', 'data/prompts/blocks.json', 'data/prompts/index.json', 'data/religionisms/religionisms.json', 'data/research/emuna.json', 'data/research/hesed.json', 'data/research/kadosh.json', 'data/research/korban.json', 'data/research/template.json', 'data/research/teshuva.json', 'data/research/tohu.json', 'data/roots/roots.json', 'data/scripture/bereshit-1.json', 'pages/tree-checker.html'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
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
  if (new URL(event.request.url).origin !== self.location.origin) return;

  event.respondWith(
    fetch(event.request).then(networkResponse => {
      if (networkResponse && networkResponse.ok) {
        const responseCopy = networkResponse.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseCopy));
      }
      return networkResponse;
    }).catch(() => caches.match(event.request).then(cachedResponse => cachedResponse || Response.error()))
  );
});