const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 8081;
const WEB_DIR = __dirname;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
};

const server = http.createServer((req, res) => {
  let filePath = req.url === "/" ? "/index.html" : req.url;
  const fullPath = path.join(WEB_DIR, filePath);

  if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) {
    res.writeHead(404);
    res.end("Not found");
    return;
  }

  const ext = path.extname(fullPath);
  const mimeType = MIME[ext] || "application/octet-stream";
  const content = fs.readFileSync(fullPath);
  res.writeHead(200, { "Content-Type": mimeType });
  res.end(content);
});

server.listen(PORT, () => {
  console.log(`\n  GOLEM web-v2 запущен: http://localhost:${PORT}/\n`);
});