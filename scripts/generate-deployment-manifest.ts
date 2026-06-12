import fs from "fs";
import crypto from "crypto";
import { AGIALPHA_MAINNET_TOKEN as AGIALPHA } from "./config/networkConfig";

function hashPublicFile(path: string): string {
  return fs.existsSync(path) ? "0x" + crypto.createHash("sha256").update(fs.readFileSync(path)).digest("hex") : "0x" + "0".repeat(64);
}

const manifest = {
  network: "ethereum-mainnet",
  chain: "ethereum",
  chainId: 1,
  agialphaToken: AGIALPHA,
  mockAgialphaUsed: false,
  newAgialphaTokenDeployed: false,
  commit: process.env.GITHUB_SHA || "LOCAL_TEMPLATE",
  deployedAt: new Date().toISOString(),
  contracts: {},
  transactions: [],
  constructorArgs: {},
  mainnetAuthorizationCertificateHash: hashPublicFile("qa/mainnet-authorization-certificate.json"),
  toolchainClearanceHash: hashPublicFile("qa/public-toolchain-clearance-evidence.json"),
  localRehearsalEvidenceHash: hashPublicFile("qa/local-rehearsal-report.json"),
  agialphaTokenVerificationHash: hashPublicFile("qa/public-agialpha-token-verification.json"),
  publicGovernanceApprovalHash: hashPublicFile("qa/public-governance-approval-evidence.json"),
  templateOnly: true
};
fs.mkdirSync("deployments", { recursive: true });
const body = JSON.stringify(manifest, null, 2) + "\n";
fs.writeFileSync("deployments/ethereum-mainnet.agialpha.template.json", body);
fs.writeFileSync("deployments/ethereum-mainnet.agialpha.template.sha256", crypto.createHash("sha256").update(body).digest("hex") + "\n");
console.log(JSON.stringify({ status: "TEMPLATE_WRITTEN", path: "deployments/ethereum-mainnet.agialpha.template.json" }, null, 2));
