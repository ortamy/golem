# tools/generators/generate-web.py — web
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import print_header, print_success, print_hint, REPO_ROOT

OUTPUT_DIR = REPO_ROOT / "docs" / "web"


def generate():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print_header("ГЕНЕРАЦИЯ ВЕБ-ИНТЕРФЕЙСА ДЛЯ NODE.JS", "🌐")

    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # index.html
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Golem — Свидетель Истины</title>
<link rel="stylesheet" href="style.css">
</head>
<body class="light">

<div id="sidebar">
    <div id="logo"><pre>
 ██████╗  ██████╗ ██╗     ███████╗███╗   ███╗
██╔════╝ ██╔═══██╗██║     ██╔════╝████╗ ████║
██║  ███╗██║   ██║██║     █████╗  ██╔████╔██║
██║   ██║██║   ██║██║     ██╔══╝  ██║╚██╔╝██║
╚██████╔╝╚██████╔╝███████╗███████╗██║ ╚═╝ ██║
 ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝
    </pre></div>
    <div id="filters">
        <input type="text" id="search" placeholder="Поиск..." oninput="render()">
        <select id="category-select" onchange="render()">
            <option value="">Все категории</option>
        </select>
        <select id="subcategory-select" onchange="render()" style="display:none;margin-top:6px">
            <option value="">Все подкатегории</option>
        </select>
        <div id="toggle-theme" onclick="toggleTheme()" title="Тёмная/светлая тема">◐</div>
    </div>
    <div id="sidebar-actions">
        <span class="sidebar-btn" onclick="randomFile()">Случайный</span>
        <span class="sidebar-btn" onclick="copyCurrentLink()">Копировать ссылку</span>
        <span class="sidebar-btn" onclick="window.print()">Печать</span>
    </div>
    <div id="file-list"></div>
    <div id="sidebar-footer">
        <div id="bookmarks-section" style="display:none">
            <div class="cat-header">Закладки</div>
            <div id="bookmarks-list"></div>
        </div>
        <div id="stats">Файлов: <span id="total-count">0</span> &nbsp;|&nbsp; {today}</div>
    </div>
</div>

<div id="main-area">
    <div id="content">
        <div id="empty">&larr; Выберите файл</div>
    </div>
    <div id="toc-panel" style="display:none">
        <div class="toc-header">Содержание</div>
        <div id="toc-list"></div>
    </div>
</div>

<button id="back-to-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<div id="copy-toast">Скопировано</div>

<script src="app.js"></script>
</body>
</html>'''

    with open(OUTPUT_DIR / "index.html", 'w', encoding='utf-8') as f:
        f.write(html)

    # style.css
    css = '''* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Courier New', monospace; display: flex; height: 100vh; }
body.light { background: #fff; color: #111; }
body.dark { background: #1a1a1a; color: #ddd; }

#sidebar { width: 320px; min-width: 320px; display: flex; flex-direction: column; overflow: hidden; }
body.light #sidebar { background: #fff; border-right: 1px solid #111; }
body.dark #sidebar { background: #1a1a1a; border-right: 1px solid #444; }

#logo { padding: 16px 20px 12px; }
body.light #logo { border-bottom: 1px solid #111; }
body.dark #logo { border-bottom: 1px solid #444; }
#logo pre { font-size: 10px; line-height: 1.4; font-weight: 700; margin: 0; font-family: 'Courier New', monospace; }
body.light #logo pre { color: #111; }
body.dark #logo pre { color: #ff4d00; }

#filters { padding: 10px 20px; position: relative; }
body.light #filters { border-bottom: 1px solid #111; }
body.dark #filters { border-bottom: 1px solid #444; }
#search, #category-select, #subcategory-select { width: 100%; padding: 8px 10px; font-family: 'Courier New', monospace; font-size: 11px; outline: none; }
body.light #search, body.light #category-select, body.light #subcategory-select { background: #fff; border: 1px solid #ccc; color: #111; }
body.dark #search, body.dark #category-select, body.dark #subcategory-select { background: #222; border: 1px solid #444; color: #ddd; }
#search:focus, #category-select:focus, #subcategory-select:focus { border-color: #ff4d00; }
#search::placeholder { color: #999; }
#category-select { margin-top: 6px; }
#subcategory-select { margin-top: 6px; display: none; }
#toggle-theme { position: absolute; right: 20px; top: 14px; cursor: pointer; font-size: 18px; user-select: none; }

#sidebar-actions { padding: 8px 20px; display: flex; gap: 12px; }
body.light #sidebar-actions { border-bottom: 1px solid #111; }
body.dark #sidebar-actions { border-bottom: 1px solid #444; }
.sidebar-btn { font-size: 9px; cursor: pointer; color: #999; text-transform: uppercase; letter-spacing: 1px; user-select: none; }
.sidebar-btn:hover { color: #ff4d00; }

#file-list { flex: 1; overflow-y: auto; }
.file-item { padding: 7px 20px; cursor: pointer; font-size: 11px; transition: background 0.1s; border-left: 2px solid transparent; }
body.light .file-item { border-bottom: 1px solid #eee; }
body.dark .file-item { border-bottom: 1px solid #2a2a2a; }
.file-item:hover { background: #fafafa; }
body.dark .file-item:hover { background: #222; }
.file-item.active { border-left: 2px solid #ff4d00; }
body.light .file-item.active { background: #fafafa; }
body.dark .file-item.active { background: #222; }
.file-item .title { font-weight: 600; }
body.dark .file-item .title { color: #ddd; }
.file-item .topic { font-size: 10px; margin-top: 2px; }
body.light .file-item .topic { color: #999; }
body.dark .file-item .topic { color: #777; }

.cat-header { padding: 10px 20px 4px; font-size: 9px; color: #ff4d00; text-transform: uppercase; letter-spacing: 3px; font-weight: 700; }
body.light .cat-header { border-bottom: 1px solid #111; }
body.dark .cat-header { border-bottom: 1px solid #444; }

#stats { padding: 10px 20px; font-size: 9px; letter-spacing: 1px; text-transform: uppercase; }
body.light #stats { border-top: 1px solid #111; color: #999; }
body.dark #stats { border-top: 1px solid #444; color: #777; }
#stats span { color: #ff4d00; font-weight: 700; }

#main-area { flex: 1; display: flex; overflow: hidden; position: relative; }
#content { flex: 1; overflow-y: auto; padding: 30px 40px 60px; }
body.light #content { background: #fff; }
body.dark #content { background: #1a1a1a; }

#content h1 { font-size: 26px; margin-bottom: 8px; font-weight: 300; letter-spacing: 2px; padding-bottom: 10px; }
body.light #content h1 { color: #111; border-bottom: 1px solid #111; }
body.dark #content h1 { color: #ff4d00; border-bottom: 1px solid #444; }
#content h2 { font-size: 15px; margin: 24px 0 6px; font-weight: 600; }
body.light #content h2 { color: #111; }
body.dark #content h2 { color: #ddd; }
#content h3 { font-size: 13px; margin: 18px 0 4px; font-weight: 600; }
body.light #content h3 { color: #333; }
body.dark #content h3 { color: #bbb; }
#content p { line-height: 1.7; margin-bottom: 8px; font-size: 13px; }
body.dark #content p { color: #ccc; }
#content blockquote { border-left: 2px solid #ff4d00; padding: 8px 14px; margin: 12px 0; font-style: italic; cursor: pointer; transition: background 0.15s; }
body.light #content blockquote { background: #fafafa; color: #555; }
body.dark #content blockquote { background: #222; color: #aaa; }
#content blockquote:hover { background: #fff3e0; }
body.dark #content blockquote:hover { background: #2a2a2a; }
#content blockquote.copied { background: #e8f5e9 !important; }
body.dark #content blockquote.copied { background: #1a3a1a !important; }
#content code { padding: 1px 5px; font-size: 11px; color: #ff4d00; }
body.light #content code { background: #f5f5f5; }
body.dark #content code { background: #222; }
#content strong { color: #ff4d00; font-weight: 700; }
#content em { font-style: italic; }
body.light #content em { color: #555; }
body.dark #content em { color: #999; }
#content hr { border: none; margin: 16px 0; }
body.light #content hr { border-top: 1px solid #111; }
body.dark #content hr { border-top: 1px solid #444; }
#content a { color: #ff4d00; text-decoration: none; border-bottom: 1px solid #ff4d00; }
#content ul, #content ol { margin: 6px 0 6px 18px; }
#content li { line-height: 1.6; font-size: 13px; margin-bottom: 3px; }
body.dark #content li { color: #ccc; }
.related-link { cursor: pointer; color: #ff4d00; border-bottom: 1px solid #ff4d00; }
.related-link:hover { opacity: 0.7; }

#empty { display: flex; align-items: center; justify-content: center; height: 100%; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; }
body.light #empty { color: #ccc; }
body.dark #empty { color: #555; }

.path-hint { font-size: 9px; margin-bottom: 12px; letter-spacing: 1px; text-transform: uppercase; }
body.light .path-hint { color: #ccc; }
body.dark .path-hint { color: #555; }

.spinner { border: 2px solid #f3f3f3; border-top: 2px solid #ff4d00; border-radius: 50%; width: 20px; height: 20px; animation: spin 0.8s linear infinite; margin: 40px auto; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.bookmark-btn { cursor: pointer; color: #ccc; font-size: 14px; user-select: none; margin-left: 8px; }
.bookmark-btn.active { color: #ff4d00; }
.bookmark-item { font-size: 10px; padding: 4px 20px; cursor: pointer; color: #ff4d00; }
.bookmark-item:hover { text-decoration: underline; }
.history-item { font-size: 10px; padding: 4px 20px; cursor: pointer; color: #999; display: block; }
.history-item:hover { color: #ff4d00; }

#toc-panel { width: 200px; min-width: 200px; overflow-y: auto; padding: 16px; }
body.light #toc-panel { border-left: 1px solid #eee; background: #fafafa; }
body.dark #toc-panel { border-left: 1px solid #333; background: #1e1e1e; }
.toc-header { font-size: 10px; color: #ff4d00; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; margin-bottom: 10px; }
.toc-item { font-size: 11px; padding: 2px 0; cursor: pointer; display: block; }
body.light .toc-item { color: #555; }
body.dark .toc-item { color: #999; }
.toc-item:hover { color: #ff4d00; }
.toc-item.h3 { padding-left: 10px; font-size: 10px; }

.hebrew { font-family: 'Times New Roman', serif; font-size: 15px; direction: rtl; }

#back-to-top { position: fixed; bottom: 20px; right: 20px; width: 32px; height: 32px; background: #ff4d00; color: #fff; border: none; cursor: pointer; font-size: 16px; display: none; align-items: center; justify-content: center; font-family: 'Courier New', monospace; z-index: 99; }
#back-to-top:hover { opacity: 0.8; }

#copy-toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #111; color: #fff; padding: 8px 16px; font-size: 11px; letter-spacing: 1px; opacity: 0; transition: opacity 0.3s; pointer-events: none; z-index: 999; }
body.dark #copy-toast { background: #fff; color: #111; }
#copy-toast.show { opacity: 1; }

@media (max-width: 768px) { #sidebar { width: 260px; min-width: 260px; } #content { padding: 20px 24px; } #toc-panel { display: none !important; } }
'''

    with open(OUTPUT_DIR / "style.css", 'w', encoding='utf-8') as f:
        f.write(css)

    # app.js
    js = '''// Golem Web Interface v8.0 — Node.js dynamic

var FILES = [],
    currentPath = null,
    bookmarks = JSON.parse(localStorage.getItem('golem_bookmarks') || '[]'),
    history = JSON.parse(localStorage.getItem('golem_history') || '[]'),
    categories = {};

fetch('/api/files')
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
        document.getElementById('file-list').innerHTML =
            '<div style="padding:20px;color:#ff4d00;font-size:11px;">Ошибка загрузки. Запустите сервер:<br><code>node server.js</code></div>';
    });

function buildCategorySelect() {
    var sel = document.getElementById('category-select');
    var cats = Object.keys(categories).sort();
    for (var i = 0; i < cats.length; i++) {
        var count = FILES.filter(function(f) { return f.category === cats[i]; }).length;
        sel.innerHTML += '<option value="' + cats[i] + '">' + cats[i] + ' (' + count + ')</option>';
    }
}

function render() {
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

function loadFile(p) {
    currentPath = p;
    var c = document.getElementById('content');
    c.innerHTML = '<div class="spinner"></div>';

    fetch('/api/file?path=' + encodeURIComponent(p))
        .then(function(r) { return r.text(); })
        .then(function(md) {
            var isBm = bookmarks.indexOf(p) >= 0;
            c.innerHTML = '<div class="path-hint">' + esc(p) +
                ' <span class="bookmark-btn' + (isBm ? ' active' : '') +
                '" onclick="toggleBookmark(\\'' + p + '\\')">' +
                (isBm ? '★' : '☆') + '</span></div>' +
                parseMD(md) + renderRelated(p);
            addToHistory(p);
            buildTOC(md);
            setupQuoteCopy();
        })
        .catch(function(e) {
            c.innerHTML = '<div style="color:#ff4d00;padding:40px;">Ошибка: ' + esc(p) + '</div>';
        });
    render();
}

function parseMD(t) {
    t = t.replace(/\\*\\*Метаданные файла\\*\\*[\\s\\S]*?(?=\\n---|\\n# |\\n## )/, '');
    var h = t;
    h = h.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
    h = h.replace(/^### (.+)$/gm, '<h3 id="$1">$1</h3>');
    h = h.replace(/^## (.+)$/gm, '<h2 id="$1">$1</h2>');
    h = h.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    h = h.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
    h = h.replace(/`([^`]+)`/g, '<code>$1</code>');
    h = h.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
    h = h.replace(/\\*(.+?)\\*/g, '<em>$1</em>');
    h = h.replace(/^---$/gm, '<hr>');
    h = h.replace(/\\n\\n/g, '</p><p>');
    h = '<p>' + h + '</p>';
    h = h.replace(/<p><\\/p>/g, '');
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
        h += '<li><span class="related-link" onclick="loadFile(\\'' + r + '\\')">' + esc(tt) + '</span></li>';
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
    var i = bookmarks.indexOf(p);
    if (i >= 0) bookmarks.splice(i, 1);
    else bookmarks.push(p);
    localStorage.setItem('golem_bookmarks', JSON.stringify(bookmarks));
    loadFile(p);
}

function addToHistory(p) {
    history = history.filter(function(h) { return h !== p; });
    history.unshift(p);
    if (history.length > 15) history.pop();
    localStorage.setItem('golem_history', JSON.stringify(history));
}

function renderHistory() {
    var ct = document.getElementById('sidebar-footer'),
        old = document.getElementById('history-section');
    if (old) old.remove();
    if (!history.length) return;
    var s = document.createElement('div');
    s.id = 'history-section';
    s.innerHTML = '<div class="cat-header">История</div>';
    for (var i = 0; i < Math.min(history.length, 8); i++) {
        (function(p) {
            var d = document.createElement('div');
            d.className = 'history-item';
            var f = FILES.find(function(x) { return x.path === p; });
            var t = p || '';
            if (f && f.title) t = f.title;
            d.textContent = t.substring(0, 40);
            d.onclick = function() { loadFile(p); };
            s.appendChild(d);
        })(history[i]);
    }
    ct.insertBefore(s, document.getElementById('stats'));
}

function randomFile() {
    if (!FILES.length) return;
    loadFile(FILES[Math.floor(Math.random() * FILES.length)].path);
}

function copyCurrentLink() {
    if (!currentPath) return;
    var u = window.location.origin + '/api/file?path=' + encodeURIComponent(currentPath);
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
    document.getElementById('back-to-top').style.display = window.scrollY > 400 ? 'flex' : 'none';
});

document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    if (e.key === '/') { document.getElementById('search').focus(); e.preventDefault(); }
    if (e.key === 'Escape') { document.getElementById('search').blur(); }
    if (e.key === 'b' && currentPath) toggleBookmark(currentPath);
    if (e.key === 'r') randomFile();
});

function esc(s) {
    var d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
}
'''

    with open(OUTPUT_DIR / "app.js", 'w', encoding='utf-8') as f:
        f.write(js)

    print_success(f"Веб-интерфейс сохранён: {OUTPUT_DIR}")
    print("   Файлы: index.html, style.css, app.js")
    print()
    print_hint("Запуск сервера:")
    print("   node docs/web/server.js")
    print("   http://localhost:8080/")


def main():
    generate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
