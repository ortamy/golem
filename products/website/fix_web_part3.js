const fs = require('fs');
const pages = [
  'web/ru/research/index.html', 'web/en/research/index.html', 'web/he/research/index.html'
];

pages.forEach(function(fp) {
  let c = fs.readFileSync(fp, 'utf8');

  // Fix the link generation: use onclick with openResearchFile instead of href redirect
  c = c.replace(
    /a\.href = '\.\.\/\.\.\/index\.html#open=' \+ encodeURIComponent\(f\.path\);/g,
    `a.href = 'javascript:void(0)'; a.onclick = (function(p) { return function() { openResearchFile(p); }; })(f.path);`
  );

  // Add back button and content area before research-list
  if (!c.includes('id="back-to-list"')) {
    const backBtn = '<button id="back-to-list" onclick="backToList()" style="display:none;margin:0 auto 20px;padding:8px 16px;background:#b8860b;color:#faf3e0;border:none;border-radius:4px;cursor:pointer;font-family:EB Garamond,serif;font-size:14px;">← Назад к списку</button><div id="research-content" style="display:none;"></div>';
    c = c.replace('<div id="research-list">', backBtn + '<div id="research-list">');
  }

  // Add openResearchFile, parseSimpleMD, backToList functions
  if (!c.includes('function openResearchFile(')) {
    const fn = `
function openResearchFile(p) {
  var content = document.getElementById('research-content');
  content.innerHTML = '<div class="content"><h1>'+p.split('/').pop().replace('.md','')+'</h1><div class="md-body">Загрузка...</div></div>';
  content.style.display = 'block';
  document.getElementById('research-list').style.display = 'none';
  document.getElementById('research-search').style.display = 'none';
  document.getElementById('back-to-list').style.display = 'inline-block';
  window.scrollTo(0, 0);
  fetch('../../' + p)
    .then(function(r) { return r.text(); })
    .then(function(md) {
      var body = content.querySelector('.md-body');
      body.innerHTML = parseSimpleMD(md);
    })
    .catch(function() { content.querySelector('.md-body').innerHTML = '<p style="color:#c0392b">Error loading file</p>'; });
}
function parseSimpleMD(t) {
  t = t.replace(/^#+ (.+)$/gm, '<h2>$1</h2>');
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/\*(.+?)\*/g, '<em>$1</em>');
  t = t.replace(/`(.+?)`/g, '<code>$1</code>');
  t = t.replace(/\\n/g, '<br>');
  return t;
}
function backToList() {
  document.getElementById('research-content').style.display = 'none';
  document.getElementById('research-list').style.display = 'block';
  document.getElementById('research-search').style.display = 'block';
  document.getElementById('back-to-list').style.display = 'none';
  window.scrollTo(0, 0);
}
`;
    c = c.replace('</script>', fn + '\n</script>');
  }

  fs.writeFileSync(fp, c, 'utf8');
  console.log('Fixed research: ' + fp);
});
