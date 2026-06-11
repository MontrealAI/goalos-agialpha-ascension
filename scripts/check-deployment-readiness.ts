import fs from "fs";
const required = ["docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json", "docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json", "docs/MAINNET_TECHNICAL_READINESS_DECISION.json", "scripts/deploy-ethereum-mainnet-gated.ts", "scripts/private/run-final-local-mainnet-deployment.py"];
const blockers = required.filter((p) => !fs.existsSync(p)).map((p) => `Missing ${p}`);
console.log(JSON.stringify({ status: blockers.length ? "NO" : "YES", blockers }, null, 2));
if (blockers.length) process.exit(1);
