// dupcheck.mjs — повторяющиеся простые селекторы внутри одного файла
// (кандидаты на "осколки" вроде scripture-reader .scripture-navigation .lab-btn x4)
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/css';
const SKIP = new Set(['tokens.css', 'lab.css']);

function listCss(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    if (name === 'components') { out.push(...listCss(join(dir, name))); continue; }
    if (name.endsWith('.css') && !SKIP.has(name)) out.push(join(dir, name));
  }
  return out;
}

for (const f of listCss(ROOT)) {
  const src = readFileSync(f, 'utf8').replace(/\r/g, '');
  const name = f.split(/[\\/]/).pop();
  //Strip comments
  const noComments = src.replace(/\/\*[\s\S]*?\*\//g, '');
  // Count simple standalone selectors like ".a .b {" appearing as own rule head
  const counts = {};
  const re = /^([.#][\w-]+(?:\s*[>~+\s][.#]?[\w()-]+)*)\s*\{/gm;
  let mm;
  while ((mm = re.exec(noComments))) {
    const sel = mm[1].trim();
    counts[sel] = (counts[sel] || 0) + 1;
  }
  const dups = Object.entries(counts).filter(([, n]) => n >= 2);
  if (dups.length) {
    console.log(`-- ${name}`);
    for (const [sel, n] of dups.sort((a, b) => b[1] - a[1]).slice(0, 12)) console.log(`   x${n}  ${sel}`);
  }
}
