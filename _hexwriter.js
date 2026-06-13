const fs=require("fs");
const hex = process.argv[2];
const path = process.argv[3];
const buf = Buffer.from(hex, "hex");
fs.writeFileSync(path, buf, "utf8");
console.log("OK: "+path);