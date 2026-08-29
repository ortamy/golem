const fs = require('fs');
const f = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/js/timeline.js';
let s = fs.readFileSync(f, 'utf8');

const before = "'<div\\\\ class=\"tl-detail-title\">'\\\\ \\\\+\\\\ escapeHtml\\\\(timeline\\\\.title\\\\)\\\\ \\\\+\\\\ '</div>'\\\\ \\\\+";
const after  = "'<div class=\"tl-detail-title\">' + escapeHtml(timeline.title) + '</div>' +";

let ok = false;
if (s.includes(after)) {
  console.log('timeline.js: already correct');
  ok = true;
}
if (!ok && s.includes(before)) {
  s = s.replace(before, after);
  fs.writeFileSync(f, s, 'utf8');
  console.log('timeline.js: fixed');
} else if (!ok) {
  console.log('NOT FOUND - dumping L175:');
  const lines = s.split('\n');
  console.log(lines[174]);
}


