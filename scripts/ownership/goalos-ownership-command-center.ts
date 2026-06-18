import hre from "hardhat";
import fs from "fs";
import path from "path";
import crypto from "crypto";

const { ethers } = hre as any;
const ROOT = path.join(__dirname, "../..");
const MANAGED_ROLES = [
  "DEFAULT_ADMIN_ROLE",
  "PROTOCOL_ADMIN_ROLE",
  "OPERATOR_ROLE",
  "REVIEWER_MANAGER_ROLE",
  "TREASURY_ROLE",
  "PAUSER_ROLE",
  "VAULT_MANAGER_ROLE",
];
const RUNTIME_OWNER_ENV = [
  "FOUNDER_ADDRESS",
  "TREASURY_ADDRESS",
  "COMMERCIALIZATION_PERFORMANCE_ADMIN",
  "PROOF_REWARDS_ADMIN",
  "LIQUIDITY_ADMIN",
  "SECURITY_ADMIN",
  "COMMUNITY_ADMIN",
  "APPROVED_PERMANENT_OWNER_ADDRESSES",
];
const RUNTIME_ADDRESS_GETTERS = [
  "treasury",
  "founder",
  "commercializationAdmin",
  "proofRewardsAdmin",
  "liquidityAdmin",
  "securityAdmin",
  "communityAdmin",
  "agialphaToken",
  "credentialRegistry",
  "evaluatorStaking",
  "jobRegistry",
  "legacyAGIJobManager",
  "proofSubmissionRegistry",
  "reputationRegistry",
];
const AGIALPHA = "AGIALPHA";
const ERC173 = "0x7f5828d0";
const EIP1271_MAGIC_VALUE = "0x1626ba7e";

type ManagedEntry = { name: string; address: string };
type PlannedEntry = ManagedEntry & { currentOwner: string; action: string; gasEstimate: string };
type TransferOptions = { rehearsalInterruptAfter?: number; skipMainnetTypedConfirmation?: boolean };

function sha256(buf: Buffer | string): string {
  return "0x" + crypto.createHash("sha256").update(buf).digest("hex");
}

function canonicalJson(data: unknown): string {
  return JSON.stringify(data, Object.keys(data as Record<string, unknown>).sort());
}

function planHash(plan: Record<string, unknown>): string {
  const copy = { ...plan };
  delete copy.planHash;
  return sha256(JSON.stringify(copy));
}

function writeJsonAtomic(file: string, data: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp-${process.pid}`;
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2) + "\n");
  fs.renameSync(tmp, file);
  fs.writeFileSync(`${file}.sha256`, `${sha256(fs.readFileSync(file))}  ${path.basename(file)}\n`);
}

function requireAddress(name: string): string {
  const value = process.env[name];
  if (!value || !ethers.isAddress(value) || ethers.getAddress(value) === ethers.ZeroAddress) {
    throw new Error(`Missing/invalid ${name}`);
  }
  return ethers.getAddress(value);
}

function optionalAddressesFromEnv(): Set<string> {
  const out = new Set<string>();
  for (const name of RUNTIME_OWNER_ENV) {
    const value = process.env[name];
    if (!value) continue;
    for (const raw of value.split(",")) {
      const trimmed = raw.trim();
      if (trimmed && ethers.isAddress(trimmed) && ethers.getAddress(trimmed) !== ethers.ZeroAddress) {
        out.add(ethers.getAddress(trimmed));
      }
    }
  }
  return out;
}

function expectedChainId(label: string): bigint {
  if (label === "ethereum-mainnet") return 1n;
  if (label === "ethereum-sepolia") return 11155111n;
  throw new Error(`Unsupported ownership network label ${label}`);
}

function requireExpectedChain(label: string, actual: bigint): void {
  const expected = expectedChainId(label);
  if (actual !== expected) {
    throw new Error(`Wrong chain for ${label}: detected ${actual}, expected ${expected}`);
  }
}

function forbidCiMainnet(chainId: bigint): void {
  if (chainId === 1n && (process.env.CI || process.env.GITHUB_ACTIONS)) {
    throw new Error("Mainnet ownership handoff is local-only and forbidden in CI/GitHub Actions");
  }
}

function manifestPath(label: string): string {
  return path.join(ROOT, "deployments", `${label}.agialpha.latest.json`);
}

function latestPlanPath(label: string): string {
  return path.join(ROOT, ".private", `${label}.ownership-plan.latest.json`);
}

function publicHandoffPath(label: string): string {
  return path.join(ROOT, "deployments", `${label}.ownership-handoff.latest.json`);
}

function evidencePath(label: string): string {
  return path.join(ROOT, "qa", `${label.replace("ethereum-", "")}-ownership-handoff-evidence.json`);
}

function reportPath(label: string): string {
  return path.join(ROOT, "docs", label === "ethereum-mainnet" ? "ETHEREUM_MAINNET_OWNERSHIP_HANDOFF_REPORT.md" : "SEPOLIA_OWNERSHIP_HANDOFF_REPORT.md");
}

function readManifest(label: string): { path: string; hash: string; data: any } {
  const p = manifestPath(label);
  if (!fs.existsSync(p)) throw new Error(`Missing deployment manifest ${p}`);
  const raw = fs.readFileSync(p);
  return { path: p, hash: sha256(raw), data: JSON.parse(raw.toString("utf8")) };
}


function readPlanIfPresent(label: string): any | undefined {
  const planPath = latestPlanPath(label);
  if (!fs.existsSync(planPath)) return undefined;
  return JSON.parse(fs.readFileSync(planPath, "utf8"));
}

function resolveDisposableOwner(label: string, manifest: any, fallbackSigner: string): string {
  const envOwner = process.env.OWNERSHIP_DISPOSABLE_OWNER_ADDRESS;
  if (envOwner && ethers.isAddress(envOwner)) return ethers.getAddress(envOwner);
  const plan = readPlanIfPresent(label);
  if (plan?.disposableOwner && ethers.isAddress(plan.disposableOwner)) return ethers.getAddress(plan.disposableOwner);
  if (manifest?.deployer && ethers.isAddress(manifest.deployer)) return ethers.getAddress(manifest.deployer);
  if (label === "ethereum-mainnet") throw new Error("Missing disposable owner: set OWNERSHIP_DISPOSABLE_OWNER_ADDRESS or run ownership plan first");
  return fallbackSigner;
}

async function signerForOwner(owner: string, fallbackSigner: any): Promise<any> {
  const fallback = ethers.getAddress(fallbackSigner.address);
  if (fallback === owner) return fallbackSigner;
  if (hre.network.name === "hardhat") {
    await ethers.provider.send("hardhat_impersonateAccount", [owner]);
    await ethers.provider.send("hardhat_setBalance", [owner, "0x3635c9adc5dea00000"]);
    return ethers.getSigner(owner);
  }
  throw new Error(`Connected signer ${fallback} is not the planned disposable owner ${owner}`);
}

function entries(manifest: any): ManagedEntry[] {
  const contracts = manifest.contracts || manifest.addresses || {};
  return Object.entries(contracts)
    .filter(([name, value]) => name !== AGIALPHA && typeof value === "string" && ethers.isAddress(value))
    .map(([name, address]) => ({ name, address: ethers.getAddress(address as string) }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

async function contractAt(address: string): Promise<any> {
  return new ethers.Contract(
    address,
    [
      "function owner() view returns (address)",
      "function transferOwnership(address)",
      "function supportsInterface(bytes4) view returns (bool)",
      "function hasRole(bytes32,address) view returns (bool)",
      ...MANAGED_ROLES.map((role) => `function ${role}() view returns (bytes32)`),
      ...RUNTIME_ADDRESS_GETTERS.map((getter) => `function ${getter}() view returns (address)`),
      "function managedOwnershipRoleCount() view returns (uint256)",
      "event OwnershipTransferred(address indexed previousOwner,address indexed newOwner)",
      "event GoalOSOwnershipRolesMigrated(address indexed previousOwner,address indexed newOwner)",
    ],
    ethers.provider,
  );
}

async function roleIds(c: any): Promise<Record<string, string>> {
  const out: Record<string, string> = {};
  for (const role of MANAGED_ROLES) out[role] = await c[role]();
  return out;
}

async function runtimeAddressAudit(c: any, disposableOwner: string): Promise<Array<{ getter: string; value: string; ok: boolean }>> {
  const out: Array<{ getter: string; value: string; ok: boolean }> = [];
  for (const getter of RUNTIME_ADDRESS_GETTERS) {
    try {
      const value = ethers.getAddress(await c[getter]());
      out.push({ getter, value, ok: value !== disposableOwner });
    } catch {
      // Getter is absent on this contract or not callable with the expected address return.
    }
  }
  return out;
}

function proofMessage(proof: any): string {
  const message = proof.message || proof.challenge || proof.statement;
  if (!message || typeof message !== "string") throw new Error("Final-owner proof missing signed message/challenge");
  return message;
}

function proofMessageIncludesBindings(message: string, chainId: bigint, finalOwner: string, manifestHash: string): void {
  const lower = message.toLowerCase();
  const chainPattern = new RegExp(`(?:^|[^a-z0-9_])(?:chainId|chain_id|chain id)[\\s:=\"]+${chainId.toString()}(?:[^0-9]|$)`, "i");
  if (!chainPattern.test(message)) throw new Error("Final-owner proof message missing exact chainId binding");
  if (!lower.includes(finalOwner.toLowerCase())) throw new Error("Final-owner proof message missing final owner binding");
  if (!lower.includes(manifestHash.toLowerCase())) throw new Error("Final-owner proof message missing manifest hash binding");
}

async function validateProof(chainId: bigint, finalOwner: string, manifestHash: string): Promise<{ required: boolean; commitment?: string; signer?: string; kind?: string }> {
  if (chainId !== 1n) return { required: false };
  const proofPath = process.env.FINAL_OWNER_CONTROL_PROOF_PATH || ".private/final-owner-control-proof.json";
  const absolute = path.join(ROOT, proofPath);
  if (!fs.existsSync(absolute)) throw new Error(`Missing Mainnet final-owner control proof ${proofPath}`);
  const proof = JSON.parse(fs.readFileSync(absolute, "utf8"));
  const kind = proof.finalOwnerKind || proof.kind || process.env.FINAL_OWNER_KIND || "LEDGER_EOA";
  const message = proofMessage(proof);
  const signature = proof.signature;
  if (!signature || typeof signature !== "string") throw new Error("Final-owner proof missing signature");
  if (ethers.getAddress(proof.finalOwnerAddress) !== finalOwner || BigInt(proof.chainId) !== chainId || proof.deploymentManifestSha256 !== manifestHash) {
    throw new Error("Final-owner proof target/chain/manifest mismatch");
  }
  proofMessageIncludesBindings(message, chainId, finalOwner, manifestHash);
  const expiresAtMs = Date.parse(proof.expiresAt);
  if (!Number.isFinite(expiresAtMs)) throw new Error("Final-owner proof expiry is invalid");
  if (!message.includes(proof.expiresAt)) throw new Error("Final-owner proof message missing exact expiry binding");
  if (expiresAtMs <= Date.now()) throw new Error("Final-owner proof expired");
  if (kind === "LEDGER_EOA") {
    const recovered = ethers.getAddress(ethers.verifyMessage(message, signature));
    if (recovered !== finalOwner) throw new Error(`Final-owner proof signature recovered ${recovered}, expected ${finalOwner}`);
    return { required: true, commitment: sha256(canonicalJson(proof)), signer: recovered, kind };
  }
  if (kind === "SAFE") {
    const code = await ethers.provider.getCode(finalOwner);
    if (code === "0x") throw new Error("Safe final-owner proof target has no bytecode");
    const safe = new ethers.Contract(finalOwner, ["function isValidSignature(bytes32,bytes) view returns (bytes4)"], ethers.provider);
    const digest = ethers.hashMessage(message);
    const magic = await safe.isValidSignature(digest, signature);
    if (magic !== EIP1271_MAGIC_VALUE) throw new Error("Safe final-owner proof failed EIP-1271 validation");
    return { required: true, commitment: sha256(canonicalJson(proof)), signer: finalOwner, kind };
  }
  throw new Error(`Unsupported FINAL_OWNER_KIND ${kind}`);
}

function actionForOwner(owner: string, deployer: string, finalOwner: string, permanentOwners: Set<string>): string {
  if (owner === finalOwner) return "ALREADY_FINAL_OWNER";
  if (owner === deployer) return "TRANSFER";
  if (permanentOwners.has(owner)) return "PERMANENT_RUNTIME_OWNER";
  return "FAIL";
}

async function doctor(label: string): Promise<void> {
  const net = await ethers.provider.getNetwork();
  requireExpectedChain(label, net.chainId);
  forbidCiMainnet(net.chainId);
  const finalOwner = requireAddress("FINAL_OWNER_ADDRESS");
  const permanentOwners = optionalAddressesFromEnv();
  const [deployer] = await ethers.getSigners();
  const deployerAddress = ethers.getAddress(deployer.address);
  if (deployerAddress === finalOwner) throw new Error("FINAL_OWNER_ADDRESS must differ from disposable deployer");
  if (permanentOwners.has(deployerAddress)) throw new Error("Disposable deployer is listed as an approved permanent owner");
  const manifest = readManifest(label);
  const list = entries(manifest.data);
  if (!list.length) throw new Error("No managed contracts found in manifest");
  const seen = new Set<string>();
  for (const entry of list) {
    if (seen.has(entry.address)) throw new Error(`Duplicate managed address ${entry.address}`);
    seen.add(entry.address);
    if ((await ethers.provider.getCode(entry.address)) === "0x") throw new Error(`No bytecode at ${entry.name} ${entry.address}`);
    const c = await contractAt(entry.address);
    const owner = ethers.getAddress(await c.owner());
    const action = actionForOwner(owner, deployerAddress, finalOwner, permanentOwners);
    if (action === "FAIL") throw new Error(`Unexpected owner for ${entry.name}: ${owner}`);
    try {
      if (!(await c.supportsInterface(ERC173))) throw new Error("false");
    } catch {
      throw new Error(`${entry.name} lacks ERC-173 support`);
    }
  }
  await validateProof(net.chainId, finalOwner, manifest.hash);
  console.log(`PASS ownership doctor ${label}: ${list.length} managed contracts, chainId ${net.chainId}`);
}

async function plan(label: string): Promise<void> {
  const net = await ethers.provider.getNetwork();
  requireExpectedChain(label, net.chainId);
  forbidCiMainnet(net.chainId);
  const finalOwner = requireAddress("FINAL_OWNER_ADDRESS");
  const permanentOwners = optionalAddressesFromEnv();
  const [connectedSigner] = await ethers.getSigners();
  const manifest = readManifest(label);
  const deployerAddress = resolveDisposableOwner(label, manifest.data, ethers.getAddress(connectedSigner.address));
  const deployer = await signerForOwner(deployerAddress, connectedSigner);
  if (permanentOwners.has(deployerAddress)) throw new Error("Disposable deployer is listed as an approved permanent owner");
  const proof = await validateProof(net.chainId, finalOwner, manifest.hash);
  const manifestEntries = entries(manifest.data);
  if (!manifestEntries.length) throw new Error("No managed contracts found in manifest");
  const managed: PlannedEntry[] = [];
  let totalGas = 0n;
  for (const entry of manifestEntries) {
    const c = (await contractAt(entry.address)).connect(deployer);
    const owner = ethers.getAddress(await c.owner());
    let gasEstimate = "0";
    let action = actionForOwner(owner, deployerAddress, finalOwner, permanentOwners);
    if (action === "TRANSFER") {
      gasEstimate = (await c.transferOwnership.estimateGas(finalOwner)).toString();
      totalGas += BigInt(gasEstimate);
    }
    managed.push({ ...entry, currentOwner: owner, action, gasEstimate });
  }
  if (managed.some((entry) => entry.action === "FAIL")) throw new Error("Ownership plan contains unexpected owners");
  const out: Record<string, unknown> = {
    schemaVersion: 1,
    status: "PLANNED",
    network: label,
    chainId: Number(net.chainId),
    sourceManifest: path.relative(ROOT, manifest.path),
    deploymentManifestSha256: manifest.hash,
    disposableOwner: deployerAddress,
    finalOwner,
    approvedPermanentOwners: [...permanentOwners].sort(),
    finalOwnerKind: process.env.FINAL_OWNER_KIND || "LEDGER_EOA",
    finalOwnerControlProof: proof,
    managedRoles: MANAGED_ROLES,
    managedContracts: managed,
    totalGasEstimate: totalGas.toString(),
    expiresAt: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
    createdAt: new Date().toISOString(),
    claimBoundary: "Plan only; not evidence of public-chain handoff.",
  };
  out.planHash = planHash(out);
  writeJsonAtomic(latestPlanPath(label), out);
  console.log(`PASS wrote ${latestPlanPath(label)} ${out.planHash}`);
}

function validateLoadedPlan(plan: any, label: string, chainId: bigint, manifestHash: string, deployer: string, finalOwner: string): void {
  const actual = planHash(plan);
  if (plan.planHash !== actual) throw new Error(`Ownership plan hash mismatch: stored ${plan.planHash}, computed ${actual}`);
  if (plan.network !== label) throw new Error(`Ownership plan network mismatch: ${plan.network} !== ${label}`);
  if (BigInt(plan.chainId) !== chainId) throw new Error(`Ownership plan chainId mismatch: ${plan.chainId} !== ${chainId}`);
  if (plan.deploymentManifestSha256 !== manifestHash) throw new Error("Ownership plan manifest hash mismatch");
  if (ethers.getAddress(plan.disposableOwner) !== deployer) throw new Error("Ownership plan disposable owner mismatch");
  if (ethers.getAddress(plan.finalOwner) !== finalOwner) throw new Error("Ownership plan final owner mismatch");
  const expiresAtMs = Date.parse(plan.expiresAt);
  if (!Number.isFinite(expiresAtMs)) throw new Error("Ownership plan expiry is invalid");
  if (expiresAtMs <= Date.now()) throw new Error("Plan expired");
}

async function transfer(label: string, options: TransferOptions = {}): Promise<void> {
  const net = await ethers.provider.getNetwork();
  requireExpectedChain(label, net.chainId);
  forbidCiMainnet(net.chainId);
  const finalOwner = requireAddress("FINAL_OWNER_ADDRESS");
  const permanentOwners = optionalAddressesFromEnv();
  const [connectedSigner] = await ethers.getSigners();
  const manifest = readManifest(label);
  const loadedPlanForOwner = readPlanIfPresent(label);
  const deployerAddress = ethers.getAddress(loadedPlanForOwner?.disposableOwner || resolveDisposableOwner(label, manifest.data, ethers.getAddress(connectedSigner.address)));
  const deployer = await signerForOwner(deployerAddress, connectedSigner);
  const p = latestPlanPath(label);
  if (!fs.existsSync(p)) throw new Error("Run ownership plan first");
  const loadedPlan = JSON.parse(fs.readFileSync(p, "utf8"));
  validateLoadedPlan(loadedPlan, label, net.chainId, manifest.hash, deployerAddress, finalOwner);
  const currentProof = await validateProof(net.chainId, finalOwner, manifest.hash);
  if (loadedPlan.finalOwnerControlProof?.required && loadedPlan.finalOwnerControlProof.commitment !== currentProof.commitment) {
    throw new Error("Final-owner control proof changed since plan creation; rerun ownership plan");
  }
  if (net.chainId === 1n && !options.skipMainnetTypedConfirmation && process.env.OWNERSHIP_MAINNET_CONFIRMATION !== `ETHEREUM_MAINNET-1-${finalOwner}-${loadedPlan.planHash}`) {
    throw new Error("Missing exact OWNERSHIP_MAINNET_CONFIRMATION");
  }
  const journal = path.join(ROOT, ".private", `${label}.ownership-journal.json`);
  const journalData = fs.existsSync(journal) ? JSON.parse(fs.readFileSync(journal, "utf8")) : { transactions: [] };
  let transferred = 0;
  for (const entry of loadedPlan.managedContracts as PlannedEntry[]) {
    const c = (await contractAt(entry.address)).connect(deployer);
    const owner = ethers.getAddress(await c.owner());
    if (owner === finalOwner) continue;
    if (entry.action === "PERMANENT_RUNTIME_OWNER") {
      if (owner !== ethers.getAddress(entry.currentOwner) || !permanentOwners.has(owner)) {
        throw new Error(`Unexpected runtime owner for ${entry.name}: live ${owner}, planned ${entry.currentOwner}`);
      }
      continue;
    }
    if (owner !== deployerAddress || entry.action !== "TRANSFER") throw new Error(`Unexpected owner/action for ${entry.name}: ${owner}/${entry.action}`);
    const tx = await c.transferOwnership(finalOwner);
    journalData.transactions.push({ name: entry.name, address: entry.address, hash: tx.hash, submittedAt: new Date().toISOString() });
    writeJsonAtomic(journal, journalData);
    const receipt = await tx.wait(Number(process.env.OWNERSHIP_CONFIRMATIONS || (net.chainId === 1n ? 5 : 1)));
    if (!receipt || receipt.status !== 1) throw new Error(`Transfer failed ${entry.name}`);
    if (ethers.getAddress(await c.owner()) !== finalOwner) throw new Error(`Post-transfer owner mismatch ${entry.name}`);
    transferred += 1;
    if (options.rehearsalInterruptAfter && transferred >= options.rehearsalInterruptAfter) {
      throw new Error(`OWNERSHIP_REHEARSAL_INTERRUPT_AFTER_${options.rehearsalInterruptAfter}`);
    }
  }
  console.log("PASS ownership transfer completed/resumed");
}

async function verify(label: string, writeEvidence = true): Promise<void> {
  const net = await ethers.provider.getNetwork();
  requireExpectedChain(label, net.chainId);
  forbidCiMainnet(net.chainId);
  const finalOwner = requireAddress("FINAL_OWNER_ADDRESS");
  const permanentOwners = optionalAddressesFromEnv();
  const [connectedSigner] = await ethers.getSigners();
  const manifest = readManifest(label);
  const loadedPlanForOwner = readPlanIfPresent(label);
  const deployerAddress = ethers.getAddress(loadedPlanForOwner?.disposableOwner || resolveDisposableOwner(label, manifest.data, ethers.getAddress(connectedSigner.address)));
  const managedEntries = entries(manifest.data);
  if (!managedEntries.length) throw new Error("No managed contracts found in manifest");
  const results = [];
  for (const entry of managedEntries) {
    const c = await contractAt(entry.address);
    const ids = await roleIds(c);
    const owner = ethers.getAddress(await c.owner());
    const runtimeAddresses = await runtimeAddressAudit(c, deployerAddress);
    const ownerIsFinal = owner === finalOwner;
    const ownerIsApprovedPermanent = permanentOwners.has(owner);
    let ok = ownerIsFinal || ownerIsApprovedPermanent;
    for (const id of Object.values(ids)) {
      if (ownerIsFinal && !(await c.hasRole(id, finalOwner))) ok = false;
      if (ownerIsApprovedPermanent && !(await c.hasRole(id, owner))) ok = false;
      if (await c.hasRole(id, deployerAddress)) ok = false;
    }
    if (runtimeAddresses.some((item) => !item.ok)) ok = false;
    results.push({ ...entry, owner, ownerClass: ownerIsFinal ? "FINAL_OWNER" : ownerIsApprovedPermanent ? "APPROVED_PERMANENT_OWNER" : "UNEXPECTED", runtimeAddresses, ok });
  }
  const failed = results.filter((result) => !result.ok);
  if (failed.length) throw new Error(`Ownership verification failed for ${failed.map((f) => f.name).join(",")}`);
  const block = await ethers.provider.getBlock("latest");
  const evidence = {
    schemaVersion: 1,
    status: "PASSED",
    network: label,
    chainId: Number(net.chainId),
    verifiedAt: new Date().toISOString(),
    confirmedBlockNumber: block?.number,
    confirmedBlockHash: block?.hash,
    deploymentManifestSha256: manifest.hash,
    managedContractCount: results.length,
    disposableDeployer: deployerAddress,
    finalOwner,
    approvedPermanentOwners: [...permanentOwners].sort(),
    results,
    claimBoundary: label === "ethereum-mainnet" ? "Mainnet PASSED evidence requires detected chainId 1 and live provider state." : "Sepolia/local rehearsal evidence only; not Mainnet evidence.",
  };
  if (writeEvidence) {
    writeJsonAtomic(evidencePath(label), evidence);
    writeJsonAtomic(publicHandoffPath(label), evidence);
    fs.writeFileSync(reportPath(label), `# ${label} Ownership Handoff Report\n\nStatus: ${evidence.status}\n\nChain ID: ${evidence.chainId}\n\nManaged contracts: ${results.length}\n\nClaim boundary: ${evidence.claimBoundary}\n`);
  }
  console.log(`PASS ownership verify ${label}: ${results.length}`);
}

async function evidence(label: string): Promise<void> {
  await verify(label);
}

async function forkRehearsal(label: string): Promise<void> {
  if (hre.network.name !== "hardhat") throw new Error("Ownership fork rehearsal must run on the local Hardhat network");
  await plan(label);
  try {
    await transfer(label, { rehearsalInterruptAfter: 1, skipMainnetTypedConfirmation: true });
  } catch (error: any) {
    if (!String(error?.message || error).includes("OWNERSHIP_REHEARSAL_INTERRUPT_AFTER_1")) throw error;
    console.log("PASS ownership fork rehearsal deliberate interruption after 1 transfer");
  }
  await transfer(label, { skipMainnetTypedConfirmation: true });
  await verify(label, false);
  const localEvidence = {
    schemaVersion: 1,
    status: "PASSED",
    network: label,
    rehearsalOnly: true,
    generatedAt: new Date().toISOString(),
    claimBoundary: "Hardhat fork/local rehearsal only; not public-chain Mainnet handoff evidence.",
  };
  writeJsonAtomic(path.join(ROOT, ".private", `${label}.ownership-fork-rehearsal.latest.json`), localEvidence);
  console.log("PASS ownership fork rehearsal transfer/resume/verify completed");
}

async function sweep(label: string): Promise<void> {
  const net = await ethers.provider.getNetwork();
  requireExpectedChain(label, net.chainId);
  forbidCiMainnet(net.chainId);
  const finalOwner = requireAddress("FINAL_OWNER_ADDRESS");
  const evp = evidencePath(label);
  if (!fs.existsSync(evp) || JSON.parse(fs.readFileSync(evp, "utf8")).status !== "PASSED") {
    throw new Error("Ownership PASSED evidence required before ETH sweep");
  }
  if (net.chainId === 1n && !process.env.OWNERSHIP_SWEEP_CONFIRMATION) throw new Error("Missing OWNERSHIP_SWEEP_CONFIRMATION");
  console.log(`DRY SAFE: sweep command gated; implementer must fund/sign locally to sweep ETH to ${finalOwner}. No tokens are swept.`);
}

async function main(): Promise<void> {
  const cmd = process.env.OWNERSHIP_COMMAND || process.argv.find((arg) => /^(sepolia|mainnet):/.test(arg)) || "";
  const label = cmd.includes("mainnet") ? "ethereum-mainnet" : "ethereum-sepolia";
  if (cmd.endsWith(":doctor")) return doctor(label);
  if (cmd.endsWith(":plan")) return plan(label);
  if (cmd.endsWith(":dry-run")) return plan(label);
  if (cmd.endsWith(":fork-rehearsal")) return forkRehearsal(label);
  if (cmd.endsWith(":transfer") || cmd.endsWith(":transfer-local-gated")) return transfer(label);
  if (cmd.endsWith(":verify")) return verify(label);
  if (cmd.endsWith(":evidence")) return evidence(label);
  if (cmd.endsWith(":sweep-deployer-local-gated")) return sweep(label);
  throw new Error(`Unknown ownership command ${cmd}`);
}

main().catch((error) => {
  console.error(`FAIL ${error.message}`);
  process.exit(1);
});
