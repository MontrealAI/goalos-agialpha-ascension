import fs from "fs";
const AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const path = process.argv[2] || "deployments/ethereum-mainnet.agialpha.latest.json";
const blockers: string[] = [];
if (!fs.existsSync(path)) blockers.push(`Missing manifest: ${path}`);
else {
  const m = JSON.parse(fs.readFileSync(path, "utf8"));
  if (m.chain !== "ethereum" || m.chainId !== 1 || m.network !== "ethereum-mainnet") blockers.push("Manifest is not Ethereum Mainnet.");
  if ((m.agialphaToken || "").toLowerCase() !== AGIALPHA.toLowerCase()) blockers.push("Manifest AGIALPHA token mismatch.");
  if (m.mockAgialphaUsed !== false || m.newAgialphaTokenDeployed !== false) blockers.push("Manifest indicates forbidden Mock/new AGIALPHA token path.");
  if (!Array.isArray(m.transactions)) blockers.push("Manifest transactions must be an array.");
}
console.log(JSON.stringify({ path, status: blockers.length ? "BLOCKED" : "PASSED", blockers }, null, 2));
if (blockers.length) process.exit(1);
