const CACHE_NAME = 'golem-cache-v1';
const PRECACHE_URLS = ['index.html', 'css/admin.css', 'css/agent-map.css', 'css/agent-server.css', 'css/block-renderer.css', 'css/board-generator.css', 'css/board.css', 'css/cartography.css', 'css/dashboard.css', 'css/davar-checker.css', 'css/etymology-lab.css', 'css/exposure-editor.css', 'css/heraldry.css', 'css/investigation.css', 'css/lab-hero.css', 'css/lab.css', 'css/language-map.css', 'css/learn.css', 'css/methodology.css', 'css/paleo-images.css', 'css/paleo-linguistics.css', 'css/prompt-generator.css', 'css/religionisms.css', 'css/research-library.css', 'css/root-dictionary.css', 'css/scripture-reader.css', 'css/states.css', 'css/translation-comparator.css', 'css/word-analyzer.css', 'js/access-gate.js', 'js/admin-settings.js', 'js/agent-map.js', 'js/agent-server.js', 'js/board-generator.js', 'js/board-library.js', 'js/board.js', 'js/cartography.js', 'js/dashboard.js', 'js/davar-checker.js', 'js/ed-chat.js', 'js/etymology-lab.js', 'js/exposure-editor.js', 'js/heraldry.js', 'js/investigation.js', 'js/lab-hero.js', 'js/language-map.js', 'js/learn.js', 'js/load-researches.js', 'js/methodology.js', 'js/paleo-images.js', 'js/paleo-keyboard.js', 'js/paleo-letters.js', 'js/paleo-linguistics.js', 'js/prompt-generator.js', 'js/religionism-checker.js', 'js/root-dictionary.js', 'js/router.js', 'js/scripture-reader.js', 'js/states.js', 'js/translation-comparator.js', 'js/vision-ui.js', 'js/vision.js', 'js/modules/block-renderer.js', 'js/modules/exposure-case.js', 'js/modules/religionisms.js', 'data/cartography.json', 'data/dictionaries.json', 'data/lab-config.json', 'data/methodology.json', 'data/paleo-mechanics.json', 'data/qumran-books.json', 'data/states.json', 'data/witnesses.json', 'data/exposures/documents.json', 'data/exposures/index.json', 'data/heraldry/heraldry.json', 'data/language-map/languages.json', 'data/learn/alphabet.json', 'data/methodology/cards.json', 'data/paleo-linguistics/akkadian.json', 'data/paleo-linguistics/arabic.json', 'data/paleo-linguistics/aramaic.json', 'data/paleo-linguistics/eblaite.json', 'data/paleo-linguistics/evolution.json', 'data/paleo-linguistics/languages.json', 'data/paleo-linguistics/paleo-hebrew.json', 'data/paleo-linguistics/phoenician.json', 'data/paleo-linguistics/proto-canaanite.json', 'data/paleo-linguistics/ugaritic.json', 'data/prompts/blocks.json', 'data/prompts/index.json', 'data/religionisms/religionisms.json', 'data/research/emuna.json', 'data/research/hesed.json', 'data/research/kadosh.json', 'data/research/korban.json', 'data/research/template.json', 'data/research/teshuva.json', 'data/research/tohu.json', 'data/roots/roots.json', 'data/scripture/bereshit-1.json', 'assets/icons/32/archaeology/lamp.png', 'assets/icons/32/archaeology/testtube.png', 'assets/icons/32/archaeology/vase.png', 'assets/icons/32/crafts/hammer-and-chisel.png', 'assets/icons/32/israel/heart.png', 'assets/icons/32/israel/menorah.png', 'assets/icons/32/nav/alert.png', 'assets/icons/32/nav/door.png', 'assets/icons/32/nav/home.png', 'assets/icons/32/paleo/track.png', 'assets/icons/32/scribe/scroll.png', 'assets/icons/32/scribe/scrolls.png', 'assets/icons/32/seals/ring.png', 'assets/icons/32/temple/torch.png', 'assets/icons/32/ui/anchor.png', 'assets/icons/32/ui/arrows.png', 'assets/icons/32/ui/book.png', 'assets/icons/32/ui/close.png', 'assets/icons/32/ui/download.png', 'assets/icons/32/ui/export.png', 'assets/icons/32/ui/home.png', 'assets/icons/32/ui/hourglass.png', 'assets/icons/32/ui/import.png', 'assets/icons/32/ui/info.png', 'assets/icons/32/ui/keyboard.png', 'assets/icons/32/ui/link.png', 'assets/icons/32/ui/map.png', 'assets/icons/32/ui/moon.png', 'assets/icons/32/ui/question.png', 'assets/icons/32/ui/scales.png', 'assets/icons/32/ui/settings.png', 'assets/icons/32/ui/sun.png', 'assets/icons/32/ui/unload.png', 'assets/icons/32/ui/web.png', 'assets/icons/32/weapons/shield.png', 'assets/icons/32/weapons/sword.png'];

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

  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const networkUpdate = fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.ok) {
          const responseCopy = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseCopy));
        }
        return networkResponse;
      }).catch(() => cachedResponse);

      // Cache First: мгновенно отдаём кэш, затем обновляем его из сети.
      return cachedResponse || networkUpdate;
    })
  );
});
