const fs = require('fs'); const cp = require('child_process');
fs.mkdirSync('docs/deployment/generated',{recursive:true});
const pkg = JSON.parse(fs.readFileSync('package.json','utf8'));
const git = 'current Git HEAD (run git rev-parse HEAD)';
const commands = Object.keys(pkg.scripts).filter(k=>k==='deploy'||k.startsWith('deploy:')||k.startsWith('docs:deployment')).sort().map(k=>`| npm run ${k} | ${pkg.scripts[k].replace(/\|/g,'\\|')} |`).join('\n');
fs.writeFileSync('docs/deployment/generated/COMMANDS.md', `# Generated deployment commands\n\nPackage version: ${pkg.version}\n\nLast verified commit: ${git}\n\n| Command | Implementation |\n|---|---|\n${commands}\n`);
fs.writeFileSync('docs/deployment/generated/CONFIGURATION_REFERENCE.md', `# Generated configuration reference\n\nSource schema: schemas/deployment-config.schema.json\n\nPublic files: config/deployment/sepolia.json and config/deployment/mainnet.json. Private files stay in .private/ and are ignored.\n`);
fs.writeFileSync('docs/deployment/COMMAND_CENTER.html', '<!doctype html><meta charset="utf-8"><title>GoalOS Deployment Command Center</title><h1>GoalOS Deployment Command Center</h1><p>This offline guide never collects, stores, or transmits secrets.</p><ol><li>Install: <code>npm ci</code></li><li>Start: <code>npm run deploy</code></li></ol>');
console.log('Deployment docs generated.');
