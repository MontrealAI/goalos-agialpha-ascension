import fs from "fs";
import crypto from "crypto";

const AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const outJson = "qa/ETHEREUM_MAINNET_FORK_SIMULATION.json";
const outMd = "docs/ETHEREUM_MAINNET_FORK_SIMULATION_REPORT.md";
fs.mkdirSync("qa", { recursive: true });
fs.mkdirSync("docs", { recursive: true });

const blockers: string[] = [];
if (!process.env.MAINNET_RPC_URL && !process.env.ETHEREUM_MAINNET_RPC_URL) {
  blockers.push("MAINNET_RPC_URL or ETHEREUM_MAINNET_RPC_URL is required for a real Ethereum mainnet fork simulation");
}
if ((process.env.AGIALPHA_TOKEN_ADDRESS || AGIALPHA).toLowerCase() !== AGIALPHA.toLowerCase()) {
  blockers.push(`AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA}`);
}
blockers.push("Fork-only deployment simulation was not executed in this environment; no mainnet RPC evidence was supplied");

const status = blockers.length === 0 ? "PASSED" : "PENDING_RPC";
const generatedAt = new Date().toISOString();
const decision = {
  status,
  generatedAt,
  generatedBy: "scripts/mainnet-fork-simulate.ts",
  chain: "ethereum",
  chainId: 1,
  agialphaToken: AGIALPHA,
  mainnetBroadcast: false,
  expectedManifest: "deployments/ethereum-mainnet.agialpha.latest.json",
  checks: {
    forkMainnet: status === "PASSED",
    usesExistingAGIALPHA: true,
    deploysMockAGIALPHAOnMainnet: false,
    deploysNewAGIALPHAOnMainnet: false,
    launchGateChecks: status === "PASSED",
    emergencyAdminChecks: status === "PASSED",
    roleEscalationChecks: status === "PASSED"
  },
  blockers
};
fs.writeFileSync(outJson, JSON.stringify(decision, null, 2) + "\n");
const hash = crypto.createHash("sha256").update(JSON.stringify(decision)).digest("hex");
fs.writeFileSync(outMd, `# Ethereum Mainnet Fork Simulation Report\n\nStatus: **${status}**\n\nSHA-256: \`${hash}\`\n\n## Blockers\n${blockers.map((b) => `- ${b}`).join("\n") || "- None."}\n\nNo Ethereum Mainnet broadcast occurred.\n`);
console.log(JSON.stringify(decision, null, 2));
