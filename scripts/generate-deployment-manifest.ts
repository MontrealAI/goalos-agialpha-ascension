import fs from "fs";
import crypto from "crypto";
const AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const manifest = { network: "ethereum-mainnet", chain: "ethereum", chainId: 1, agialphaToken: AGIALPHA, mockAgialphaUsed: false, newAgialphaTokenDeployed: false, commit: process.env.GITHUB_SHA || "LOCAL_TEMPLATE", deployedAt: new Date().toISOString(), deployerCommitmentHash: "0x" + "0".repeat(64), contracts: {}, transactions: [], constructorArgs: {}, roleAssignmentsCommitmentHash: "0x" + "0".repeat(64), authorizationDecisionHash: "0x" + "0".repeat(64), toolchainClearanceHash: "0x" + "0".repeat(64), sepoliaEvidenceHash: "0x" + "0".repeat(64), mainnetPreflightHash: "0x" + "0".repeat(64), founderApprovalCommitmentHash: "0x" + "0".repeat(64), addressCeremonyCommitmentHash: "0x" + "0".repeat(64), templateOnly: true };
fs.mkdirSync("deployments", { recursive: true });
const body = JSON.stringify(manifest, null, 2) + "\n";
fs.writeFileSync("deployments/ethereum-mainnet.agialpha.template.json", body);
fs.writeFileSync("deployments/ethereum-mainnet.agialpha.template.sha256", crypto.createHash("sha256").update(body).digest("hex") + "\n");
console.log("Wrote public-safe Ethereum Mainnet deployment manifest template.");
