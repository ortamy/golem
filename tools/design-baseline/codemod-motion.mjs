/* =============================================================
   codemod-motion.mjs — Этап 7: микровзаимодействия
   - legacy motion-tokens (--transition / --transition-fast) →
     комбо-токены motion с easing var(--ease-out)
   - durations анимаций fade/slide/-in ≥0.3s → var(--dur-2)
     (только settled-state сохраняется; spin/infinite/Pulse и пр. — нет)
   Сравнимо с кодемодом из этапа 2.
   ============================================================= */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/css';
const APPLY = process.argv.includes('--apply');
const SKIP = new Set(['tokens.css', 'lab.css', 'theme-white.css']); // tokens — источник motion-токенов

function listCss(dir) {
  const out = [];
  for (const n of readdirSync(dir)) {
    if (n === 'components') { out.push(...listCss(join(dir, n))); continue; }
    if (n.endsWith('.css') && !SKIP.has(n)) out.push(join(dir, n));
  }
  return out;
}
const stats = {};
const bump = k => stats[k] = (stats[k] || 0) + 1;

function transform(src) {
  let out = src;

  // R1: legacy motion-tokens → комбо (lookahead [,)] охватывает fallback-форму)
  out = out.replace(/var\(\s*--transition-fast(?=[,)])/g, () => { bump('motion-fast'); return 'var(--motion-fast'; });
  out = out.replace(/var\(\s*--transition(?=[,)])/g,    () => { bump('motion-base'); return 'var(--motion-base'; });

  // R2: анимационные durations для fade/slide/-in → var(--dur-2)
  //     (перехватываем только строки без infinite; имена без fade/-in в конце — мимо)
  out = out.replace(/^(.*animation:\s*)([\w-]+)(\s+)((?:0?\.\d+|1)\d*s)(.*)$/gm, (m, pre, name, gap, dur, rest) => {
    if (rest.includes('infinite')) return m;
    if (!/fade|(?:^|[-])in$/i.test(name)) return m;
    const d = parseFloat(dur);
    if (Number.isNaN(d) || d < 0.28) return m;   // микровзаимодействия побыстрее, но не < 0.28s без причин
    bump('anim ' + name + '@' + dur);
    return `${pre}${name}${gap}var(--dur-2)${rest}`;
  });

  return out;
}

const files = listCss(ROOT);
let touched = 0;
for (const path of files) {
  const src = readFileSync(path, 'utf8');
  const out = transform(src);
  if (out !== src) {
    touched++;
    const name = path.split(/[\\/]/).pop();
    console.log(`${APPLY ? '[WRITE]' : '[DIFF ]'} ${name}`);
    if (APPLY) writeFileSync(path, out);
  }
}
console.log('\nФайлов к изменению: ' + touched + '/' + files.length);
console.log('=== STATS ===');
console.log(Object.entries(stats).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ': ' + v).join('\n') || '(пусто)');
if (!APPLY) console.log('\n(DRY RUN — добавь --apply для записи)');

