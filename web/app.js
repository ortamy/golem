// web/app.js — Golem Web Interface v10.0

(function() {
    'use strict';

    var IS_LOCAL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    var API = IS_LOCAL ? '/api/files' : 'files.json';

    var FILES = [],
        currentPath = null,
        bookmarks = JSON.parse(localStorage.getItem('golem_bookmarks') || '[]'),
        fileHistory = JSON.parse(localStorage.getItem('golem_history') || '[]'),
        fontSize = localStorage.getItem('golem_fontSize') || 'medium',
        filteredCache = null;

    function isMobile() { return window.innerWidth <= 768; }
    function $(id) { return document.getElementById(id); }

    function esc(s) {
        var d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    function fetchJSON(url, cb) {
        fetch(url).then(function(r) { return r.json(); }).then(cb).catch(function(e) { console.error(e); });
    }

    function fetchText(url, cb) {
        fetch(url).then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); }).then(cb).catch(function(e) { console.error(e); });
    }

    function getIconHtml(iconName) {
        if (!iconName || iconName === 'default.png') return '';
        return '<img class="file-icon" src="icons/32/'+iconName+'" alt="" width="16" height="16"> ';
    }

    function renderTitle(file) {
        var title = file.title || file.path;
        // Убираем все эмодзи из начала заголовка
        title = title.replace(/^[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2000}-\u{27B0}\u{FE00}-\u{FE0F}\u{1FA00}-\u{1FA6F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{1F1E0}-\u{1F1FF}\u{2702}-\u{27B0}\u{2934}-\u{2935}\u{25AA}-\u{25AB}\u{25FB}-\u{25FE}\u{2B05}-\u{2B07}\u{2B1B}-\u{2B1C}\u{2B50}\u{2764}\u{2714}\u{2716}\u{303D}\u{2122}\u{00A9}\u{00AE}\u{2194}-\u{2199}\u{21A9}-\u{21AA}\u{231A}-\u{231B}\u{2328}\u{23CF}\u{23E9}-\u{23F3}\u{23F8}-\u{23FA}\u{24C2}\u{25B6}\u{25C0}\u{3030}\u{3297}\u{3299}]+/gu, '').trim();
        // Если есть иконка — вставляем её
        if (file.icon && file.icon !== 'default.png') {
            var iconPath = 'icons/32/' + file.icon;
            return '<img src="' + iconPath + '" class="icon" alt="" style="width:20px;height:20px;vertical-align:middle;margin-right:8px;">' + esc(title);
        }
        return esc(title);
    }

    // Навигация
    function buildSelects() {
        var counts = {}, cats = [];
        FILES.forEach(function(f) {
            if (!counts[f.category]) { counts[f.category] = 0; cats.push(f.category); }
            counts[f.category]++;
        });
        cats.sort();
        ['category-select', 'category-select-mobile'].forEach(function(elId) {
            var sel = $(elId); if (!sel) return;
            var val = sel.value;
            sel.innerHTML = '<option value="">Все категории</option>';
            cats.forEach(function(cat) { sel.innerHTML += '<option value="' + esc(cat) + '">' + esc(cat) + ' (' + counts[cat] + ')</option>'; });
            if (val) sel.value = val;
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
            return (f.title||'').toLowerCase().indexOf(q)>=0 || (f.topic||'').toLowerCase().indexOf(q)>=0 || (f.path||'').toLowerCase().indexOf(q)>=0;
        });

        var ss = m ? $('subcategory-select-mobile') : $('subcategory-select');
        if (ss && cat) {
            var subs = {};
            FILES.forEach(function(f) { if (f.category===cat && f.subcategory) subs[f.subcategory]=true; });
            var sn = Object.keys(subs).sort();
            if (sn.length) {
                var cur = ss.value;
                ss.style.display = 'block';
                ss.innerHTML = '<option value="">Все подкатегории</option>';
                sn.forEach(function(s) { ss.innerHTML += '<option value="'+esc(s)+'"'+(s===cur?' selected':'')+'>'+esc(s)+'</option>'; });
            } else { ss.style.display = 'none'; ss.value = ''; }
        } else if (ss) { ss.style.display = 'none'; ss.value = ''; }

        filteredCache = list;
        return list;
    }

    function renderList(container, itemClass, headerClass, clickHandler) {
        if (!container) return;
        container.innerHTML = '';
        var filtered = getFiltered(), cc = '';
        filtered.forEach(function(f) {
            if (f.category !== cc) {
                cc = f.category;
                var h = document.createElement('div'); h.className = headerClass; h.textContent = cc;
                container.appendChild(h);
            }
            var d = document.createElement('div'); d.className = itemClass;
            d.innerHTML = '<div class="title">' + renderTitle(f) + '</div>'+(f.topic?'<div class="topic">'+esc((f.topic||'').substring(0,90))+'</div>':'');
            d.onclick = (function(p){ return function(){ clickHandler(p); }; })(f.path);
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
            for (var i=0; i<items.length; i++) items[i].remove();
            renderList(mlv, 'file-item-mobile', 'cat-header-mobile', openFileMobile);
        } else {
            renderList($('file-list'), 'file-item', 'cat-header', loadFile);
            var tc = $('total-count'); if (tc) tc.textContent = getFiltered().length;
        }
        renderBookmarks(); renderHistory();
    }

    // Хлебные крошки
    function renderBreadcrumbs(p) {
        var parts = p.split('/'), html = 'Главная';
        for (var i=0; i<parts.length; i++) html += ' <span class="bc-sep">›</span> ' + parts[i].replace('.md','');
        return html;
    }

    // Прогресс чтения
    function updateProgressBar() {
        var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        var scrolled = (winScroll / height) * 100;
        var bar = $('progress-bar'); if (bar) bar.style.width = scrolled + '%';
    }

    // Размер шрифта
    function setFontSize(size) {
        fontSize = size;
        localStorage.setItem('golem_fontSize', size);
        var sizes = { small: '12px', medium: '14px', large: '16px' };
        document.body.style.fontSize = sizes[size] || '14px';
        var btns = document.querySelectorAll('.font-size-btn');
        for (var i=0; i<btns.length; i++) btns[i].classList.remove('active');
        var ab = document.querySelector('.font-size-btn[data-size="'+size+'"]');
        if (ab) ab.classList.add('active');
    }

function parseMD(t, fileIcon) {
    t = t.replace(/\*\*Метаданные файла\*\*[\s\S]*?(?=\n---|\n# |\n## )/, '');
    
    var lines = t.split('\n');
    var html = '';
    var inParagraph = false;
    
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        
        // Пустая строка — закрываем параграф
        if (line.trim() === '') {
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            continue;
        }
        
        // Заголовки
        if (line.match(/^#### (.+)$/)) {
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += '<h4>' + line.replace(/^#### /, '') + '</h4>';
            continue;
        }
        if (line.match(/^### (.+)$/)) {
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            var h3title = line.replace(/^### /, '').replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2000}-\u{27B0}\u{FE00}-\u{FE0F}\u{1FA00}-\u{1FA6F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{1F1E0}-\u{1F1FF}\u{2702}-\u{27B0}\u{2934}-\u{2935}\u{25AA}-\u{25AB}\u{25FB}-\u{25FE}\u{2B05}-\u{2B07}\u{2B1B}-\u{2B1C}\u{2B50}\u{2764}\u{2714}\u{2716}\u{303D}\u{2122}\u{00A9}\u{00AE}\u{2194}-\u{2199}\u{21A9}-\u{21AA}\u{231A}-\u{231B}\u{2328}\u{23CF}\u{23E9}-\u{23F3}\u{23F8}-\u{23FA}\u{24C2}\u{25B6}\u{25C0}\u{3030}\u{3297}\u{3299}]+/gu, '').trim();
            html += '<h3 id="' + h3title + '">' + h3title + '</h3>';
            continue;
        }
        if (line.match(/^## (.+)$/)) {
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            var h2title = line.replace(/^## /, '').replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2000}-\u{27B0}\u{FE00}-\u{FE0F}\u{1FA00}-\u{1FA6F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{1F1E0}-\u{1F1FF}\u{2702}-\u{27B0}\u{2934}-\u{2935}\u{25AA}-\u{25AB}\u{25FB}-\u{25FE}\u{2B05}-\u{2B07}\u{2B1B}-\u{2B1C}\u{2B50}\u{2764}\u{2714}\u{2716}\u{303D}\u{2122}\u{00A9}\u{00AE}\u{2194}-\u{2199}\u{21A9}-\u{21AA}\u{231A}-\u{231B}\u{2328}\u{23CF}\u{23E9}-\u{23F3}\u{23F8}-\u{23FA}\u{24C2}\u{25B6}\u{25C0}\u{3030}\u{3297}\u{3299}]+/gu, '').trim();
            html += '<h2 id="' + h2title + '">' + h2title + '</h2>';
            continue;
        }
        if (line.match(/^# (.+)$/)) {
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            var h1title = line.replace(/^# /, '').replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2000}-\u{27B0}\u{FE00}-\u{FE0F}\u{1FA00}-\u{1FA6F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{1F1E0}-\u{1F1FF}\u{2702}-\u{27B0}\u{2934}-\u{2935}\u{25AA}-\u{25AB}\u{25FB}-\u{25FE}\u{2B05}-\u{2B07}\u{2B1B}-\u{2B1C}\u{2B50}\u{2764}\u{2714}\u{2716}\u{303D}\u{2122}\u{00A9}\u{00AE}\u{2194}-\u{2199}\u{21A9}-\u{21AA}\u{231A}-\u{231B}\u{2328}\u{23CF}\u{23E9}-\u{23F3}\u{23F8}-\u{23FA}\u{24C2}\u{25B6}\u{25C0}\u{3030}\u{3297}\u{3299}]+/gu, '').trim();
            var iconHtml = fileIcon ? fileIcon : '';
            html += '<h1>' + iconHtml + h1title + '</h1>';
            continue;
        }
        
        // Горизонтальная линия
        if (line.match(/^---$/)) {
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += '<hr>';
            continue;
        }
        
        // Цитата
        if (line.match(/^> (.+)$/)) {
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += '<blockquote>' + line.replace(/^> /, '') + '</blockquote>';
            continue;
        }
        
        // Обычный текст — параграф
        if (!inParagraph) {
            html += '<p>';
            inParagraph = true;
        } else {
            html += '\n';
        }
        
        // Inline форматирование
        line = line.replace(/!\[icon\]\(([^)]+)\)/g, '<img src="$1" class="h2-icon" alt="" style="width:20px;height:20px;vertical-align:middle;margin-right:8px;">');
        line = line.replace(/`([^`]+)`/g, '<code>$1</code>');
        line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        line = line.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        html += line;
    }
    
    if (inParagraph) { html += '</p>'; }
    
    return html;
}

    function loadFile(p) {
        currentPath = p;
        var c = $('content');
        c.classList.remove('fade-in');
        c.innerHTML = '<div class="spinner"></div>';
        var url = IS_LOCAL ? '/api/file?path='+encodeURIComponent(p) : p;
        fetchText(url, function(md) {
            var isBm = bookmarks.indexOf(p) >= 0;
            var file = FILES.find(function(x){ return x.path === p; });
            var iconHtml = (file && file.icon && file.icon !== 'default.png')
                ? '<img src="icons/32/' + file.icon + '" class="content-icon" alt="" style="width:28px;height:28px;vertical-align:middle;margin-right:10px;">'
                : '';
            c.innerHTML = '<div id="breadcrumbs">'+renderBreadcrumbs(p)+'</div>' +
                '<div class="path-hint">'+esc(p)+' <span class="bookmark-btn'+(isBm?' active':'')+
                '" onclick="toggleBookmark(\''+p.replace(/'/g,"\\'")+'\')">'+(isBm?'★':'☆')+'</span></div>'+
                parseMD(md, iconHtml)+renderRelated(p);
            addToHistory(p); buildTOC(md); setupQuoteCopy();
            void c.offsetWidth; c.classList.add('fade-in');
        }, function() { c.innerHTML = '<div style="color:#ff4d00;padding:40px;">Ошибка: '+esc(p)+'</div>'; });
    }


    function openFileMobile(p) {
        currentPath = p;
        $('file-page').style.display = 'block';
        $('file-path-hint').textContent = p;
        var bm = $('file-bookmark-btn'), isBm = bookmarks.indexOf(p) >= 0;
        bm.textContent = isBm?'★':'☆'; bm.className = 'bookmark-btn'+(isBm?' active':'');
        bm.onclick = function(){ toggleBookmark(p); };
        $('mobile-list-view').style.display = 'none';
        $('stats-mobile').style.display = 'none';
        var c = $('file-content-mobile'); c.innerHTML = '<div class="spinner"></div>';
        var url = IS_LOCAL ? '/api/file?path='+encodeURIComponent(p) : p;
        fetchText(url, function(md) {
            var file = FILES.find(function(x){ return x.path === p; });
            var iconHtml = (file && file.icon && file.icon !== 'default.png')
                ? '<img src="icons/32/' + file.icon + '" class="content-icon" alt="" style="width:28px;height:28px;vertical-align:middle;margin-right:10px;">'
                : '';
            c.innerHTML = parseMD(md, iconHtml)+renderRelatedMobile(p);
            addToHistory(p);
        }, function() { c.innerHTML = '<div style="color:#ff4d00;padding:40px;">Ошибка: '+esc(p)+'</div>'; });
    }

    function closeFile() {
        $('file-page').style.display = 'none';
        $('mobile-list-view').style.display = 'block';
        $('stats-mobile').style.display = 'block';
        currentPath = null; render();
    }

    function buildTOC(md) {
        var pn = $('toc-panel'), ls = $('toc-list');
        var hd = md.match(/^#{2,3} (.+)$/gm);
        if (!hd || hd.length<2) { pn.style.display = 'none'; return; }
        pn.style.display = 'block'; ls.innerHTML = '';
        hd.forEach(function(h) {
            var lv = h.indexOf('### ')=== -1?'h2':'h3', tt = h.replace(/^#{2,3} /,'').trim();
            var d = document.createElement('div'); d.className = 'toc-item '+lv; d.textContent = tt;
            d.onclick = function(){ var el = $(tt); if (el) el.scrollIntoView({behavior:'smooth'}); };
            ls.appendChild(d);
        });
    }

    function renderLinks(p, clickFn) {
        var f = FILES.find(function(x){ return x.path===p; });
        if (!f || !f.related || !f.related.length) return '';
        var h = '<hr><h3>Связанные файлы</h3><ul>';
        f.related.forEach(function(r) {
            var rf = FILES.find(function(x){ return x.path===r; }), tt = rf?(rf.title||r):r;
            h += '<li><span class="related-link" onclick="'+clickFn.name+'(\''+r.replace(/'/g,"\\'")+'\')">'+esc(tt)+'</span></li>';
        });
        return h+'</ul>';
    }
    function renderRelated(p){ return renderLinks(p, loadFile); }
    function renderRelatedMobile(p){ return renderLinks(p, openFileMobile); }

    function setupQuoteCopy() {
        var qs = document.querySelectorAll('#content blockquote');
        for (var i=0; i<qs.length; i++) qs[i].onclick = function(){ navigator.clipboard.writeText(this.textContent.trim()).then(showToast); };
    }

    function showToast() {
        var t = $('copy-toast'); t.classList.add('show');
        setTimeout(function(){ t.classList.remove('show'); }, 1500);
    }

    function toggleBookmark(p) {
        if (!p) return;
        var i = bookmarks.indexOf(p);
        if (i>=0) bookmarks.splice(i,1); else bookmarks.push(p);
        localStorage.setItem('golem_bookmarks', JSON.stringify(bookmarks));
        if (isMobile()) {
            var bm = $('file-bookmark-btn'), isBm = bookmarks.indexOf(p)>=0;
            bm.textContent = isBm?'★':'☆'; bm.className = 'bookmark-btn'+(isBm?' active':'');
        } else loadFile(p);
    }

    function addToHistory(p) {
        fileHistory = fileHistory.filter(function(h){ return h!==p; });
        fileHistory.unshift(p); if (fileHistory.length>15) fileHistory.pop();
        localStorage.setItem('golem_history', JSON.stringify(fileHistory));
    }

    function renderBookmarks() {
        var bl = $('bookmarks-list'), bm = $('burger-bookmarks-list');
        [bl,bm].forEach(function(list) {
            if (!list) return; list.innerHTML = '';
            bookmarks.forEach(function(p) {
                var d = document.createElement('div'); d.className = 'bookmark-item';
                var bf = FILES.find(function(x){ return x.path===p; });
                d.innerHTML = bf ? renderTitle(bf) : esc(p);
                d.onclick = function(){ if(isMobile()) openFileMobile(p); else loadFile(p); };
                list.appendChild(d);
            });
        });
        var bs = $('bookmarks-section'); if (bs) bs.style.display = bookmarks.length?'block':'none';
    }

    function renderHistory() {
        var hl = $('history-list'), bh = $('burger-history-list');
        [hl,bh].forEach(function(list) {
            if (!list) return; list.innerHTML = '';
            fileHistory.slice(0,8).forEach(function(p) {
                var d = document.createElement('div'); d.className = 'history-item';
                var f = FILES.find(function(x){ return x.path===p; });
                d.innerHTML = f ? renderTitle(f) : esc((p||'').substring(0,40));
                d.onclick = function(){ if(isMobile()) openFileMobile(p); else loadFile(p); };
                list.appendChild(d);
            });
        });
        var hs = $('history-section'); if (hs) hs.style.display = fileHistory.length?'block':'none';
    }

    function toggleBurger(){ $('burger-menu').classList.toggle('open'); $('burger-overlay').classList.toggle('show'); }
    function closeBurger(){ $('burger-menu').classList.remove('open'); $('burger-overlay').classList.remove('show'); }

    function randomFile() {
        if (!FILES.length) return;
        closeBurger();
        var p = FILES[Math.floor(Math.random()*FILES.length)].path;
        if (isMobile()) openFileMobile(p); else loadFile(p);
    }

    function copyCurrentLink() {
        if (!currentPath) return;
        var u = window.location.origin + (IS_LOCAL?'/api/file?path=':'/') + encodeURIComponent(currentPath);
        navigator.clipboard.writeText(u).then(showToast);
    }

    function toggleTheme() {
        var b = document.body;
        var isLight = b.classList.contains('light');
        b.classList.toggle('light', !isLight);
        b.classList.toggle('dark', isLight);
        localStorage.setItem('golem_theme', isLight?'dark':'light');
    }

    // Обработчик ресайза — перерисовывает интерфейс при смене ширины окна
    var lastWidth = window.innerWidth;
    window.addEventListener('resize', function() {
        var w = window.innerWidth;
        if ((lastWidth <= 768) !== (w <= 768)) {
            // Пересекли границу мобильного/десктопа — перерендериваем
            lastWidth = w;
            // Сбросим filteredCache и перерисуем
            if (FILES.length) {
                render();
            }
        } else {
            // В пределах одного режима — просто обновим layout при необходимости
            lastWidth = w;
        }
    });

    // Инициализация
    if (localStorage.getItem('golem_theme') === 'light') {
        document.body.classList.remove('dark'); document.body.classList.add('light');
    }

    setFontSize(fontSize);
    window.addEventListener('scroll', updateProgressBar);
    window.addEventListener('scroll', function() {
        var bt = $('back-to-top'); if (bt) bt.style.display = window.scrollY>400?'flex':'none';
    });

    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
        var m = isMobile();
        if (e.key === '/') { var s = m?$('search-mobile'):$('search'); if (s) s.focus(); e.preventDefault(); }
        if (e.key === 'Escape') { if (m && currentPath) closeFile(); else { var s2 = m?$('search-mobile'):$('search'); if (s2) s2.blur(); } }
        if (e.key === 'b' && currentPath) toggleBookmark(currentPath);
        if (e.key === 'r') randomFile();
    });

    window.toggleTheme = toggleTheme;
    window.toggleBurger = toggleBurger;
    window.closeBurger = closeBurger;
    window.randomFile = randomFile;
    window.copyCurrentLink = copyCurrentLink;
    window.toggleBookmark = toggleBookmark;
    window.closeFile = closeFile;
    window.render = render;
    window.setFontSize = setFontSize;

    fetchJSON(API, function(data) {
        FILES = data;
        buildSelects();
        render();
    }, function(e) {
        console.error(e.message);
        var el = isMobile()?$('mobile-list-view'):$('file-list');
        if (el) el.innerHTML = '<div style="padding:20px;color:#ff4d00;">Ошибка загрузки</div>';
    });
})();