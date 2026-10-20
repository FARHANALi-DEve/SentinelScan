const fs = require('fs');
fs.mkdirSync('dist', { recursive: true });
fs.copyFileSync('src/styles.css','dist/styles.css');
fs.copyFileSync('index.html','dist/index.html');
console.log('SentinelScan static assets ready in frontend/dist/');
