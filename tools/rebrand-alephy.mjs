// Одноразовый кодмод ребрендинга GOLEM → ALEPHY (golem → alephy).
// Латиница: регистро-сохраняющая замена golem/GOLEM/Golem → alephy/ALEPHY/Alephy.
// Кириллица: только брендовые формы со склонениями (Голем/Голема/… → Алефи/Алефи/…),
// в защищённых строках (определения термина גֹּלֶם/𐤂𐤋𐤌/«без алеф») и файлах-словарях — без изменений.
// Запуск: node tools/rebrand-alephy.mjs  (DRY=1 — сухой прогон)
import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';

const DRY = process.env.DRY === '1';

const TEXT_EXT = new Set([
  '.md', '.html', '.htm', '.js', '.mjs', '.cjs', '.css', '.scss', '.json', '.py',
  '.sh', '.yml', '.yaml', '.txt', '.svg', '.xml', '.toml', '.cfg', '.ini', '.conf',
  '.spec', '.webmanifest', '.bat', '.cmd', '.lock', '.map', '.gitignore',
  '.dockerignore', '.clinerules', '.editorconfig', '.npmrc', '.gitattributes',
  '.ts', '.tsx', '.jsx',
]);
// Файлы без расширения, которые тоже текстовые.
const NAME_ALLOW = new Set(['Dockerfile', 'sshd_config']);

// Файлы, где «golem/голем» — исследуемый термин, а не бренд: не трогаем целиком.
const FILE_PROTECT = (p) =>
  p.startsWith('docs/05-DICTIONARIES/') || p.startsWith('products/neuro/');

// Кириллическая замена — только в брендовом хроме и docs (не в контентных статьях).
const CYR_SCOPE = [
  'docs/', 'products/website/src/pages/', 'products/website/src/locales/',
  'products/website/src/js/', 'products/website/apps/researchlab/',
  'products/website/src/content/', 'products/website/index.html',
  'products/website/config/', 'products/website/app.js',
  'products/agents/', 'products/video/', 'docker/', 'tools/', 'tasks/',
  'archive/', 'requirements.txt', 'docker-compose.yml', 'products/INDEX.md',
];

// Производные/служебные пути не правим.
const SKIP = (p) =>
  p.startsWith('products/website/build/') || /(^|\/)test-results\//.test(p);

// Строки-исключения для обоих проходов: ссылки на словарную страницу термина
// (регистр важен: именно строчное golem.md, а не брендовый GOLEM.md),
// анкер roots.json и внешний HF-репозиторий.
const LINE_PROTECTS = [/golem\.md/, /roots\.json#golem/i, /HF_REPO/];
// Кириллические строки с определением термина не меняем.
const CYR_LINE_PROTECT = /𐤂𐤋𐤌|גֹּלֶם|גולם|без\s+алеф|г\.\s?л\.\s?м/i;

const latinRe = /golem/gi;
const latinMap = (m) =>
  m === 'golem' ? 'alephy' : m === 'GOLEM' ? 'ALEPHY' : m === 'Golem' ? 'Alephy' : 'alephy';

// Порядок суффиксов — от длинных к коротким.
const CYR_RULES = [
  [/ГОЛЕМ(АМИ|ОМ|ОЙ|АМ|АХ|А|У|Е|И|Ы)?/g, 'АЛЕФИ'],
  [/Голем(ами|ом|ой|ам|ах|а|у|е|и|ы)?/g, 'Алефи'],
  [/голем(ами|ом|ой|ам|ах|а|у|е|и|ы)?/g, 'алефи'],
];

const list = execSync('git ls-files -z', { maxBuffer: 1 << 28 }).toString('utf8')
  .split('\0').filter(Boolean);

const report = [];
let totalLatin = 0, totalCyr = 0, changedFiles = 0, skipped = [];

for (const p of list) {
  if (SKIP(p)) continue;
  const dot = p.lastIndexOf('.');
  const ext = dot > 0 ? p.slice(dot) : p;
  const base = p.slice(p.lastIndexOf('/') + 1);
  if (!TEXT_EXT.has(ext) && !NAME_ALLOW.has(base)) continue;

  const buf = readFileSync(p);
  let text;
  try {
    text = buf.toString('utf8');
    if (text.includes('\u0000')) throw new Error('binary');
    if (text.includes('\uFFFD')) throw new Error('non-utf8');
  } catch (e) {
    skipped.push(`${p} (${e.message})`);
    continue;
  }

  const inCyrScope = CYR_SCOPE.some((s) => p === s || p.startsWith(s));
  let latin = 0, cyr = 0, protLines = 0;
  const lines = text.split('\n');
  const out = lines.map((line) => {
    if (LINE_PROTECTS.some((re) => re.test(line))) { protLines++; return line; }
    let l = line;
    if (!FILE_PROTECT(p)) {
      l = l.replace(latinRe, (m) => { latin++; return latinMap(m); });
    }
    if (inCyrScope && !FILE_PROTECT(p)) {
      if (CYR_LINE_PROTECT.test(line)) { protLines++; return line; }
      for (const [re, to] of CYR_RULES) l = l.replace(re, () => { cyr++; return to; });
    }
    return l;
  }).join('\n');

  if (latin + cyr > 0) {
    changedFiles++; totalLatin += latin; totalCyr += cyr;
    report.push(`${p}\tlatin=${latin}\tcyr=${cyr}\tprotectedLines=${protLines}`);
    if (!DRY) writeFileSync(p, out, 'utf8');
  } else if (protLines > 0) {
    report.push(`${p}\tlatin=0\tcyr=0\tprotectedLines=${protLines}`);
  }
}

const summary = [
  DRY ? '=== DRY RUN (ничего не записано) ===' : '=== ЗАПИСАНО ===',
  `Файлов изменено: ${changedFiles}`,
  `Латинских замен: ${totalLatin}`,
  `Кириллических замен: ${totalCyr}`,
  `Пропущено (binary/non-utf8): ${skipped.length}`,
  ...skipped.map((s) => 'SKIP ' + s),
  '',
  ...report,
].join('\n');

writeFileSync('tools/rebrand-alephy-report.txt', summary + '\n', 'utf8');
console.log(summary.split('\n').slice(0, 8).join('\n'));
