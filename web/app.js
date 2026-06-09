// Golem Web Interface v8.3 — PC sidebar + Mobile burger + separate file page

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
        render();
    })
    .catch(function(e) {
        console.error('Ошибка загрузки:', e.message);
    });

function buildCategorySelect() {
    var sel = document.getElementById('category-select');
    sel.innerHTML = '<option value="">Все категории</option>';
    var cats = Object.keys(categories).sort();
    for (var i = 0; i < cats.length; i++) {
        var count = FILES.filter(function(f) { return f.category === cats[i]; }).length;
        sel.innerHTML += '<option value="' + cats[i] + '">' + cats[i] + ' (' + count + ')</option>';
    }
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
}

function renderMobile() {
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

    var mlv = document.getElementById('mobile-list-view');
    if (!mlv) {
        mlv = document.createElement('div');
        mlv.id = 'mobile-list-view';
        document.body.appendChild(mlv);
    }

    mlv.innerHTML = '';

    var searchEl = document.getElementById('search');
    var catEl = document.getElementById('category-select');
    var subEl = document.getElementById('subcategory-select');

    mlv.appendChild(searchEl);
    mlv}

    function copyCurrentLink() {
    if (!currentPath) return;
    var u = window.location.origin + (IS_LOCAL ? '/api/file?path=' : '/') + encodeURIComponent(currentPath);
    navigator.clipboard.writeText(u).then(function() { showToast(); });
}