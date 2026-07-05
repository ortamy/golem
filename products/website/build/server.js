// products/website/server.js — сервер для локальной разработки
const http = require('http');
const fs = require('fs').promises;
const path = require('path');
const zlib = require('zlib');

const PORT = 8080;
const ROOT = path.resolve(__dirname, '../..');
const WEB_DIR = __dirname;

const SCAN_DIRS = [
    { folder: 'content/terminology', label: 'Терминология' },
    { folder: 'content/tanakh', label: 'ТаНаХ' },
    { folder: 'content/bashah', label: 'БаШаХ' },
    { folder: 'content/researches', label: 'Исследования' },
    { folder: 'content/teachings', label: 'Учения' },
    { folder: 'content/hebrew', label: 'Изучение иврита' },
    { folder: 'content/paleo-hebrew', label: 'Палео-иврит' },
];

const IGNORE_FILES = ['README.md', 'STRUCTURE.md', 'GLOSSARY.md', 'CHANGELOG.md'];

const CACHE_TTL = 5 * 60 * 1000; // 5 минут
let filesCache = null;
let filesCacheTime = 0;

const SUBCATEGORY_LABELS = {
    'archive': 'Архив',
    'books': 'Книги',
    'chronology': 'Хронология',
    'companies': 'Компании',
    'concepts': 'Понятия',
    'economy': 'Экономика',
    'events': 'События',
    'history': 'История',
    'language': 'Язык',
    'languages': 'Языки',
    'manuscripts': 'Рукописи',
    'media': 'Медиа',
    'medicine': 'Медицина',
    'names': 'Имена',
    'persons': 'Личности',
    'physis': 'Природа',
    'practices': 'Практики',
    'psychology': 'Психология',
    'roman-law': 'Римское право',
    'science': 'Наука',
    'simvolika': 'Символика',
    'slavery': 'Рабство',
    'sociology': 'Общество',
    'sport': 'Спорт',
    'systems': 'Системы',
    'tanakh': 'ТаНаХ',
    'teachings': 'Учения',
    'adam': 'Адам',
    'anatomy': 'Анатомия',
    'brit-nissuin': 'Брит-нисуин',
    'creation': 'Творение',
    'elohim': 'Элоhим',
    'geography': 'География',
    'hitgalut': 'Хитгалут',
    'kehillah': 'Кеhилла',
    'kelim': 'Келим',
    'makom': 'Маком',
    'mikra': 'Микра',
    'moadim': 'Моадим',
    'ruach': 'Руах',
    'shedim': 'Шедим',
    'tamid': 'Тамид',
    // Подкатегории ruach
    'behemot': 'Беhемот',
    'chayot': 'Хайот',
    'cholim': 'Холим',
    'leshonot': 'Лешонот',
    'levushim': 'Левушим',
    'makot': 'Мако́т',
    'matachot': 'Матахот',
    'mavet': 'Мавет',
    'meshalim': 'Мешалим',
    'misparim': 'Миспарим',
    'seor': 'Сеор',
    'taharah': 'Таhара',
    'techiah': 'Техия',
    // Подкатегории shedim
    'avonot': 'Авонóт',
    'choshech': 'Хошех',
    'kerav': 'Керав',
    'nefilah': 'Нефила',
    'rodefim': 'Родефим',
    'ruchot-raot': 'Рухот раот',
    'shemot-shedim': 'Шемот шедим',
    'sheol': 'Шеол',
};

const ICON_RULES = {
    "content/terminology": "scroll.png",
    "content/researches": "book.png",
    "content/teachings": "heart.png",
    "content/practices": "shield.png",
    "content/hebrew": "lamp.png",
    "content/exposed": "sword.png",
    "content/tanakh/books": "scrolls.png",
    "content/tanakh/persons": "default.png",
    "content/tanakh/events": "default.png",
    "content/bashah/books": "scrolls.png",
    "content/bashah/letters": "scales.png",
    "content/bashah/persons": "default.png",
    "content/bashah/events": "default.png",
    "content/bashah/teachings": "heart.png",
    "content/bashah/terminology": "scroll.png",
    "content/bashah/concepts": "anchor.png",
    "content/bashah/practices": "shield.png",
    "content/bashah/chronology": "hourglass.png",
    "content/bashah/manuscripts": "default.png",
    "content/bashah/geography": "default.png",
    "content/bashah/nevua": "torch.png",
    "content/tzel/adam": "vase.png",
    "content/tzel/brit-nissuin": "ring.png",
    "content/tzel/elohim": "default.png",
    "content/tzel/hitgalut": "alert.png",
    "content/tzel/kehillah": "default.png",
    "content/tzel/kelim": "hammer-and-chisel.png",
    "content/tzel/makom": "default.png",
    "content/tzel/mikra": "default.png",
    "content/tzel/moadim": "track.png",
    "content/tzel/ruach": "default.png",
    "content/tzel/shedim": "default.png",
    "content/tzel/tamid": "default.png",
};

function resolveIcon(relPath) {
    var sorted = Object.keys(ICON_RULES).sort(function(a, b) { return b.length - a.length; });
    for (var i = 0; i < sorted.length; i++) {
        if (relPath.startsWith(sorted[i])) {
            return ICON_RULES[sorted[i]];
        }
    }
    return "default.png";
}

const MIME = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/plain; charset=utf-8',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
};

async function scanFiles() {
    const now = Date.now();
    if (filesCache && (now - filesCacheTime) < CACHE_TTL) {
        return filesCache;
    }

    const files = [];
    for (const { folder, label } of SCAN_DIRS) {
        const dirPath = path.join(ROOT, folder);
        try {
            await walkDir(dirPath, folder, label, files);
        } catch (e) {
            console.error('Ошибка сканирования папки', folder, e.message);
        }
    }
    filesCache = files;
    filesCacheTime = now;
    return files;
}

async function walkDir(dirPath, baseFolder, label, files) {
    let entries;
    try {
        entries = await fs.readdir(dirPath, { withFileTypes: true });
    } catch (e) {
        return;
    }
    for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        if (entry.isDirectory()) {
            await walkDir(fullPath, baseFolder, label, files);
        } else if (entry.name.endsWith('.md') && !IGNORE_FILES.includes(entry.name)) {
            const relPath = path.relative(ROOT, fullPath).replace(/\\/g, '/');
            let content;
            try {
                content = await fs.readFile(fullPath, 'utf-8');
            } catch (e) {
                continue;
            }
            const title = extractTitle(content) || entry.name.replace('.md', '').replace(/-/g, ' ');
            const topic = extractTopic(content);
            const related = extractRelated(content);
            const parts = relPath.split('/');
            let subcategory = '';
            if (parts.length > 3) {
                subcategory = SUBCATEGORY_LABELS[parts[2]] || parts[2];
            }
            files.push({
                path: relPath,
                title: title,
                topic: topic,
                category: label,
                subcategory: subcategory,
                related: related,
                icon: resolveIcon(relPath),
            });
        }
    }
}

function extractTitle(content) {
    const match = content.match(/^#\s+(.+?)$/m);
    if (match) {
        return match[1]
            .replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{FE00}-\u{FEFF}\u{200D}\u{FE0F}]/gu, '')
            .replace(/^\s+/, '')
            .trim()
            .substring(0, 80);
    }
    return '';
}

function extractTopic(content) {
    const match = content.match(/\*\*Тема:\*\*\s*(.+?)(?:\n|$)/);
    return match ? match[1].trim().substring(0, 100) : '';
}

function extractRelated(content) {
    const sections = content.match(/\*\*Связанные файлы:\*\*[\s\S]*?(?=\n\n|$)/g);
    if (!sections) return [];
    const related = [];
    for (const section of sections) {
        const matches = section.matchAll(/`([^`]+)`/g);
        for (const m of matches) {
            if (!related.includes(m[1])) {
                related.push(m[1]);
            }
        }
    }
    return related;
}

function renderMdPage(title, content, filePath) {
    let html = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/^\> (.+)$/gm, '<blockquote>$1</blockquote>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    html = '<p>' + html + '</p>';

    return `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} — Голем</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/style.css">
<style>
body { font-family: 'EB Garamond', Georgia, serif; font-size: 18px; line-height: 1.8; background: #ede0c8; color: #2c1810; margin: 0; padding-top: 56px; }
.top-bar { position: fixed; top: 0; left: 0; right: 0; background: #2c1810; color: #ede0c8; padding: 0 24px; height: 56px; display: flex; align-items: center; justify-content: space-between; z-index: 1000; border-bottom: 1px solid #4a3020; }
.top-bar .logo { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 20px; font-weight: 700; font-style: italic; color: #b8860b; letter-spacing: 4px; }
.top-bar .logo a { color: #b8860b; text-decoration: none; }
.md-content { max-width: 800px; margin: 0 auto; padding: 40px 24px; }
.md-content h1 { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 36px; font-weight: 700; font-style: italic; color: #b8860b; margin-bottom: 8px; }
.md-content h2 { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 28px; color: #b8860b; margin-top: 32px; margin-bottom: 16px; }
.md-content h3 { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 22px; color: #2c1810; margin-top: 24px; }
.md-content p { margin-bottom: 16px; }
.md-content code { background: #faf3e0; padding: 2px 6px; border-radius: 3px; font-size: 15px; border: 1px solid #d4c4a8; }
.md-content blockquote { border-left: 3px solid #b8860b; padding-left: 16px; margin-left: 0; color: #5c4a3a; font-style: italic; }
.site-footer { background: #2c1810; color: #8a7a6a; padding: 40px 24px 24px; text-align: center; margin-top: 60px; }
.footer-copy { font-size: 12px; letter-spacing: 2px; font-family: 'Cormorant Garamond', Georgia, serif; }
</style>
</head>
<body>
<header class="top-bar">
  <div class="logo"><a href="/ru/index.html">ГОЛЕМ</a></div>
</header>
<main class="md-content">
${html}
</main>
<footer class="site-footer">
  <div class="footer-copy">Проект «Голем». Восстановление истины. Яхве один.</div>
</footer>
</body>
</html>`;
}

function compress(content, mimeType) {
    const textTypes = ['text/html', 'text/css', 'application/javascript', 'application/json', 'text/plain', 'image/svg+xml'];
    const isText = textTypes.some(t => mimeType.startsWith(t));
    if (!isText) return { body: content, headers: {} };

    const acceptEncoding = (req.headers['accept-encoding'] || '').split(',').map(s => s.trim());
    if (acceptEncoding.includes('gzip')) {
        return {
            body: zlib.gzipSync(content),
            headers: { 'Content-Encoding': 'gzip', 'Vary': 'Accept-Encoding' }
        };
    }
    if (acceptEncoding.includes('deflate')) {
        return {
            body: zlib.deflateSync(content),
            headers: { 'Content-Encoding': 'deflate', 'Vary': 'Accept-Encoding' }
        };
    }
    return { body: content, headers: {} };
}

const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const pathname = url.pathname;

    res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8080');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    if (pathname === '/api/files') {
        try {
            const files = await scanFiles();
            const body = JSON.stringify(files, null, 2);
            const compressed = compress(body, 'application/json');
            res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', ...compressed.headers });
            res.end(compressed.body);
        } catch (e) {
            console.error('Ошибка сканирования:', e.message);
            res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
            res.end(JSON.stringify({ error: e.message }));
        }
        return;
    }

    if (pathname === '/api/file') {
        const filePath = url.searchParams.get('path');
        if (!filePath) {
            res.writeHead(400);
            res.end('Missing path parameter');
            return;
        }
        const normalized = path.normalize(filePath).replace(/\\/g, '/');
        if (normalized.includes('..')) {
            res.writeHead(403);
            res.end('Forbidden');
            return;
        }
        const fullPath = path.join(ROOT, normalized);
        if (!normalized.endsWith('.md')) {
            res.writeHead(400);
            res.end('Only .md files allowed');
            return;
        }
        try {
            const stat = await fs.stat(fullPath);
            if (!stat.isFile()) {
                res.writeHead(404);
                res.end('Not found');
                return;
            }
            const content = await fs.readFile(fullPath, 'utf-8');
            res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
            res.end(content);
        } catch (e) {
            res.writeHead(404);
            res.end('Not found');
        }
        return;
    }

    if (pathname === '/view') {
        const filePath = url.searchParams.get('path');
        if (!filePath || !filePath.endsWith('.md')) {
            res.writeHead(400);
            res.end('Missing path parameter');
            return;
        }
        const normalized = path.normalize(filePath).replace(/\\/g, '/');
        if (normalized.includes('..')) {
            res.writeHead(403);
            res.end('Forbidden');
            return;
        }
        const fullPath = path.join(ROOT, normalized);
        try {
            const stat = await fs.stat(fullPath);
            if (!stat.isFile()) {
                res.writeHead(404);
                res.end('Not found');
                return;
            }
            const content = await fs.readFile(fullPath, 'utf-8');
            const title = extractTitle(content) || filePath.replace('.md', '').replace(/-/g, ' ');
            const html = renderMdPage(title, content, filePath);
            const compressed = compress(html, 'text/html');
            res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', ...compressed.headers });
            res.end(compressed.body);
        } catch (e) {
            res.writeHead(404);
            res.end('Not found');
        }
        return;
    }

    let filePath = pathname === '/' ? '/index.html' : pathname;
    let fullPath = path.join(WEB_DIR, filePath);

    try {
        await fs.access(fullPath);
    } catch {
        fullPath = path.join(ROOT, filePath);
    }

    try {
        const stat = await fs.stat(fullPath);
        if (stat.isDirectory()) {
            res.writeHead(404);
            res.end('Not found');
            return;
        }
    } catch {
        res.writeHead(404);
        res.end('Not found');
        return;
    }

    const ext = path.extname(fullPath);
    const mimeType = MIME[ext] || 'application/octet-stream';
    const content = await fs.readFile(fullPath);
    const compressed = compress(content, mimeType);
    res.writeHead(200, { 'Content-Type': mimeType, ...compressed.headers });
    res.end(compressed.body);
});

server.listen(PORT, () => {
    console.log('\n========================================');
    console.log('  GOLEM — Свидетель Истины');
    console.log('========================================');
    console.log(`  Сервер запущен: http://localhost:${PORT}/`);
    console.log(`  API файлов:     http://localhost:${PORT}/api/files`);
    console.log(`  API файла:      http://localhost:${PORT}/api/file?path=content/terminology/yhwh.md`);
    console.log('========================================\n');
    console.log('  Категории:');
    SCAN_DIRS.forEach(({ folder, label }) => {
        const dirPath = path.join(ROOT, folder);
        const exists = fs.existsSync(dirPath);
        console.log(`    ${exists ? '✅' : '⚠️ '} ${label} (${folder})`);
    });
    console.log('========================================\n');
});