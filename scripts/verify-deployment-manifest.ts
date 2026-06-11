import fs from "fs";
const AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const ADDRESS_RE = /0x[0-9a-fA-F]{40}/g;
const path = process.argv[2] || "deployments/ethereum-mainnet.agialpha.latest.json";
const blockers: string[] = [];
if (!fs.existsSync(path)) blockers.push(`Missing manifest: ${path}`);
else {
  const raw = fs.readFileSync(path, "utf8");
  const m = JSON.parse(raw);
  if (m.chain !== "ethereum" || m.chainId !== 1 || m.network !== "ethereum-mainnet") blockers.push("Manifest is not Ethereum Mainnet.");
  if ((m.agialphaToken || "").toLowerCase() !== AGIALPHA.toLowerCase()) blockers.push("Manifest AGIALPHA token mismatch.");
  if (m.mockAgialphaUsed !== false || m.newAgialphaTokenDeployed !== false) blockers.push("Manifest indicates forbidden Mock/new AGIALPHA token path.");
  if (!Array.isArray(m.transactions)) blockers.push("Manifest transactions must be an array.");
  if (m.constructorArgsRedacted === false && !m.templateOnly) blockers.push("Ethereum Mainnet manifest constructor args must be redacted.");
  const constructorArgsText = JSON.stringify(m.constructorArgs || {});
  const leakedConstructorAddresses = [...constructorArgsText.matchAll(ADDRESS_RE)].map((match) => match[0]).filter((addr) => addr.toLowerCase() !== AGIALPHA.toLowerCase());
  if (leakedConstructorAddresses.length) blockers.push("Constructor args contain unredacted non-AGIALPHA addresses.");
}
console.log(JSON.stringify({ path, status: blockers.length ? "BLOCKED" : "PASSED", blockers }, null, 2));
if (blockers.length) process.exit(1);
