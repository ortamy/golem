/* =============================================================
   compare.mjs — попиксельная сверка двух версий базлайна
   Запуск:  node compare.mjs v0 v1
   Логика:  pixelmatch с порогом --threshold (по умолч. 0.12)
            и допуском --max-diff (%% пикселей, по умолч. 0.5).
   Выход:   diff/<tagA>..tagB>/<theme>-<route>.png + отчет report.md
   Вердикт: OK / DRIFT (>max-diff %) / SIZE (разный размер кадра).
   ============================================================= */
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// === АРГУМЕНТЫ ===
const tagA = process.argv[2] || 'v0';
const tagB = process.argv[3] || 'v1';
const thresholdArgIdx = process.argv.indexOf('--threshold');
const maxDiffArgIdx = process.argv.indexOf('--max-diff');
const THRESHOLD = thresholdArgIdx > -1 ? parseFloat(process.argv[thresholdArgIdx + 1]) : 0.12;
const MAX_DIFF_PCT = maxDiffArgIdx > -1 ? parseFloat(process.argv[maxDiffArgIdx + 1]) : 0.5;

const THEMES = ['light', 'white', 'dark'];
// Полная матрица маршрутов (синхронна со screenshot.mjs)
const ROUTES = [
  'dashboard', 'manifest', 'states', 'dictionaries', 'researches',
  'timeline', 'scripture-reader', 'generators', 'cartography', 'learn', 'methodology'
];

const rows = [];
let driftCount = 0;

for (const theme of THEMES) {
  for (const route of ROUTES) {
    const fileA = join(__dirname, 'baseline', tagA, theme, `${route}.png`);
    const fileB = join(__dirname, 'baseline', tagB, theme, `${route}.png`);

    if (!existsSync(fileA) || !existsSync(fileB)) {
      // Кадр есть только в новом теге -> новая зона покрытия, не дрейф.
      if (!existsSync(fileA) && existsSync(fileB)) {
        rows.push({ theme, route, verdict: 'NEW-BASELINE', pct: null,
          note: 'маршрут добавлен в матрицу на этом теге' });
      } else {
        rows.push({ theme, route, verdict: 'MISSING', pct: null });
        driftCount++;
      }
      continue;
    }

    const imgA = PNG.sync.read(readFileSync(fileA));
    const imgB = PNG.sync.read(readFileSync(fileB));

    if (imgA.width !== imgB.width || imgA.height !== imgB.height) {
      // Разная высота fullPage — верстка изменила поток; фиксируем, решает ревьюер.
      rows.push({ theme, route, verdict: 'SIZE', pct: null,
        note: `A=${imgA.width}x${imgA.height} B=${imgB.width}x${imgB.height}` });
      driftCount++;
      continue;
    }

    const diff = new PNG({ width: imgA.width, height: imgA.height });
    const changed = pixelmatch(imgA.data, imgB.data, diff.data, imgA.width, imgA.height, { threshold: THRESHOLD });
    const pct = (changed / (imgA.width * imgA.height)) * 100;

    if (pct > MAX_DIFF_PCT) {
      const diffDir = join(__dirname, 'diff', `${tagA}..${tagB}`);
      mkdirSync(diffDir, { recursive: true });
      writeFileSync(join(diffDir, `${theme}-${route}.png`), PNG.sync.write(diff));
      driftCount++;
    }
    rows.push({ theme, route, verdict: pct > MAX_DIFF_PCT ? 'DRIFT' : 'OK', pct });
  }
}

// === ОТЧЁТ ===
const line = (r) => {
  const pctStr = r.pct === null ? '—' : r.pct.toFixed(4) + '%';
  return `| ${r.theme} | ${r.route} | ${r.verdict} | ${pctStr} | ${r.note || ''} |`;
};
const report = [
  `# Сверка базлайна ${tagA} → ${tagB}`,
  '',
  `- Порог различия пикселя (threshold): ${THRESHOLD}`,
  `- Допуск расхождений на кадр: ${MAX_DIFF_PCT}%`,
  `- Кадров с дрейфом/аномалиями: **${driftCount}/${rows.length}**`,
  `- Хит-карты дрейфа: tools/design-baseline/diff/${tagA}..${tagB}/`,
  '',
  '| Тема | Маршрут | Вердикт | Расхождение | Примечание |',
  '|---|---|---|---|---|',
  ...rows.map(line),
  '',
].join('\n');

const outMd = join(__dirname, 'diff', `${tagA}..${tagB}`, 'report.md');
mkdirSync(dirname(outMd), { recursive: true });
writeFileSync(outMd, report);
console.log(report);
console.log(`Отчёт: ${outMd}`);
process.exitCode = driftCount > 0 ? 2 : 0;
