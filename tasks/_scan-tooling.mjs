// Временный сканер для design-consistency аудита лаба (Этап 1, read-only).
// Запуск: node tasks/_scan-tooling.mjs -> tasks/_audit-raw.txt / _audit-raw.json
import fs from 'node:fs';
import path from 'node:path';

const ROOT = 'C:/Users/DELL/Desktop/alephy/products/website/apps/researchlab';
const OUT_TXT = 'C:/Users/DELL/Desktop/alephy/tasks/_audit-raw.txt';
const OUT_JSON = 'C:/Users/DELL/Desktop/alephy/tasks/_audit-raw.json';
const SKIP_DIRS = new Set(['node_modules', 'libs', 'vendor']);

function walk(dir, exts, acc = []) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return acc; }
  for (const e of entries) {
    if (SKIP_DIRS.has(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, exts, acc);
    else if (exts.some((x) => e.name.endsWith(x))) acc.push(p);
  }
  return acc;
}
const rel = (p) => path.relative(ROOT, p).replaceAll('\\', '/');

const cssFiles = walk(path.join(ROOT, 'css'), ['.css']);
const htmlFiles = [path.join(ROOT, 'index.html'), ...walk(path.join(ROOT, 'pages'), ['.html'])];
const jsFiles = walk(path.join(ROOT, 'js'), ['.js']);

const table = new Map();
function norm(v) {
  return String(v)
    .replace(/!important/gi, '')
    .replace(/#[0-9a-fA-F]{3,8}\b/g, (m) => m.toLowerCase())
    .replace(/\s+/g, ' ')
    .trim();
}
function add(prop, value, file) {
  const v = norm(value);
  if (!v) return;
  const key = `${prop}::${v}`;
  let e = table.get(key);
  if (!e) { e = { prop, value: v, count: 0, files: new Map() }; table.set(key, e); }
  e.count++;
  e.files.set(file, (e.files.get(file) || 0) + 1);
}

const CSS_PROPS = [
  'box-shadow', 'text-shadow', 'backdrop-filter',
  'border-radius', 'z-index', 'font-size',
  'padding', 'margin', 'gap',
  'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'padding-inline', 'padding-block', 'margin-inline', 'margin-block',
  'row-gap', 'column-gap',
];
const propRes = CSS_PROPS.map((p) => [p, new RegExp(`(?:^|[;{\\s(])${p}\\s*:\\s*([^;{}]+)`, 'gi')]);

for (const f of cssFiles) {
  const text = fs.readFileSync(f, 'utf8');
  const name = rel(f);
  for (const [prop, re] of propRes) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text))) add(prop, m[1], name);
  }
  for (const m of text.matchAll(/#[0-9a-fA-F]{3,8}\b/g)) add('color-hex', m[0], name);
  for (const m of text.matchAll(/\b(?:rgba|hsla?)\([^)]+\)/g)) add('color-func', m[0], name);
}
// ---------- правила (max-width/контейнеры) и @media ----------
const maxWidthRules = [];
const mediaQueries = new Map();
for (const f of cssFiles) {
  const text = fs.readFileSync(f, 'utf8');
  const name = rel(f);
  for (const m of text.matchAll(/@media[^{]+/g)) {
    const q = norm(m[0].replace('@media', ''));
    if (!q) continue;
    let e = mediaQueries.get(q);
    if (!e) { e = { value: q, count: 0, files: new Map() }; mediaQueries.set(q, e); }
    e.count++;
    e.files.set(name, (e.files.get(name) || 0) + 1);
  }
  const re = /([^{}]+)\{([^{}]*)\}/g;
  let m;
  while ((m = re.exec(text))) {
    const sel = m[1].split('}').pop().trim();
    const body = m[2];
    const mw = body.match(/max-width\s*:\s*([^;}]+)/);
    if (mw) maxWidthRules.push({ file: name, selector: sel, value: norm(mw[1]), hasAuto: /margin[^;}]*auto/.test(body) });
  }
}

// ---------- inline-стили в JS/HTML ----------
const inlineTable = new Map();
function addInline(prop, value, file) {
  const p = String(prop).trim().toLowerCase();
  const v = norm(value);
  if (!p || !v) return;
  const key = `${p}::${v}`;
  let e = inlineTable.get(key);
  if (!e) { e = { prop: p, value: v, count: 0, files: new Map() }; inlineTable.set(key, e); }
  e.count++;
  e.files.set(file, (e.files.get(file) || 0) + 1);
}
for (const f of [...htmlFiles, ...jsFiles]) {
  const text = fs.readFileSync(f, 'utf8');
  const name = rel(f);
  for (const m of text.matchAll(/style\s*=\s*(["'])(.*?)\1/gs)) {
    for (const decl of m[2].split(';')) {
      const i = decl.indexOf(':');
      if (i > 0) addInline(decl.slice(0, i), decl.slice(i + 1), name);
    }
  }
  for (const m of text.matchAll(/\.style\.([A-Za-z]+)\s*=\s*(["'])(.*?)\2/g)) {
    const prop = m[1].replace(/[A-Z]/g, (c) => '-' + c.toLowerCase());
    addInline(prop, m[3], name);
  }
  for (const m of text.matchAll(/setProperty\(\s*(["'])(--[\w-]+)\1\s*,\s*(["'])(.*?)\3/g)) {
    addInline('setProperty:' + m[2], m[4], name);
  }
}
// ---------- токены: определения, использование, lab-container ----------
const tokenDefs = new Map();
const tokenUse = new Map();
for (const f of cssFiles) {
  const text = fs.readFileSync(f, 'utf8');
  for (const m of text.matchAll(/(--[\w-]+)\s*:\s*([^;{}]+)[;}]/g)) {
    const n = m[1];
    if (!tokenDefs.has(n)) tokenDefs.set(n, { value: norm(m[2]), files: new Set() });
    tokenDefs.get(n).files.add(rel(f));
  }
  for (const m of text.matchAll(/var\((--[\w-]+)/g)) tokenUse.set(m[1], (tokenUse.get(m[1]) || 0) + 1);
}
const labContainerUses = new Map();
for (const f of [...cssFiles, ...htmlFiles, ...jsFiles]) {
  const text = fs.readFileSync(f, 'utf8');
  const n = (text.match(/lab-container/g) || []).length;
  if (n) labContainerUses.set(rel(f), n);
}

// ---------- вывод ----------
const entries = [...table.values()];
const byProp = (p) => entries.filter((e) => e.prop === p).sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));
const fmt = (list, cap = 400) => list.slice(0, cap).map((e) => {
  const top = [...e.files.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6).map(([f, c]) => `${f}(${c})`).join(', ');
  const more = e.files.size > 6 ? ` +${e.files.size - 6} файлов` : '';
  return `${String(e.count).padStart(4)}x  ${e.value}\n        ${top}${more}`;
}).join('\n');

const L = [];
const push = (s = '') => L.push(s);
push('=== SUMMARY (CSS, объявления) ===');
push('prop            | decls | unique | from-var | literal');
let totalDecl = 0;
for (const p of CSS_PROPS.concat(['color-hex', 'color-func'])) {
  const list = byProp(p);
  if (!list.length) continue;
  const decls = list.reduce((s, e) => s + e.count, 0);
  const fromVar = list.filter((e) => e.value.startsWith('var(')).reduce((s, e) => s + e.count, 0);
  totalDecl += decls;
  push(`${p.padEnd(15)} | ${String(decls).padStart(5)} | ${String(list.length).padStart(6)} | ${String(fromVar).padStart(8)} | ${String(decls - fromVar).padStart(7)}`);
}
push(`TOTAL: ${totalDecl}`);
push('');
push('=== box-shadow: значения ===');
push(fmt(byProp('box-shadow')));
push('');
push('=== box-shadow: форма (цвет вырезан) ===');
const shapeMap = new Map();
for (const e of byProp('box-shadow')) {
  const shape = e.value.replace(/rgba?\([^)]*\)|hsla?\([^)]*\)|#[0-9a-fA-F]{3,8}|var\([^)]*\)|rgb\([^)]*\)/gi, 'C').replace(/\s+/g, ' ').trim();
  let s = shapeMap.get(shape);
  if (!s) { s = { shape, count: 0, variants: new Set() }; shapeMap.set(shape, s); }
  s.count += e.count;
  s.variants.add(e.value);
}
push([...shapeMap.values()].sort((a, b) => b.count - a.count).map((s) => `${String(s.count).padStart(4)}x  ${s.shape}  [цветовых вариантов: ${s.variants.size}]`).join('\n'));
push('');
push('=== text-shadow ===');
push(fmt(byProp('text-shadow'), 25));
push('');
push('=== backdrop-filter ===');
push(fmt(byProp('backdrop-filter'), 25));
push('');
push('=== border-radius ===');
push(fmt(byProp('border-radius')));
push('');
push('=== z-index ===');
push(fmt(byProp('z-index')));
push('');
push('=== font-size ===');
push(fmt(byProp('font-size')));
push('');
for (const p of CSS_PROPS.slice(7)) {
  const list = byProp(p);
  if (!list.length) continue;
  push(`=== ${p} ===`);
  push(fmt(list, 40));
  push('');
}
push('=== цвета: hex ===');
push(fmt(byProp('color-hex'), 120));
push('');
push('=== цвета: rgb/hsl ===');
push(fmt(byProp('color-func'), 80));
push('');
push('=== max-width ===');
const mwGroup = new Map();
for (const r of maxWidthRules) {
  if (!/px|rem|ch|%|em/.test(r.value)) continue;
  let g = mwGroup.get(r.value);
  if (!g) { g = { value: r.value, count: 0, files: new Map(), sels: new Map() }; mwGroup.set(r.value, g); }
  g.count++;
  g.files.set(r.file, (g.files.get(r.file) || 0) + 1);
  const key = r.selector.length > 70 ? r.selector.slice(0, 67) + '...' : r.selector;
  g.sels.set(key, (g.sels.get(key) || 0) + 1);
}
for (const g of [...mwGroup.values()].sort((a, b) => parseFloat(b.value) - parseFloat(a.value))) {
  const top = [...g.files.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([f, c]) => `${f}(${c})`).join(', ');
  push(`${String(g.count).padStart(3)}x  max-width: ${g.value}  [${top}]`);
  for (const [s, c] of [...g.sels.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4)) push(`        ${c}x  ${s}`);
}
push('');
push('=== @media breakpoints ===');
push([...mediaQueries.values()].sort((a, b) => b.count - a.count).map((e) => `${String(e.count).padStart(3)}x  ${e.value}  [${[...e.files.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5).map(([f, c]) => `${f}(${c})`).join(', ')}]`).join('\n'));
push('');
push('=== inline-стили JS/HTML ===');
const inlineByProp = new Map();
for (const e of inlineTable.values()) {
  const base = e.prop.startsWith('setProperty') ? 'setProperty(--var)' : e.prop;
  if (!inlineByProp.has(base)) inlineByProp.set(base, []);
  inlineByProp.get(base).push(e);
}
for (const [p, list] of [...inlineByProp.entries()].sort((a, b) => b[1].length - a[1].length)) {
  const decls = list.reduce((s, e) => s + e.count, 0);
  push(`--- ${p} (${decls}x, ${list.length} unique) ---`);
  push(fmt(list.sort((a, b) => b.count - a.count), 25));
}
push('');
push('=== токены: определения (все) ===');
for (const [n, d] of [...tokenDefs.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
  push(`${n} = ${d.value}  [${[...d.files].join(',')}]`);
}
push('');
push('=== токены: top-60 по использованию ===');
push([...tokenUse.entries()].sort((a, b) => b[1] - a[1]).slice(0, 60).map(([n, c]) => `${String(c).padStart(4)}x  ${n}`).join('\n'));
push('');
push('=== lab-container ===');
push(labContainerUses.size ? [...labContainerUses.entries()].map(([f, c]) => `${String(c).padStart(3)}x  ${f}`).join('\n') : '(нет)');

fs.writeFileSync(OUT_TXT, L.join('\n'), 'utf8');
fs.writeFileSync(OUT_JSON, JSON.stringify({
  declarations: [...table.values()].map((e) => ({ ...e, files: [...e.files.entries()] })),
  inline: [...inlineTable.values()].map((e) => ({ ...e, files: [...e.files.entries()] })),
  maxWidth: maxWidthRules,
  media: [...mediaQueries.values()].map((e) => ({ ...e, files: [...e.files.entries()] })),
  tokens: { defs: [...tokenDefs.entries()].map(([n, d]) => [n, d.value, [...d.files]]), use: [...tokenUse.entries()] },
  labContainer: [...labContainerUses.entries()],
}, null, 1), 'utf8');
console.log('done. entries:', table.size, 'inline:', inlineTable.size, 'maxWidth:', maxWidthRules.length, 'tokens:', tokenDefs.size);



