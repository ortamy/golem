// web/server.js — сервер для локальной разработки
// docs/web/server.js — динамический сервер Golem (Node.js)
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const ROOT = path.resolve(__dirname, '..');
const WEB_DIR = __dirname;

const SCAN_DIRS = [
    { folder: 'content/terminology', label: 'Терминология' },
    { folder: 'content/tanakh', label: 'ТаНаХ' },
    { folder: 'content/bashah', label: 'БаШаХ' },
    { folder: 'content/researches', label: 'Исследования' },
    { folder: 'content/teachings', label: 'Учения' },
    { folder: 'content/hebrew', label: 'Изучение иврита' },
];

const IGNORE_FILES = ['README.md', 'STRUCTURE.md', 'GLOSSARY.md', 'CHANGELOG.md'];

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
};

const ICON_RULES = {
    "content/terminology": "scroll.png",
    "content/researches": "book.png",
    "content/teachings": "heart.png",
    "content/practices": "shield.png",
    "content/hebrew": "lamp.png",
    "content/exposed": "sword.png",
    "content/tanakh/books": "scrolls.png",
    "content/tanakh/persons": "person.png",
    "content/tanakh/events": "event.png",
    "content/bashah/books": "scrolls.png",
    "content/bashah/letters": "scales.png",
    "content/bashah/persons": "person.png",
    "content/bashah/events": "event.png",
    "content/bashah/teachings": "heart.png",
    "content/bashah/terminology": "scroll.png",
    "content/bashah/concepts": "anchor.png",
    "content/bashah/practices": "shield.png",
    "content/bashah/chronology": "hourglass.png",
    "content/bashah/manuscripts": "manuscripts.png",
    "content/bashah/geography": "geography.png",
    "content/bashah/nevua": "torch.png",
    "content/tzel/adam": "vase.png",
    "content/tzel/brit-nissuin": "ring.png",
    "content/tzel/elohim": "elohim.png",
    "content/tzel/hitgalut": "alert.png",
    "content/tzel/kehillah": "kehillah.png",
    "content/tzel/kelim": "hammer-and-chisel.png",
    "content/tzel/makom": "makom.png",
    "content/tzel/mikra": "mikra.png",
    "content/tzel/moadim": "track.png",
    "content/tzel/ruach": "ruach.png",
    "content/tzel/shedim": "shedim.png",
    "content/tzel/tamid": "tamid.png",
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

function scanFiles() {
    const files = [];
    for (const { folder, label } of SCAN_DIRS) {
        const dirPath = path.join(ROOT, folder);
        if (!fs.existsSync(dirPath)) continue;
        walkDir(dirPath, folder, label, files);
    }
    return files;
}

function walkDir(dirPath, baseFolder, label, files) {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        if (entry.isDirectory()) {
            walkDir(fullPath, baseFolder, label, files);
        } else if (entry.name.endsWith('.md') && !IGNORE_FILES.includes(entry.name)) {
            const relPath = path.relative(ROOT, fullPath).replace(/\\/g, '/');
            const content = fs.readFileSync(fullPath, 'utf-8');
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

// Сервер
const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const pathname = url.pathname;

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    if (pathname === '/api/files') {
        try {
            const files = scanFiles();
            res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
            res.end(JSON.stringify(files, null, 2));
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
        const fullPath = path.join(ROOT, filePath);
        if (!fs.existsSync(fullPath) || !filePath.endsWith('.md')) {
            res.writeHead(404);
            res.end('File not found');
            return;
        }
        try {
            const content = fs.readFileSync(fullPath, 'utf-8');
            res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
            res.end(content);
        } catch (e) {
            res.writeHead(500);
            res.end('Error reading file');
        }
        return;
    }

    let filePath = pathname === '/' ? '/index.html' : pathname;
    let fullPath = path.join(WEB_DIR, filePath);

    if (!fs.existsSync(fullPath)) {
        fullPath = path.join(ROOT, filePath);
    }

    if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) {
        res.writeHead(404);
        res.end('Not found');
        return;
    }

    const ext = path.extname(fullPath);
    const mimeType = MIME[ext] || 'application/octet-stream';
    const content = fs.readFileSync(fullPath);
    res.writeHead(200, { 'Content-Type': mimeType });
    res.end(content);
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