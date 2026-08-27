// metrics.mjs — остаточный хаос после кодемода (сырьё vs токены)
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/css';
const SKIP = new Set(['lab.css', 'theme-white.css']);

function listCss(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    if (name === 'components') { out.push(...listCss(join(dir, name))); continue; }
    if (name.endsWith('.css')) out.push(join(dir, name));
  }
  return out;
}

const m = {
  radiusRaw: 0, radiusVar: 0,
  shadowRaw: 0, shadowVar: 0,
  fontRaw: 0, fontVar: 0,
  spaceRaw: 0, spaceVar: 0,
  transVar: 0, transRawDur: 0
};

for (const f of listCss(ROOT)) {
  const src = readFileSync(f, 'utf8');
  const name = f.split(/[\\/]/).pop();
  const isTokens = name === 'tokens.css';

  // радиусы
  let x = src.match(/border-radius:\s*[^;\r\n}]+/g) || [];
  for (const d of x) { if (d.includes('var(--radius')) m.radiusVar++; else if (!isTokens) m.radiusRaw++; }

  // тени: декларации, начинающиеся не с var/none/inset и содержащие длину
  x = src.match(/box-shadow:\s*([^;}]+)/g) || [];
  for (const d of x) {
    const v = d.replace(/^box-shadow:\s*/, '').trim();
    if (v.startsWith('var(') || /^var\(/.test(v)) m.shadowVar++;
    else if (v === 'none' || v.startsWith('inset') === false && /\dpx/.test(v) && !v.includes('var(--shadow')) { if (!isTokens && !v.startsWith('none')) m.shadowRaw++; }
  }

  // размеры шрифта
  x = src.match(/font-size:\s*([^;\r\n}]+)/g) || [];
  for (const d of x) { if (d.includes('var(--text')) m.fontVar++; else if (/\d/.test(d) && !isTokens) m.fontRaw++; }

  // spacing-свойства с сырыми px
  x = src.match(/(?:^|[^-])\b(?:gap|padding|margin)(?:-\w+)?:\s*([^;\r\n}]+)/gm) || [];
  for (const d of x) {
    const val = d.split(':')[1] || '';
    const hasPx = /\b\d+px\b/.test(val);
    const hasVar = /var\(--space/.test(val);
    if (hasPx && !hasVar) m.spaceRaw++;
    else if (hasVar) m.spaceVar++;
  }

  // переходы
  x = src.match(/transition:[^;\r\n}]+/g) || [];
  for (const d of x) {
    if (/var\(--(transition|dur)/.test(d)) m.transVar++;
    else if (/\d*\.?\d+m?s\b/.test(d)) m.transRawDur++;
  }
}

console.log('radius   : raw', m.radiusRaw, '| var', m.radiusVar);
console.log('shadow   : raw', m.shadowRaw, '| var-start', m.shadowVar);
console.log('font     : raw', m.fontRaw, '| var', m.fontVar);
console.log('space    : raw-only', m.spaceRaw, '| var-mixed', m.spaceVar);
console.log('transit  : var', m.transVar, '| raw-duration', m.transRawDur);
