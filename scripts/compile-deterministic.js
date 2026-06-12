#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const solc = require('solc');
const root = path.resolve(__dirname, '..');
const pkg = require(path.join(root, 'package.json'));
console.log(`Deterministic Solidity compile using local solc-js ${solc.version()} (package solc ${pkg.dependencies?.solc || pkg.devDependencies?.solc}).`);
for (const dir of ['artifacts','cache','direct-solc-output']) {
  fs.rmSync(path.join(root, dir), { recursive: true, force: true });
}
let r = spawnSync(process.execPath, [path.join(root, 'scripts/direct-solc-compile.js')], { cwd: root, stdio: 'inherit', env: { ...process.env, HARDHAT_DISABLE_DOWNLOADS: 'true' }});
if (r.status !== 0) process.exit(r.status || 1);
r = spawnSync(process.execPath, [path.join(root, 'scripts/generate-hardhat-artifacts-from-solc.js')], { cwd: root, stdio: 'inherit' });
if (r.status !== 0) process.exit(r.status || 1);
console.log('compile:deterministic completed without Hardhat compiler download.');
