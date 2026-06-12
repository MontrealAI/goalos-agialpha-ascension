import { ethers, network } from "hardhat";
import fs from "fs";
import crypto from "crypto";
import { deployGoalOSAGIALPHAAscension } from "./deploy-core";
import { AGIALPHA_MAINNET_TOKEN, assertAgialphaMainnetToken, assertNoMockTokenOnMainnet, assertNoSecretLogging } from "./config/networkConfig";

const CONFIRM_PHRASE = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET";
const REQUIRED_HASHES = [
  "AUTHORIZATION_DECISION_HASH",
  "TOOLCHAIN_CLEARANCE_HASH",
  "LOCAL_REHEARSAL_EVIDENCE_HASH",
  "AGIALPHA_TOKEN_VERIFICATION_HASH",
  "PUBLIC_GOVERNANCE_APPROVAL_HASH"
];
function readJson(path: string) { if (!fs.existsSync(path)) throw new Error(`${path} is missing.`); return JSON.parse(fs.readFileSync(path, "utf8")); }
function validHash(value: string | undefined) { return /^0x[0-9a-fA-F]{64}$/.test(value || "") && !/^0x0{64}$/i.test(value || ""); }
function hashFile(path: string) { return "0x" + crypto.createHash("sha256").update(fs.readFileSync(path)).digest("hex"); }

async function main() {
  assertNoSecretLogging();
  if (process.env.GITHUB_ACTIONS === "true" || process.env.CI === "true") throw new Error("Ethereum Mainnet deployment is forbidden in CI/GitHub Actions.");
  if (network.name !== "ethereumMainnet" && network.name !== "mainnet") throw new Error("Use --network ethereumMainnet for final deployment.");
  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) !== 1) throw new Error(`Wrong network. Expected Ethereum mainnet chainId 1, got ${net.chainId}.`);
  if (process.env.MAINNET_TARGET !== "ethereum") throw new Error("MAINNET_TARGET must be ethereum.");
  const token = process.env.AGIALPHA_TOKEN_ADDRESS || "";
  assertAgialphaMainnetToken(token);
  assertNoMockTokenOnMainnet(1, token);
  if ((await ethers.provider.getCode(AGIALPHA_MAINNET_TOKEN)) === "0x") throw new Error("Canonical AGIALPHA token has no code on Ethereum Mainnet provider.");
  if (process.env.MOCK_AGIALPHA_ADDRESS) throw new Error("MOCK_AGIALPHA_ADDRESS must not be set for Ethereum Mainnet.");
  if (process.env.DEPLOY_NEW_AGIALPHA_TOKEN === "true") throw new Error("Deploying or minting a new AGIALPHA token on Ethereum Mainnet is forbidden.");
  const publicAuth = readJson("docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json");
  if (publicAuth.status !== "YES" || publicAuth.ETHEREUM_MAINNET_AUTHORIZED !== "YES") throw new Error("Redacted public Ethereum Mainnet authorization decision is not YES.");
  const deployAuth = readJson("docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json");
  if (deployAuth.status !== "YES" || deployAuth.MAINNET_DEPLOYMENT_AUTHORIZED !== "YES") throw new Error("Public Mainnet deployment authorization decision is not YES.");
  const toolchain = readJson("qa/public-toolchain-clearance-evidence.json");
  if (toolchain.automatedSecurityToolchain !== "PASSED" && toolchain.status !== "PASSED") throw new Error("Public toolchain clearance evidence is not PASSED.");
  const rehearsal = readJson("qa/local-rehearsal-report.json");
  if (rehearsal.status !== "PASSED") throw new Error("Local deterministic rehearsal evidence is not PASSED.");
  const tokenVerification = readJson("qa/public-agialpha-token-verification.json");
  if (tokenVerification.status !== "PASSED" && tokenVerification.status !== "ACCEPTED_BY_PUBLIC_GOVERNANCE") throw new Error("Public AGIALPHA verification evidence is not passed/accepted.");
  process.env.ALLOW_MAINNET_DEPLOYMENT = "YES_PUBLIC_REPOSITORY_AUTHORIZED_MANUAL_DEPLOYMENT";
  for (const key of REQUIRED_HASHES) if (!validHash(process.env[key])) throw new Error(`${key} commitment is missing or invalid.`);
  if (process.env.MAINNET_DEPLOYMENT_CONFIRMATION !== CONFIRM_PHRASE && process.env.FINAL_DEPLOY_CONFIRMATION !== CONFIRM_PHRASE) throw new Error(`Typed confirmation phrase is required: ${CONFIRM_PHRASE}`);
  console.log(JSON.stringify({ status: "MAINNET_DEPLOYMENT_GATES_PASSED_REDACTED", chain: "ethereum", chainId: 1, agialphaToken: AGIALPHA_MAINNET_TOKEN, privateOperatorPackageRequired: false, noMainnetMock: true }, null, 2));
  const deployment = await deployGoalOSAGIALPHAAscension();
  const manifestPath = "deployments/ethereum-mainnet.agialpha.latest.json";
  if (fs.existsSync(manifestPath)) fs.writeFileSync("deployments/ethereum-mainnet.agialpha.latest.sha256", hashFile(manifestPath) + "\n");
  console.log(JSON.stringify({ status: "ETHEREUM_MAINNET_DEPLOYMENT_COMPLETE_REDACTED", manifest: manifestPath, contracts: Object.keys(deployment.contracts || {}).length, transactions: (deployment.transactions || []).length }, null, 2));
}
main().catch((error) => { console.error(error?.message || error); process.exitCode = 1; });
