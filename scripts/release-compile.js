#!/usr/bin/env node
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
function run(args) {
  return spawnSync(process.platform === 'win32' ? 'npm.cmd' : 'npm', args, { cwd: root, encoding: 'utf8', stdio: 'pipe', env: { ...process.env, HARDHAT_DISABLE_DOWNLOADS: 'true' } });
}
function digestArtifacts() {
  const base = path.join(root, 'artifacts', 'contracts');
  const out = [];
  function walk(dir) {
    if (!fs.existsSync(dir)) return;
    for (const ent of fs.readdirSync(dir, { withFileTypes: true }).sort((a,b)=>a.name.localeCompare(b.name))) {
      const p = path.join(dir, ent.name);
      if (ent.isDirectory()) walk(p);
      else if (ent.name.endsWith('.json') && !ent.name.endsWith('.dbg.json')) {
        const j = JSON.parse(fs.readFileSync(p, 'utf8'));
        out.push({ file: path.relative(root, p), bytecode: crypto.createHash('sha256').update(j.bytecode || '').digest('hex'), runtime: crypto.createHash('sha256').update(j.deployedBytecode || '').digest('hex') });
      }
    }
  }
  walk(base);
  return crypto.createHash('sha256').update(JSON.stringify(out)).digest('hex');
}
const first = run(['run', 'compile:ci']);
const output = `${first.stdout || ''}${first.stderr || ''}`;
process.stdout.write(output);
if (first.status !== 0) process.exit(first.status || 1);
if (/^(WARNING|ERROR):/m.test(output)) {
  console.error('release:compile blocked: compiler output contained project warning/error text.');
  process.exit(1);
}
const d1 = digestArtifacts();
const second = run(['run', 'compile:ci']);
const output2 = `${second.stdout || ''}${second.stderr || ''}`;
process.stdout.write(output2);
if (second.status !== 0) process.exit(second.status || 1);
if (/^(WARNING|ERROR):/m.test(output2)) {
  console.error('release:compile blocked: second compiler output contained project warning/error text.');
  process.exit(1);
}
const d2 = digestArtifacts();
const mismatch = d1 === d2 ? 0 : 1;
const report = { schemaVersion:'1.0', command:'npm run release:compile', warnings:0, bytecodeMismatch:mismatch, artifactDigest:d2, generatedAt:new Date().toISOString(), claimBoundary:'Local deterministic compile evidence only; no deployment or verification claim.' };
fs.mkdirSync(path.join(root, 'qa', 'release'), { recursive: true });
fs.writeFileSync(path.join(root, 'qa', 'release', 'compile-report.json'), JSON.stringify(report, null, 2) + '\n');
console.log('COMPILE_PASS');
console.log('warnings: 0');
console.log(`bytecodeMismatch: ${mismatch}`);
if (mismatch) process.exit(1);
