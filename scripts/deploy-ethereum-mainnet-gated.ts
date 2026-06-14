import { ethers, network } from "hardhat";
import fs from "fs";
import crypto from "crypto";
import { deployGoalOSAGIALPHAAscension } from "./deploy-core";
import { AGIALPHA_MAINNET_TOKEN, assertAgialphaMainnetToken, assertNoMockTokenOnMainnet, assertNoSecretLogging } from "./config/networkConfig";

const CONFIRM_PHRASE = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET";
const ALLOW_MAINNET_DEPLOYMENT_VALUE = "YES_PUBLIC_REPOSITORY_AUTHORIZED_MANUAL_DEPLOYMENT";
function readJson(path: string) { if (!fs.existsSync(path)) throw new Error(`${path} is missing.`); return JSON.parse(fs.readFileSync(path, "utf8")); }
function hashFile(path: string) { return "0x" + crypto.createHash("sha256").update(fs.readFileSync(path)).digest("hex"); }
function evidencePath(entry: any, fallback: string): string { return (entry && typeof entry === "object" && entry.path) ? entry.path : (typeof entry === "string" ? entry : fallback); }

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
  const certificate = readJson("qa/mainnet-authorization-certificate.json");
  if ((certificate.technicallyMainnetReady ?? certificate.TECHNICALLY_MAINNET_READY) !== "YES") throw new Error("Mainnet Authorization Certificate technical readiness is not YES.");
  if ((certificate.mainnetDeploymentAuthorized ?? certificate.MAINNET_DEPLOYMENT_AUTHORIZED) !== "YES") throw new Error("Mainnet Authorization Certificate deployment authorization is not YES.");
  if ((certificate.ethereumMainnetAuthorized ?? certificate.ETHEREUM_MAINNET_AUTHORIZED) !== "YES") throw new Error("Mainnet Authorization Certificate Ethereum authorization is not YES.");
  if (certificate.mainnetDeployed !== "NO") throw new Error("Certificate must say MAINNET_DEPLOYED: NO before first deployment.");
  if (certificate.ciCanDeployMainnet !== false) throw new Error("Certificate must state ciCanDeployMainnet=false.");
  if (certificate.runtimeSecretsStoredInGitHub !== false) throw new Error("Certificate must state runtimeSecretsStoredInGitHub=false.");
  if (certificate.privateOperatorAuthorizationPackageRequired !== false) throw new Error("Certificate must state privateOperatorAuthorizationPackageRequired=false.");
  const evidence = certificate.evidence || {};
  const toolchainPath = evidencePath(evidence.toolchainClearance, "qa/public-toolchain-clearance-evidence.json");
  const rehearsalPath = evidencePath(evidence.localRehearsal, "qa/local-rehearsal-report.json");
  const tokenVerificationPath = evidencePath(evidence.agialphaTokenVerification, "qa/public-agialpha-token-verification.json");
  const governancePath = evidencePath(evidence.publicGovernanceApproval, "qa/public-governance-approval-evidence.json");
  const requiredEvidenceFiles = ["qa/mainnet-authorization-certificate.json", toolchainPath, rehearsalPath, tokenVerificationPath, governancePath];
  for (const publicEvidencePath of requiredEvidenceFiles) if (!fs.existsSync(publicEvidencePath)) throw new Error(`Required public evidence file is missing: ${publicEvidencePath}`);
  const toolchain = readJson(toolchainPath);
  if (toolchain.automatedSecurityToolchain !== "PASSED" && toolchain.status !== "PASSED") throw new Error("Public toolchain clearance evidence is not PASSED.");
  const rehearsal = readJson(rehearsalPath);
  if (rehearsal.status !== "PASSED") throw new Error("Local deterministic rehearsal evidence is not PASSED.");
  const tokenVerification = readJson(tokenVerificationPath);
  if (tokenVerification.status !== "PASSED" && tokenVerification.status !== "ACCEPTED_BY_PUBLIC_GOVERNANCE") throw new Error("Public AGIALPHA verification evidence is not passed/accepted.");
  if (process.env.ALLOW_MAINNET_DEPLOYMENT !== ALLOW_MAINNET_DEPLOYMENT_VALUE) throw new Error(`ALLOW_MAINNET_DEPLOYMENT must equal ${ALLOW_MAINNET_DEPLOYMENT_VALUE} for local Ethereum Mainnet broadcast.`);
  if (process.env.MAINNET_DEPLOYMENT_CONFIRMATION !== CONFIRM_PHRASE && process.env.FINAL_DEPLOY_CONFIRMATION !== CONFIRM_PHRASE) throw new Error(`Typed confirmation phrase is required: ${CONFIRM_PHRASE}`);
  console.log(JSON.stringify({ status: "MAINNET_DEPLOYMENT_GATES_PASSED_REDACTED", chain: "ethereum", chainId: 1, agialphaToken: AGIALPHA_MAINNET_TOKEN, privateOperatorPackageRequired: false, noMainnetMock: true }, null, 2));
  const deployment = await deployGoalOSAGIALPHAAscension();
  const manifestPath = "deployments/ethereum-mainnet.agialpha.latest.json";
  if (fs.existsSync(manifestPath)) fs.writeFileSync("deployments/ethereum-mainnet.agialpha.latest.sha256", hashFile(manifestPath) + "\n");
  console.log(JSON.stringify({ status: "ETHEREUM_MAINNET_DEPLOYMENT_COMPLETE_REDACTED", manifest: manifestPath, contracts: Object.keys(deployment.contracts || {}).length, transactions: (deployment.transactions || []).length }, null, 2));
}
main().catch((error) => { console.error(error?.message || error); process.exitCode = 1; });
