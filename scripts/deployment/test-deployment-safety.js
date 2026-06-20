const assert = require('assert'); const fs = require('fs'); const cp = require('child_process');
function run(args, env={}) { return cp.spawnSync(process.platform==='win32'?'npx.cmd':'npx', ['ts-node','scripts/deployment/goalos-deploy-wizard.ts',...args], {encoding:'utf8', env:{...process.env,...env}}); }
let r = run(['--help']); assert.strictEqual(r.status,0,r.stderr); assert.match(r.stdout,/GoalOS Deployment Command Center|usage/);
r = run(['setup','--network','sepolia','--json']); assert.strictEqual(r.status,0,r.stderr); assert(fs.existsSync('config/deployment/sepolia.json')); assert(fs.existsSync('.private/sepolia-operator.env'));
r = run(['plan','--network','mainnet','--json']); assert.strictEqual(r.status,0,r.stderr); assert.match(r.stdout,/planHash/);
const hardhat = fs.readFileSync('hardhat.config.ts','utf8'); assert(!hardhat.includes('ethereumSepolia") || "http://127.0.0.1:8545"')); assert(hardhat.includes('goalos-missing-rpc.invalid'));
const out = cp.spawnSync(process.platform==='win32'?'npx.cmd':'npx',['hardhat','run','scripts/deployment/goalos-deploy-wizard.ts','--network','ethereumSepolia'],{encoding:'utf8', env:{...process.env, PRIVATE_SEPOLIA_RPC_URL:''}}); assert.notStrictEqual(out.status,0); assert.match(out.stderr+out.stdout,/Missing RPC URL|refuses localhost fallback/);
console.log('deployment safety tests passed');
