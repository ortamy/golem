/* =============================================================
   codemod.mjs — механическая миграция сырых значений на токены
   (Этап 2 плана улучшения дизайна Research Lab)

   Принцип: ЗАМЕНА ТОЛЬКО ТОЧНЫХ СООТВЕТСТВИЙ.
   Вычисленное значение не меняется => пиксельный след равен нулю.
   Нешкальные значения (радиусы 3/5/7/8px, тексты 11/14px и т.п.)
   НЕ трогаются — их ревизия = намеренные правки этапов 5-7.

   Запуск:   node codemod.mjs             -> DRY RUN (только отчет)
             node codemod.mjs --apply     -> применить замены
             node codemod.mjs --only a,b  -> ограничить списком файлов
   ============================================================= */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/css';
const APPLY = process.argv.includes('--apply');
const onlyIdx = process.argv.indexOf('--only');
const ONLY = onlyIdx > -1 ? process.argv[onlyIdx + 1].split(',').map(s => s.trim()) : null;

// Не трогаем источник правды, точку сборки. theme-white.css ждёт Этап 9.
const SKIP = new Set(['tokens.css', 'lab.css', 'theme-white.css']);

const RADIUS_MAP = {
  '4px': '--radius-xs', '6px': '--radius-sm', '10px': '--radius-md',
  '14px': '--radius-lg', '20px': '--radius-xl', '999px': '--radius-pill'
};

// Полные нормализованные значения box-shadow => токен (light-палитра ДНК)
const SHADOW_MAP = {
  '0 1px 3px rgba(44,24,16,0.10), 0 2px 8px rgba(44,24,16,0.06)': '--shadow-card',
  '0 4px 12px rgba(44,24,16,0.14), 0 2px 4px rgba(44,24,16,0.08)': '--shadow-hover',
  '0 8px 24px rgba(44,24,16,0.20), 0 2px 8px rgba(44,24,16,0.10)': '--shadow-modal',
  '0 12px 32px rgba(44,24,16,0.24), 0 4px 12px rgba(44,24,16,0.12)': '--shadow-floating',
  '0 2px 12px rgba(44,24,16,0.10)': '--shadow-soft'
};

// Легаси-алиасы (значения не меняются; перевод на --dur-* — Этап 7)
const DUR_MAP = {
  '.15s': '--transition-fast', '0.15s': '--transition-fast', '150ms': '--transition-fast',
  '.2s': '--transition', '0.2s': '--transition', '200ms': '--transition'
};
const SAFE_EASINGS = new Set(['ease', 'ease-in-out']);
const stats = {};
const bump = k => stats[k] = (stats[k] || 0) + 1;

function listCss(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    if (name === 'components') { out.push(...listCss(join(dir, name))); continue; }
    if (name.endsWith('.css') && !SKIP.has(name)) out.push(join(dir, name));
  }
  return out;
}

function norm(v) { return v.replace(/\s+/g, '').replace(/,(?=\S)/g, ', '); }

// border-radius: только целые совпадения компонентов; %, calc, slash — мимо
function fixRadius(val) {
  if (!val || val.includes('/') || val.includes('%') || val.includes('calc')) return null;
  let changed = false;
  const fixed = val.split(/\s+/).map(p => {
    if (RADIUS_MAP[p]) { changed = true; return `var(${RADIUS_MAP[p]})`; }
    return p;
  }).join(' ');
  return changed ? fixed : null;
}

// transition: список через запятую "свойство длительность [easing]"
function fixTransition(raw) {
  const parts = raw.split(',').map(p => p.trim());
  let changed = false;
  const fixed = parts.map(part => {
    const pm = part.match(/^([a-zA-Z-]+)\s+([0-9.]+m?s)(?:\s+(ease|ease-in-out|linear))?$/);
    if (!pm) return part;
    const [, prop, dur] = pm;
    const token = DUR_MAP[dur];
    if (!token) return part;
    bump('transition ' + dur + '->' + token);
    changed = true;
    return `${prop} var(${token})`;
  });
  return changed ? parts.map((p, i) => fixed[i]).join(', ') : null;
}

// box-shadow: значение может быть многострочным — жадно до ';' или '}'
function fixShadowInSource(src) {
  return src.replace(/(\r?\n)([ \t]*)box-shadow:[ \t]*([\s\S]*?)(;|\}(?=\s*\r?\n))/g,
    (mm, nl, ind, bodyRaw, terminator) => {
      const imp = /!\s*important/.test(bodyRaw) ? ' !important' : '';
      const core = bodyRaw.replace(/!\s*important/g, '').replace(/\s+/g, ' ').trim();
      if (!core || core.startsWith('inset')) return mm;
      for (const [pattern, token] of Object.entries(SHADOW_MAP)) {
        if (norm(pattern) === norm(core)) {
          bump('shadow->' + token);
          return `${nl}${ind}box-shadow: var(${token})${imp}${terminator}`;
        }
      }
      return mm;
    });
}

// === Точные карты ступени 2b: spacing + типографика (значения не меняются) ===
const SPACE_MAP = {
  '4px': '--space-1', '8px': '--space-2', '12px': '--space-3', '16px': '--space-4',
  '20px': '--space-5', '24px': '--space-6', '32px': '--space-7', '48px': '--space-8'
};
const TEXT_MAP = {
  '12px': '--text-xs', '13px': '--text-sm', '15px': '--text-md', '16px': '--text-base',
  '18px': '--text-lg', '22px': '--text-xl', '28px': '--text-2xl', '38px': '--text-3xl'
};
const SPACE_PROPS = 'gap|row-gap|column-gap|padding|padding-top|padding-right|padding-bottom|padding-left|margin|margin-top|margin-right|margin-bottom|margin-left';

// поэлементная замена в составе значения ("14px 16px" -> "14px var(--space-4)")
function fixSpaceValue(val) {
  if (!val || /calc\(|%|auto|-/.test(val)) return null;
  let changed = false;
  const fixed = val.split(/\s+/).map(p => {
    if (SPACE_MAP[p]) { changed = true; return `var(${SPACE_MAP[p]})`; }
    return p;
  }).join(' ');
  return changed ? fixed : null;
}

function transform(src) {
  let out = src;

  // 1) border-radius (в т.ч. многокомпонентный: "6px 6px 0 0")
  out = out.replace(/(\r?\n)([ \t]*)border-radius:\s*([^;\r\n}]+)/g, (mm, nl, ind, val) => {
    const fixed = fixRadius(val.trim());
    if (!fixed) return mm;
    bump('radius');
    return `${nl}${ind}border-radius: ${fixed}`;
  });

  // 2) transition
  out = out.replace(/(\r?\n)([ \t]*)transition:\s*([^;\r\n}]+)/g, (mm, nl, ind, val) => {
    const fixed = fixTransition(val.trim());
    if (!fixed) return mm;
    return `${nl}${ind}transition: ${fixed}`;
  });

  // 3) letter-spacing .08em (обе формы записи)
  out = out.replace(/letter-spacing:\s*0?\.08em\b/g, () => {
    bump('tracking');
    return 'letter-spacing: var(--tracking-caps)';
  });

  // 4) box-shadow — последним из блока 2a (многострочный парсер)
  out = fixShadowInSource(out);

  // 5) spacing-свойства (поэлементно)
  const spaceRe = new RegExp(`(\\r?\\n)([ \\t]*)(${SPACE_PROPS}):\\s*([^;\\r\\n}]+)`, 'g');
  out = out.replace(spaceRe, (mm, nl, ind, prop, val) => {
    const fixed = fixSpaceValue(val.trim());
    if (!fixed) return mm;
    bump('space');
    return `${nl}${ind}${prop}: ${fixed}`;
  });

  // 6) font-size: только одиночные точные ступени шкалы
  out = out.replace(/(\r?\n)([ \t]*)font-size:\s*([0-9.]+px)\s*(?=;|\r?\n|\})/g, (mm, nl, ind, px) => {
    const tok = TEXT_MAP[px];
    if (!tok) return mm;
    bump('font-size ' + px);
    return `${nl}${ind}font-size: var(${tok})`;
  });

  // 7) line-height: два режима плотности (unitless, значения равны)
  out = out.replace(/(\r?\n)([ \t]*)line-height:\s*1\.5\s*(?=[;\r\n}])/g, (mm, nl, ind) => {
    bump('leading-ui');
    return `${nl}${ind}line-height: var(--leading-ui)`;
  });
  out = out.replace(/(\r?\n)([ \t]*)line-height:\s*1\.8\b\s*(?=[;\r\n}])/g, (mm, nl, ind) => {
    bump('leading-read');
    return `${nl}${ind}line-height: var(--leading-read)`;
  });

  return out;
}

const files = listCss(ROOT).filter(f => !ONLY || ONLY.some(o => f.endsWith(o)));
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
console.log(`\nФайлов к изменению: ${touched}/${files.length}`);
console.log('=== STATS ===');
console.log(Object.entries(stats).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}: ${v}`).join('\n') || '(пусто)');
if (!APPLY) console.log('\n(DRY RUN — добавь --apply для записи)');

