/* =============================================================
   scan-layout.mjs — инвентаризация каркаса (Этап 5)

   Различает:
   - МЕДИА-УСЛОВИЕ: max-width внутри @media(...) — брейкпоинт, не трогать
   - ДЕКЛАРАЦИЯ: свойство в правиле — кандидат на ярусы ширины
   Плюс: все правила с селектором h1 и их font-size.

   Запуск: node scan-layout.mjs [--files a.css,b.css]
   ============================================================= */
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/css';
const SKIP = new Set(['tokens.css', 'lab.css', 'theme-white.css']);
const onlyIdx = process.argv.indexOf('--files');
const ONLY = onlyIdx > -1 ? process.argv[onlyIdx + 1].split(',').map(s => s.trim()) : null;

const files = [];
for (const name of readdirSync(ROOT)) {
  if (name === 'components') continue;
  if (name.endsWith('.css') && !SKIP.has(name)) files.push(join(ROOT, name));
}

const declWidths = new Map();   // "Npx" -> [файл:селектор]
const h1Rules = [];

for (const path of files) {
  const src = readFileSync(path, 'utf8');
  const file = path.split(/[\\/]/).pop();
  if (ONLY && !ONLY.includes(file)) continue;

  // --- ширины: отделяем медиа-условия от деклараций ---
  const re = /(max-width|min-width)\s*:\s*(\d+)px/g;
  let m;
  while ((m = re.exec(src))) {
    const before = src.slice(Math.max(0, m.index - 12), m.index);
    if (/[(\s]$/.test(before.trimEnd()) === false || /\(\s*$/.test(before)) {
      // условие: сразу перед ним открывающая скобка @media ( ...
      continue;
    }
  }
  // надёжнее вторым проходом: декларация = "prop: Npx;" НЕ следующим за "("
  const reDecl = /(^|[;{\s])(max-width)\s*:\s*(\d+)px/g;
  while ((m = reDecl.exec(src))) {
    const prev = src.slice(0, m.index);
    const openParen = prev.lastIndexOf('(');
    const closeParen = prev.lastIndexOf(')');
    if (openParen > closeParen) continue;       // мы внутри (@media (...) — условие
    // селектор = текст между последней '}' и ближайшей '{' перед декларацией
    const openBrace = prev.lastIndexOf('{');
    const closeBrace = prev.lastIndexOf('}');
    const sel = openBrace > closeBrace
      ? prev.slice(closeBrace + 1, openBrace).replace(/\r?\n/g, ' ').trim().slice(-90)
      : '?';
    const key = m[3] + 'px';
    if (!declWidths.has(key)) declWidths.set(key, []);
    declWidths.get(key).push(`${file} :: ${sel}`);
  }

  // --- правила с h1 ---
  const ruleRe = /([^{}]*\bh1\b[^{}]*)\{([^}]*)\}/g;
  while ((m = ruleRe.exec(src))) {
    const szM = m[2].match(/font-size\s*:\s*([^;}]+)/);
    const lhM = m[2].match(/line-height\s*:\s*([^;}]+)/);
    h1Rules.push({
      file,
      line: src.slice(0, m.index).split('\n').length,
      sel: m[1].replace(/\r?\n/g, ' ').trim(),
      size: szM ? szM[1].trim() : '—',
      lh: lhM ? lhM[1].trim() : ''
    });
  }
}

const out = [];
out.push('=== ДЕКЛАРАЦИИ width/max-width (не медиа) ===');
for (const [w, list] of [...declWidths.entries()].sort((a, b) => parseInt(a[0]) - parseInt(b[0]))) {
  out.push(`\n${list.length} x ${w}`);
  for (const s of list.slice(0, 30)) out.push('   ' + s);
}
out.push('\n=== ПРАВИЛА h1 ===');
for (const r of h1Rules.sort((a, b) => a.file.localeCompare(b.file))) {
  out.push(`${r.file.padEnd(26)} L${String(r.line).padEnd(5)} ${r.size.padEnd(10)} ${r.lh.padEnd(6)} ${r.sel.slice(0, 52)}`);
}
writeFileSync(join('c:/Users/DELL/Desktop/golem-main/tools/design-baseline', 'scan-layout-report.txt'), out.join('\n'), 'utf8');
console.log('OK -> scan-layout-report.txt');
