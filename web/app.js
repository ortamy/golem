// web/app.js — Golem Web Interface v9.2 — PC + Mobile, адаптивный, Live Server + Node.js

(function() {
    'use strict';

    var IS_LOCAL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    var API = IS_LOCAL ? '/api/files' : 'files.json';

    var FILES = [],
        currentPath = null,
        bookmarks = JSON.parse(localStorage.getItem('golem_bookmarks') || '[]'),
        fileHistory = JSON.parse(localStorage.getItem('golem_history') || '[]'),
        filteredCache = null;

    function isMobile() { return window.innerWidth <= 768; }

    function $(id) { return document.getElementById(id); }

    function esc(s) {
        var d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    function fetchJSON(url, cb, errCb) {
        fetch(url)
            .then(function(r) { return r.json(); })
            .then(cb)
            .catch(errCb || function(e) { console.error(e); });
    }

    function fetchText(url, cb, errCb) {
        fetch(url)
            .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
            .then(cb)
            .catch(errCb || function(e) { console.error(e); });
    }

    function buildSelects() {
        var categories = {};
        var counts = {};
        FILES.forEach(function(f) {
            categories[f.category] = true;
            counts[f.category] = (counts[f.category] || 0) + 1;
        });
        ['category-select', 'category-select-mobile'].forEach(function(elId) {
            var sel = $(elId);
            if (!sel) return;
            sel.innerHTML = '<option value="">Все категории</option>';
            Object.keys(categories).sort().forEach(function(cat) {
                sel.innerHTML += '<option value="' + esc(cat) + '">' + esc(cat) + ' (' + counts[cat] + ')</option>';
            });
        });
    }

    function getFiltered() {
        if (filteredCache) return filteredCache;
        var m = isMobile();
        var q = m ? $('search-mobile') : $('search');
        var cat = m ? $('category-select-mobile') : $('category-select');
        var sub = m ? $('subcategory-select-mobile') : $('subcategory-select');
        q = q ? q.value.toLowerCase() : '';
        cat = cat ? cat.value : '';
        sub = sub ? sub.value : '';

        var list = FILES;
        if (cat) list = list.filter(function(f) { return f.category === cat; });
        if (sub) list = list.filter(function(f) { return f.subcategory === sub; });
        if (q) list = list.filter(function(f) {
            return (f.title || '').toLowerCase().indexOf(q) >= 0 ||
                   (f.topic || '').toLowerCase().indexOf(q) >= 0 ||
                   (f.path || '').toLowerCase().indexOf(q) >= 0;
        });

        var ss = m ? $('subcategory-select-mobile') : $('subcategory-select');
        if (ss) {
            if (cat) {
                var subs = {};
                FILES.forEach(function(f) {
                    if (f.category === cat && f.subcategory) subs[f.subcategory] = true;
                });
                var sn = Object.keys(subs).sort();
                if (sn.length > 0) {
                    ss.style.display = 'block';
                    ss.innerHTML = '<option value="">Все подкатегории</option>';
                    sn.forEach(function(s) {
                        ss.innerHTML += '<option value="' + esc(s) + '"' + (s === sub ? ' selected' : '') + '>' + esc(s) + '</option>';
                    });
                } else {
                    ss.style.display = 'none';
                    ss.value = '';
                }
            } else {
                ss.style.display = 'none';
                ss.value = '';
            }
        }

        filteredCache = list;
        return list;
    }

    function renderList(container, itemClass, headerClass, clickHandler) {
        if (!container) return;
        container.innerHTML = '';

        var filtered = getFiltered();
        var cc = '';

        filtered.forEach(function(f) {
            if (f.category !== cc) {
                cc = f.category;
                var h = document.createElement('div');
                h.className = headerClass;
                h.textContent = cc;
                container.appendChild(h);
            }
            var d = document.createElement('div');
            d.className = itemClass;
            d.innerHTML = '<div class="title">' + esc(f.title || f.path) + '</div>' +
                (f.topic ? '<div class="topic">' + esc((f.topic || '').substring(0, 90)) + '</div>' : '');
            d.onclick = (function(p) { return function() { clickHandler(p); }; })(f.path);
            container.appendChild(d);
        });

        var statsEl = isMobile() ? $('stats-mobile') : $('total-count');
        if (statsEl) statsEl.textContent = filtered.length;
    }

    function render() {
        filteredCache = null;
        if (isMobile()) {
            var mlv = $('mobile-list-view');
            var items = mlv.querySelectorAll('.file-item-mobile, .cat-header-mobile');
            for (var i = 0; i < items.length; i++) items[i].remove();
            renderList(mlv, 'file-item-mobile', 'cat-header-mobile', openFileMobile);
        } else {
            renderList($('file-list'), 'file-item', 'cat-header', loadFile);
            var tc = $('total-count');
            if (tc) tc.textContent = getFiltered().length;
        }
        renderBookmarks();
        renderHistory();
    }

    function parseMD(t) {
        t = t.replace(/\*\*Метаданные файла\*\*[\s\S]*?(?=\n---|\n# |\n## )/, '');
        var h = t;
        h = h.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
        h = h.replace(/^### (.+)$/gm, '<h3 id="$1">$1</h3>');
        h = h.replace(/^## (.+)$/gm, '<h2 id="$1">$1</h2>');
        h = h.replace(/^# (.+)$/gm, '<h1>$1</h1>');
        h = h.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
        h = h.replace(/`([^`]+)`/g, '<code>$1</code>');
        h = h.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        h = h.replace(/\*(.+?)\*/g, '<em>$1</em>');
        h = h.replace(/^---$/gm, '<hr>');
        h = h.replace(/\n\n/g, '</p><p>');
        h = '<p>' + h + '</p>';
        return h.replace(/<p><\/p>/g, '');
    }

    function loadFile(p) {
        currentPath = p;
        var c = $('content');
        c.classList.remove('fade-in');
        c.innerHTML = '<div class="spinner"></div>';
        var url = IS_LOCAL ? '/api/file?path=' + encodeURIComponent(p) : p;
        fetchText(url, function(md) {
            var isBm = bookmarks.indexOf(p) >= 0;
            c.innerHTML = '<div class="path-hint">' + esc(p) +
                ' <span class="bookmark-btn' + (isBm ? ' active' : '') +
                '" onclick="toggleBookmark(\'' + p.replace(/'/g, "\\'") + '\')">' +
                (isBm ? '★' : '☆') + '</span></div>' +
                parseMD(md) + renderRelated(p);
            addToHistory(p);
            buildTOC(md);
            setupQuoteCopy();
            void c.offsetWidth;
            c.classList.add('fade-in');
        }, function() {
            c.innerHTML = '<div style="color:#ff4d00;padding:40px;">Ошибка: ' + esc(p) + '</div>';
        });
    }

    function openFileMobile(p) {
        currentPath = p;
        $('file-page').style.display = 'block';
        $('file-path-hint').textContent = p;
        var bm = $('file-bookmark-btn');
        var isBm = bookmarks.indexOf(p) >= 0;
        bm.textContent = isBm ? '★' : '☆';
        bm.className = 'bookmark-btn' + (isBm ? ' active' : '');
        bm.onclick = function() { toggleBookmark(p); };
        $('mobile-list-view').style.display = 'none';
        $('stats-mobile').style.display = 'none';

        var c = $('file-content-mobile');
        c.innerHTML = '<div class="spinner"></div>';
        var url = IS_LOCAL ? '/api/file?path=' + encodeURIComponent(p) : p;
        fetchText(url, function(md) {
            c.innerHTML = parseMD(md) + renderRelatedMobile(p);
            addToHistory(p);
        }, function() {
            c.innerHTML = '<div style="color:#ff4d00;padding:40px;">Ошибка: ' + esc(p) + '</div>';
        });
    }

    function closeFile() {
        $('file-page').style.display = 'none';
        $('mobile-list-view').style.display = 'block';
        $('stats-mobile').style.display = 'block';
        currentPath = null;
        render();
    }

    function buildTOC(md) {
        var pn = $('toc-panel'), ls = $('toc-list');
        var hd = md.match(/^#{2,3} (.+)$/gm);
        if (!hd || hd.length < 2) { pn.style.display = 'none'; return; }
        pn.style.display = 'block';
        ls.innerHTML = '';
        hd.forEach(function(h) {
            var lv = h.indexOf('### ') === -1 ? 'h2' : 'h3';
            var tt = h.replace(/^#{2,3} /, '').trim();
            var d = document.createElement('div');
            d.className = 'toc-item ' + lv;
            d.textContent = tt;
            d.onclick = function() { var el = $(tt); if (el) el.scrollIntoView({ behavior: 'smooth' }); };
            ls.appendChild(d);
        });
    }

    function renderLinks(p, clickFn) {
        var f = FILES.find(function(x) { return x.path === p; });
        if (!f || !f.related || !f.related.length) return '';
        var h = '<hr><h3>Связанные файлы</h3><ul>';
        f.related.forEach(function(r) {
            var rf = FILES.find(function(x) { return x.path === r; });
            var tt = rf ? (rf.title || r) : r;
            h += '<li><span class="related-link" onclick="' + clickFn.name + '(\'' + r.replace(/'/g, "\\'") + '\')">' + esc(tt) + '</span></li>';
        });
        return h + '</ul>';
    }

    function renderRelated(p) { return renderLinks(p, loadFile); }
    function renderRelatedMobile(p) { return renderLinks(p, openFileMobile); }

    function setupQuoteCopy() {
        var qs = document.querySelectorAll('#content blockquote');
        for (var i = 0; i < qs.length; i++) {
            qs[i].onclick = function() {
                navigator.clipboard.writeText(this.textContent.trim()).then(showToast);
            };
        }
    }

    function showToast() {
        var t = $('copy-toast');
        t.classList.add('show');
        setTimeout(function() { t.classList.remove('show'); }, 1500);
    }

    function toggleBookmark(p) {
        if (!p) return;
        var i = bookmarks.indexOf(p);
        if (i >= 0) bookmarks.splice(i, 1);
        else bookmarks.push(p);
        localStorage.setItem('golem_bookmarks', JSON.stringify(bookmarks));
        if (isMobile()) {
            var bm = $('file-bookmark-btn');
            var isBm = bookmarks.indexOf(p) >= 0;
            bm.textContent = isBm ? '★' : '☆';
            bm.className = 'bookmark-btn' + (isBm ? ' active' : '');
        } else {
            loadFile(p);
        }
    }

    function addToHistory(p) {
        fileHistory = fileHistory.filter(function(h) { return h !== p; });
        fileHistory.unshift(p);
        if (fileHistory.length > 15) fileHistory.pop();
        localStorage.setItem('golem_history', JSON.stringify(fileHistory));
    }

    function renderBookmarks() {
        var bl = $('bookmarks-list'), bm = $('burger-bookmarks-list');
        [bl, bm].forEach(function(list) {
            if (!list) return;
            list.innerHTML = '';
            bookmarks.forEach(function(p) {
                var d = document.createElement('div');
                d.className = 'bookmark-item';
                var bf = FILES.find(function(x) { return x.path === p; });
                d.textContent = bf ? (bf.title || p) : p;
                d.onclick = function() { if (isMobile()) openFileMobile(p); else loadFile(p); };
                list.appendChild(d);
            });
        });
        var bs = $('bookmarks-section');
        if (bs) bs.style.display = bookmarks.length ? 'block' : 'none';
    }

    function renderHistory() {
        var hl = $('history-list'), bh = $('burger-history-list');
        [hl, bh].forEach(function(list) {
            if (!list) return;
            list.innerHTML = '';
            fileHistory.slice(0, 8).forEach(function(p) {
                var d = document.createElement('div');
                d.className = 'history-item';
                var f = FILES.find(function(x) { return x.path === p; });
                d.textContent = (f ? f.title : p || '').substring(0, 40);
                d.onclick = function() { if (isMobile()) openFileMobile(p); else loadFile(p); };
                list.appendChild(d);
            });
        });
        var hs = $('history-section');
        if (hs) hs.style.display = fileHistory.length ? 'block' : 'none';
    }

    function toggleBurger() {
        $('burger-menu').classList.toggle('open');
        $('burger-overlay').classList.toggle('show');
    }

    function closeBurger() {
        $('burger-menu').classList.remove('open');
        $('burger-overlay').classList.remove('show');
    }

    function randomFile() {
        if (!FILES.length) return;
        closeBurger();
        var p = FILES[Math.floor(Math.random() * FILES.length)].path;
        if (isMobile()) openFileMobile(p); else loadFile(p);
    }

    function copyCurrentLink() {
        if (!currentPath) return;
        var u = window.location.origin + (IS_LOCAL ? '/api/file?path=' : '/') + encodeURIComponent(currentPath);
        navigator.clipboard.writeText(u).then(showToast);
    }

    function toggleTheme() {
        var b = document.body;
        var isLight = b.classList.contains('light');
        b.classList.toggle('light', !isLight);
        b.classList.toggle('dark', isLight);
        localStorage.setItem('golem_theme', isLight ? 'dark' : 'light');
    }

    // Init
    if (localStorage.getItem('golem_theme') === 'dark') {
        document.body.classList.remove('light');
        document.body.classList.add('dark');
    }

    window.addEventListener('scroll', function() {
        var bt = $('back-to-top');
        if (bt) bt.style.display = window.scrollY > 400 ? 'flex' : 'none';
    });

    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
        var m = isMobile();
        if (e.key === '/') {
            var s = m ? $('search-mobile') : $('search');
            if (s) s.focus();
            e.preventDefault();
        }
        if (e.key === 'Escape') {
            if (m && currentPath) closeFile();
            else { var s2 = m ? $('search-mobile') : $('search'); if (s2) s2.blur(); }
        }
        if (e.key === 'b' && currentPath) toggleBookmark(currentPath);
        if (e.key === 'r') randomFile();
    });

    // Глобальные функции для onclick в HTML
    window.toggleTheme = toggleTheme;
    window.toggleBurger = toggleBurger;
    window.closeBurger = closeBurger;
    window.randomFile = randomFile;
    window.copyCurrentLink = copyCurrentLink;
    window.toggleBookmark = toggleBookmark;
    window.closeFile = closeFile;
    window.render = render;

    // Старт
    fetchJSON(API, function(data) {
        FILES = data;
        buildSelects();
        render();
    }, function(e) {
        console.error('Ошибка загрузки:', e.message);
        var el = isMobile() ? $('mobile-list-view') : $('file-list');
        if (el) el.innerHTML = '<div style="padding:20px;color:#ff4d00;">Ошибка загрузки данных.</div>';
    });
})();