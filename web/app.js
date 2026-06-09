// Golem Web Interface v8.3 — PC + Mobile

var IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
var API_FILES = IS_LOCAL ? '/api/files' : 'files.json';
var IS_MOBILE = window.innerWidth <= 768;

var FILES = [],
    currentPath = null,
    bookmarks = JSON.parse(localStorage.getItem('golem_bookmarks') || '[]'),
    fileHistory = JSON.parse(localStorage.getItem('golem_history') || '[]'),
    categories = {};

fetch(API_FILES)
    .then(function(r) { return r.json(); })
    .then(function(data) {
        FILES = data;
        for (var i = 0; i < FILES.length; i++) {
            categories[FILES[i].category] = true;
        }
        buildCategorySelect();
        if (IS_MOBILE) buildMobileCategorySelect();
        render();
    })
    .catch(function(e) {
        console.error('Ошибка загрузки:', e.message);
    });

function buildCategorySelect() {
    var sel = document.getElementById('category-select');
    if (!sel) return;
    sel.innerHTML = '<option value="">Все категории</option>';
    var cats = Object.keys(categories).sort();
    for (var i = 0; i < cats.length; i++) {
        var count = FILES.filter(function(f) { return f.category === cats[i]; }).length;
        sel.innerHTML += '<option value="' + cats[i] + '">' + cats[i] + ' (' + count + ')</option>';
    }
}

function buildMobileCategorySelect() {
    var sel = document.getElementById('category-select-mobile');
    if (!sel) return;
    sel.innerHTML = '<option value="">Все категории</option>';
    var cats = Object.keys(categories).sort();
    for (var i = 0; i < cats.length; i++) {
        var count = FILES.filter(function(f) { return f.category === cats[i]; }).length;
        sel.innerHTML += '<option value="' + cats[i] + '">' + cats[i] + ' (' + count + ')</option>';
    }
}

function getSearchValue() {
    var el = IS_MOBILE ? document.getElementById('search-mobile') : document.getElementById('search');
    return el ? el.value.toLowerCase() : '';
}

function getCategoryValue() {
    var el = IS_MOBILE ? document.getElementById('category-select-mobile') : document.getElementById('category-select');
    return el ? el.value : '';
}

function getSubcategoryValue() {
    var el = IS_MOBILE ? document.getElementById('subcategory-select-mobile') : document.getElementById('subcategory-select');
    return el ? el.value : '';
}

function getSubcategoryEl() {
    return IS_MOBILE ? document.getElementById('subcategory-select-mobile') : document.getElementById('subcategory-select');
}

function render() {
    if (IS_MOBILE) {
        renderMobile();
        return;
    }
    renderDesktop();
}

function renderDesktop() {
    var q = document.getElementById('search').value.toLowerCase();
    var cat = document.getElementById('category-select').value;
    var sub = document.getElementById('subcategory-select').value;

    var filtered = FILES;
    if (cat) filtered = filtered.filter(function(f) { return f.category === cat; });
    if (sub) filtered = filtered.filter(function(f) { return f.subcategory === sub; });
    if (q) filtered = filtered.filter(function(f) {
        return (f.title || '').toLowerCase().indexOf(q) >= 0 ||
               (f.topic || '').toLowerCase().indexOf(q) >= 0 ||
               (f.path || '').toLowerCase().indexOf(q) >= 0;
    });

    var ss = document.getElementById('subcategory-select');
    if (cat === 'Исследования') {
        ss.style.display = 'block';
        var subs = {};
        for (var i = 0; i < FILES.length; i++) {
            if (FILES[i].category === 'Исследования' && FILES[i].subcategory) {
                subs[FILES[i].subcategory] = true;
            }
        }
        var sn = Object.keys(subs).sort();
        ss.innerHTML = '<option value="">Все подкатегории</option>';
        for (var j = 0; j < sn.length; j++) {
            var s = (sn[j] === sub) ? ' selected' : '';
            ss.innerHTML += '<option value="' + sn[j] + '"' + s + '>' + sn[j] + '</option>';
        }
    } else {
        ss.style.display = 'none';
        ss.value = '';
    }

    var list = document.getElementById('file-list');
    list.innerHTML = '';
    document.getElementById('total-count').textContent = filtered.length;

    var cc = '';
    for (var i = 0; i < filtered.length; i++) {
        var f = filtered[i];
        if (f.category !== cc) {
            cc = f.category;
            var h = document.createElement('div');
            h.className = 'cat-header';
            h.textContent = cc;
            list.appendChild(h);
        }
        var d = document.createElement('div');
        d.className = 'file-item';
        if (f.path === currentPath) d.classList.add('active');
        d.innerHTML = '<div class="title">' + esc(f.title || f.path) + '</div>' +
            (f.topic ? '<div class="topic">' + esc((f.topic || '').substring(0, 90)) + '</div>' : '');
        d.onclick = (function(p) { return function() { loadFile(p); }; })(f.path);
        list.appendChild(d);
    }

    var bS = document.getElementById('bookmarks-section'),
        bL = document.getElementById('bookmarks-list');
    if (bookmarks.length) {
        bS.style.display = 'block';
        bL.innerHTML = '';
        for (var j = 0; j < bookmarks.length; j++) {
            (function(p) {
                var bd = document.createElement('div');
                bd.className = 'bookmark-item';
                var bf = FILES.find(function(x) { return x.path === p; });
                bd.textContent = bf ? (bf.title || p) : p;
                bd.onclick = function() { loadFile(p); };
                bL.appendChild(bd);
            })(bookmarks[j]);
        }
    } else {
        bS.style.display = 'none';
    }
    renderHistory();
    renderBurgerBookmarks();
    renderBurgerHistory();
}

function renderMobile() {
    var q = getSearchValue();
    var cat = getCategoryValue();
    var sub = getSubcategoryValue();

    var filtered = FILES;
    if (cat) filtered = filtered.filter(function(f) { return f.category === cat; });
    if (sub) filtered = filtered.filter(function(f) { return f.subcategory === sub; });
    if (q) filtered = filtered.filter(function(f) {
        return (f.title || '').toLowerCase().indexOf(q) >= 0 ||
               (f.topic || '').toLowerCase().indexOf(q) >= 0 ||
               (f.path || '').toLowerCase().indexOf(q) >= 0;
    });

    var ss = getSubcategoryEl();
    if (ss) {
        if (cat === 'Исследования') {
            ss.style.display = 'block';
            var subs = {};
            for (var i = 0; i < FILES.length; i++) {
                if (FILES[i].category === 'Исследования' && FILES[i].subcategory) {
                    subs[FILES[i].subcategory] = true;
                }
            }
            var sn = Object.keys(subs).sort();
            ss.innerHTML = '<option value="">Все подкатегории</option>';
            for (var j = 0; j < sn.length; j++) {
                var s = (sn[j] === sub) ? ' selected' : '';
                ss.innerHTML += '<option value="' + sn[j] + '"' + s + '>' + sn[j] + '</option>';
            }
        } else {
            ss.style.display = 'none';
            ss.value = '';
        }
    }

    var mlv = document.getElementById('mobile-list-view');
    mlv.innerHTML = '';

    var searchEl = document.getElementById('search-mobile');
    var catEl = document.getElementById('category-select-mobile');
    var subEl = document.getElementById('subcategory-select-mobile');

    mlv.appendChild(searchEl);
    mlv.appendChild(catEl);
    mlv.appendChild(subEl);

    document.getElementById('stats-mobile').textContent = 'Файлов: ' + filtered.length;

    var cc = '';
    for (var i = 0; i < filtered.length; i++) {
        var f = filtered[i];
        if (f.category !== cc) {
            cc = f.category;
            var h = document.createElement('div');
            h.className = 'cat-header-mobile';
            h.textContent = cc;
            mlv.appendChild(h);
        }
        var d = document.createElement('div');
        d.className = 'file-item-mobile';
        d.innerHTML = '<div class="title">' + esc(f.title || f.path) + '</div>' +
            (f.topic ? '<div class="topic">' + esc((f.topic || '').substring(0, 90)) + '</div>' : '');
        d.onclick = (function(p) { return function() { openFileMobile(p); }; })(f.path);
        mlv.appendChild(d);
    }

    renderBurgerBookmarks();
    renderBurgerHistory();
}

function loadFile(p) {
    currentPath = p;
    var c = document.getElementById('content');
    c.classList.remove('fade-in');
    c.innerHTML = '<div class="spinner"></div>';

    var url = IS_LOCAL ? '/api/file?path=' + encodeURIComponent(p) : p;

    fetch(url)
        .then(function(r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
        })
        .then(function(md) {
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
        })
        .catch(function(e) {
            c.innerHTML = '<div style="color:#ff4d00;padding:40px;">Ошибка: ' + esc(p) + '</div>';
        });
}

function openFileMobile(p) {
    currentPath = p;
    var fp = document.getElementById('file-page');
    fp.style.display = 'block';
    document.getElementById('file-path-hint').textContent = p;
    var bm = document.getElementById('file-bookmark-btn');
    bm.textContent = bookmarks.indexOf(p) >= 0 ? '★' : '☆';
    bm.className = 'bookmark-btn' + (bookmarks.indexOf(p) >= 0 ? ' active' : '');
    document.getElementById('mobile-list-view').style.display = 'none';
    document.getElementById('stats-mobile').style.display = 'none';

    var c = document.getElementById('file-content-mobile');
    c.innerHTML = '<div class="spinner"></div>';

    var url = IS_LOCAL ? '/api/file?path=' + encodeURIComponent(p) : p;

    fetch(url)
        .then(function(r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
        })
        .then(function(md) {
            c.innerHTML = parseMD(md) + renderRelatedMobile(p);
            addToHistory(p);
        })
        .catch(function(e) {
            c.innerHTML = '<div style="color:#ff4d00;padding:40px;">Ошибка: ' + esc(p) + '</div>';
        });
}

function closeFile() {
    document.getElementById('file-page').style.display = 'none';
    document.getElementById('mobile-list-view').style.display = 'block';
    document.getElementById('stats-mobile').style.display = 'block';
    currentPath = null;
    renderMobile();
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
    h = h.replace(/<p><\/p>/g, '');
    return h;
}

function buildTOC(md) {
    var pn = document.getElementById('toc-panel'),
        ls = document.getElementById('toc-list');
    var hd = md.match(/^#{2,3} (.+)$/gm);
    if (!hd || hd.length < 2) { pn.style.display = 'none'; return; }
    pn.style.display = 'block';
    ls.innerHTML = '';
    for (var i = 0; i < hd.length; i++) {
        var h = hd[i],
            lv = h.indexOf('### ') === -1 ? 'h2' : 'h3',
            tt = h.replace(/^#{2,3} /, '').trim();
        var d = document.createElement('div');
        d.className = 'toc-item ' + lv;
        d.textContent = tt;
        (function(t) {
            d.onclick = function() {
                var el = document.getElementById(t);
                if (el) el.scrollIntoView({ behavior: 'smooth' });
            };
        })(tt);
        ls.appendChild(d);
    }
}

function renderRelated(p) {
    var f = FILES.find(function(x) { return x.path === p; });
    if (!f || !f.related || !f.related.length) return '';
    var h = '<hr><h3>Связанные файлы</h3><ul>';
    for (var i = 0; i < f.related.length; i++) {
        var r = f.related[i],
            rf = FILES.find(function(x) { return x.path === r; }),
            tt = rf ? (rf.title || r) : r;
        h += '<li><span class="related-link" onclick="loadFile(\'' + r.replace(/'/g, "\\'") + '\')">' + esc(tt) + '</span></li>';
    }
    return h + '</ul>';
}

function renderRelatedMobile(p) {
    var f = FILES.find(function(x) { return x.path === p; });
    if (!f || !f.related || !f.related.length) return '';
    var h = '<hr><h3>Связанные файлы</h3><ul>';
    for (var i = 0; i < f.related.length; i++) {
        var r = f.related[i],
            rf = FILES.find(function(x) { return x.path === r; }),
            tt = rf ? (rf.title || r) : r;
        h += '<li><span class="related-link" onclick="openFileMobile(\'' + r.replace(/'/g, "\\'") + '\')">' + esc(tt) + '</span></li>';
    }
    return h + '</ul>';
}

function setupQuoteCopy() {
    var qs = document.querySelectorAll('#content blockquote');
    for (var i = 0; i < qs.length; i++) {
        qs[i].onclick = function() {
            navigator.clipboard.writeText(this.textContent.trim()).then(function() { showToast(); });
        };
    }
}

function showToast() {
    var t = document.getElementById('copy-toast');
    t.classList.add('show');
    setTimeout(function() { t.classList.remove('show'); }, 1500);
}

function toggleBookmark(p) {
    if (!p) return;
    var i = bookmarks.indexOf(p);
    if (i >= 0) bookmarks.splice(i, 1);
    else bookmarks.push(p);
    localStorage.setItem('golem_bookmarks', JSON.stringify(bookmarks));
    if (IS_MOBILE) {
        var bm = document.getElementById('file-bookmark-btn');
        bm.textContent = bookmarks.indexOf(p) >= 0 ? '★' : '☆';
        bm.className = 'bookmark-btn' + (bookmarks.indexOf(p) >= 0 ? ' active' : '');
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

function renderHistory() {
    var ct = document.getElementById('sidebar-footer'),
        old = document.getElementById('history-section');
    if (old) old.remove();
    if (!fileHistory.length) return;
    var s = document.createElement('div');
    s.id = 'history-section';
    s.innerHTML = '<div class="cat-header">История</div>';
    for (var i = 0; i < Math.min(fileHistory.length, 8); i++) {
        (function(p) {
            var d = document.createElement('div');
            d.className = 'history-item';
            var f = FILES.find(function(x) { return x.path === p; });
            var t = p || '';
            if (f && f.title) t = f.title;
            d.textContent = t.substring(0, 40);
            d.onclick = function() { loadFile(p); };
            s.appendChild(d);
        })(fileHistory[i]);
    }
    ct.insertBefore(s, document.getElementById('stats'));
}

function renderBurgerBookmarks() {
    var list = document.getElementById('burger-bookmarks-list');
    if (!list) return;
    list.innerHTML = '';
    for (var j = 0; j < bookmarks.length; j++) {
        (function(p) {
            var d = document.createElement('div');
            d.className = 'bookmark-item';
            var bf = FILES.find(function(x) { return x.path === p; });
            d.textContent = bf ? (bf.title || p) : p;
            d.onclick = function() { closeBurger(); if (IS_MOBILE) openFileMobile(p); else loadFile(p); };
            list.appendChild(d);
        })(bookmarks[j]);
    }
}

function renderBurgerHistory() {
    var list = document.getElementById('burger-history-list');
    if (!list) return;
    list.innerHTML = '';
    for (var i = 0; i < Math.min(fileHistory.length, 8); i++) {
        (function(p) {
            var d = document.createElement('div');
            d.className = 'history-item';
            var f = FILES.find(function(x) { return x.path === p; });
            var t = p || '';
            if (f && f.title) t = f.title;
            d.textContent = t.substring(0, 40);
            d.onclick = function() { closeBurger(); if (IS_MOBILE) openFileMobile(p); else loadFile(p); };
            list.appendChild(d);
        })(fileHistory[i]);
    }
}

function toggleBurger() {
    document.getElementById('burger-menu').classList.toggle('open');
    document.getElementById('burger-overlay').classList.toggle('show');
}

function closeBurger() {
    document.getElementById('burger-menu').classList.remove('open');
    document.getElementById('burger-overlay').classList.remove('show');
}

function randomFile() {
    if (!FILES.length) return;
    closeBurger();
    var p = FILES[Math.floor(Math.random() * FILES.length)].path;
    if (IS_MOBILE) openFileMobile(p);
    else loadFile(p);
}

function copyCurrentLink() {
    if (!currentPath) return;
    var u = window.location.origin + (IS_LOCAL ? '/api/file?path=' : '/') + encodeURIComponent(currentPath);
    navigator.clipboard.writeText(u).then(function() { showToast(); });
}

function toggleTheme() {
    var b = document.body;
    if (b.classList.contains('light')) {
        b.classList.remove('light');
        b.classList.add('dark');
        localStorage.setItem('golem_theme', 'dark');
    } else {
        b.classList.remove('dark');
        b.classList.add('light');
        localStorage.setItem('golem_theme', 'light');
    }
}

(function() {
    if (localStorage.getItem('golem_theme') === 'dark') {
        document.body.classList.remove('light');
        document.body.classList.add('dark');
    }
})();

window.addEventListener('scroll', function() {
    var bt = document.getElementById('back-to-top');
    if (bt) bt.style.display = window.scrollY > 400 ? 'flex' : 'none';
});

document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    if (e.key === '/') {
        var s = IS_MOBILE ? document.getElementById('search-mobile') : document.getElementById('search');
        if (s) s.focus();
        e.preventDefault();
    }
    if (e.key === 'Escape') {
        if (IS_MOBILE && currentPath) closeFile();
        else {
            var s = IS_MOBILE ? document.getElementById('search-mobile') : document.getElementById('search');
            if (s) s.blur();
        }
    }
    if (e.key === 'b' && currentPath) toggleBookmark(currentPath);
    if (e.key === 'r') randomFile();
});

function esc(s) {
    var d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
}