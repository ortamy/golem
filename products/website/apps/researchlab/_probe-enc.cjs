const fs = require('node:fs');
const src = fs.readFileSync('tests/smoke.spec.js', 'utf8');
const attrMatches = [...src.matchAll(/data-root-id="([^"]*)"/g)];
for (const m of attrMatches) {
  const cps = [...m[1]].map((c) => c.codePointAt(0).toString(16)).join(' ');
  console.log('ATTR', JSON.stringify(m[1]), '=>', cps);
}
const qsa = [...src.matchAll(/waitForSelector\((`[^`]*`|'[^']*')/g)];
for (const m of qsa.slice(0, 10)) {
  const cps = [...m[1]].map((c) => c.codePointAt(0)).filter((c) => c > 0x7f).map((c) => c.toString(16));
  console.log('WAITSEL', cps.join(' ') || 'ascii-only');
}
const suspicious = [...src].map((c) => c.codePointAt(0)).filter((c) => (c >= 0x200b && c <= 0x200f) || c === 0xfeff || c === 0x00a0);
console.log('SUSPICIOUS-CHARS', suspicious.length ? suspicious.map((c) => c.toString(16)).join(' ') : 'none');
