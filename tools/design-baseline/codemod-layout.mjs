/* =============================================================
   codemod-layout.mjs — Этап 5: консолидация каркасов на токены.
   Каждая пара «файл -> значение» выверена против scan-layout-report.txt:
   в границах файла целевое значение встречается ровно у shell-селектора.
   Гвардия контекста: предыдущий символ { или ; или начало строки с пробелом —
   @media (max-width: ...) имеет '(' и не совпадает.
   Запуск: node codemod-layout.mjs           (dry run)
           node codemod-layout.mjs --apply
   ============================================================= */
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/css';
const APPLY = process.argv.includes('--apply');

// файл => { старое значение => токен }
const PLAN = {
  'layout.css':               { '1400px': '--shell-frame' },
  'exposure-editor.css':      { '1400px': '--shell-frame' },
  'cartography.css':          { '1480px': '--shell-wide' },
  'heraldry.css':             { '1480px': '--shell-wide' },
  'states.css':               { '1480px': '--shell-wide', '1080px': '--shell-page' },
  'agent-server.css':         { '1040px': '--shell-page' },
  'investigation.css':        { '1060px': '--shell-page' },
  'generators-checkers.css':  { '1080px': '--shell-page' },
  'manifest.css':             { '1080px': '--shell-page', '1180px': '--shell-page' },
  'learn.css':                { '1120px': '--shell-page' },
  'linguistic-tensor.css':    { '1120px': '--shell-page' },
  'translation-comparator.css': { '1120px': '--shell-page' },
  'analyzers.css':            { '1180px': '--shell-page' },
  'clue-generator.css':       { '1180px': '--shell-page' },
  'methodology.css':          { '1180px': '--shell-page' },
  'paleo-glossary.css':       { '1180px': '--shell-page' },
  'prompt-generator.css':     { '1240px': '--shell-page' },
  'scripture-reader.css':     { '1000px': '--shell-read' }
};

let total = 0;
for (const [file, map] of Object.entries(PLAN)) {
  const p = join(ROOT, file);
  let src = readFileSync(p, 'utf8');
  const hits = [];
  for (const [val, token] of Object.entries(map)) {
    // только декларации ({ или ; или перенос строки перед max-width)
    const re = new RegExp(`([{;\\r\\n][ \\t]*)max-width:[ \\t]*${val.replace('.', '\\.')}`, 'g');
    src = src.replace(re, (mm, pre) => {
      hits.push(`${token} <- ${val}`);
      return `${pre}max-width: var(${token})`;
    });
  }
  if (hits.length) {
    total += hits.length;
    console.log(`${file}: ${hits.length} -> ${[...new Set(hits)].join(', ')}`);
    if (APPLY) writeFileSync(p, src);
  } else {
    console.log(`${file}: СОВПАДЕНИЙ НЕТ (!!)`);
  }
}
console.log(`\nИтого сайтов: ${total} (ожидается 20). ${APPLY ? 'ЗАПИСАНО.' : '(dry run)'}`);
