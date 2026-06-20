#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const root = path.resolve(__dirname, '..');
const scanPaths = ['config/deployment/mainnet.json','scripts/verification/fixtures/sepolia-v1-regression-manifest.json','schemas/deployment-mainnet-template.schema.json','schemas/deployment-mainnet-runtime.schema.json'].join(':');
const scanner = () => spawnSync(process.platform === 'win32' ? 'npm.cmd' : 'npm', ['run', 'repo:no-private-operator-data'], { cwd: root, encoding: 'utf8', env: { ...process.env, NO_PRIVATE_OPERATOR_SCAN_PATHS: scanPaths } });
const must = (cond, msg) => { if (!cond) { console.error(msg); process.exit(1); } };
const mainnet = path.join(root, 'config/deployment/mainnet.json');
const fixture = path.join(root, 'scripts/verification/fixtures/sepolia-v1-regression-manifest.json');
const m0 = fs.readFileSync(mainnet, 'utf8');
const f0 = fs.readFileSync(fixture, 'utf8');
const operator = '0x1234567890abcdef1234567890abcdef12345678';
try {
  let r = scanner();
  must(r.status === 0, 'placeholder-only mainnet template and runtime fixture must pass scanner');
  must(m0.includes('0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'), 'canonical AGIALPHA public constant must remain committed');
  const m = JSON.parse(m0);
  must(m.temporaryDeployerAddress === null && m.finalLedgerOwnerAddress === null, 'operator fields must be null placeholders in the public template');
  fs.writeFileSync(mainnet, m0.replace('"temporaryDeployerAddress": null', `"temporaryDeployerAddress": "${operator}"`));
  r = scanner();
  must(r.status !== 0, 'valid operator address inserted into mainnet template must fail');
  must(!(`${r.stdout}${r.stderr}`).includes(operator), 'scanner output must redact private operator addresses');
  must((`${r.stdout}${r.stderr}`).includes('PRIVATE_OPERATOR_ADDRESS'), 'scanner must report structured PRIVATE_OPERATOR_ADDRESS rule');
  fs.writeFileSync(mainnet, m0);
  fs.writeFileSync(fixture, f0.replace('"fixtureOnly": true,', `"fixtureOnly": true,\n  "operatorAddress": "${operator}",`));
  r = scanner();
  must(r.status !== 0, 'static private-looking role address in verification fixture must fail');
  must(!(`${r.stdout}${r.stderr}`).includes(operator), 'fixture scanner output must redact private-looking fixture address');
  fs.writeFileSync(fixture, f0);
  r = spawnSync(process.execPath, ['scripts/verification/test-verification-v2.js'], { cwd: root, encoding: 'utf8' });
  must(r.status === 0, 'V1 regression and V2 verification behavior must remain tested');
  const templateSchema = JSON.parse(fs.readFileSync(path.join(root, 'schemas/deployment-mainnet-template.schema.json'), 'utf8'));
  const runtimeSchema = JSON.parse(fs.readFileSync(path.join(root, 'schemas/deployment-mainnet-runtime.schema.json'), 'utf8'));
  must(templateSchema.properties.temporaryDeployerAddress.type === 'null', 'template schema must require deployer placeholder');
  must(runtimeSchema.properties.temporaryDeployerAddress.$ref, 'runtime schema must require a real deployer address');
  console.log('private operator data regression tests passed');
} finally {
  fs.writeFileSync(mainnet, m0);
  fs.writeFileSync(fixture, f0);
}
