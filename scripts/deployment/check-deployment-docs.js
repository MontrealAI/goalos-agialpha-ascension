const fs = require('fs'); const cp = require('child_process');
cp.spawnSync(process.execPath,['scripts/deployment/build-deployment-docs.js'],{stdio:'inherit'});
const required = ['docs/deployment/00_START_HERE.md','docs/deployment/README.md','docs/deployment/generated/COMMANDS.md','docs/deployment/COMMAND_CENTER.html'];
let ok = true; for (const f of required) { if (!fs.existsSync(f)) { console.error('Missing', f); ok=false; } }
const text = required.filter(f=>fs.existsSync(f)).map(f=>fs.readFileSync(f,'utf8')).join('\n');
if (!text.includes('npm run deploy')) { console.error('Missing npm run deploy docs'); ok=false; }
if (/0x[a-fA-F0-9]{64}|PRIVATE_KEY=0x[a-fA-F0-9]{64}|https?:\/\/[^\s]*[A-Za-z0-9]{24}/.test(text)) { console.error('Secret-looking literal in deployment docs'); ok=false; }
process.exit(ok?0:1);
