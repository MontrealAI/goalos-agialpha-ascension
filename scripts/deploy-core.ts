import { ethers } from "hardhat";
import fs from "fs";
import path from "path";
import crypto from "crypto";
import { applyRuntimeAddressesToEnv } from "./validate-runtime-addresses";

const AGIALPHA_MAINNET = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const LEGACY_AGI_JOB_MANAGER_MAINNET = "0xb3aaeb69b630f0299791679c063d68d6687481d1";

type ChainInfo = { label: string; file: string; chainId: number; isMainnet: boolean };
const transactions: string[] = [];
const constructorArgs: Record<string, any[]> = {};
function sha256Hex(text: string) { return "0x" + crypto.createHash("sha256").update(text).digest("hex"); }

function jsonReplacer(_key: string, value: any) {
  return typeof value === "bigint" ? value.toString() : value;
}

function redactConstructorArg(value: any): any {
  if (typeof value === "bigint") return value.toString();
  if (typeof value === "string" && ethers.isAddress(value)) {
    if (value.toLowerCase() === AGIALPHA_MAINNET.toLowerCase()) return value;
    return { redactedAddress: true, commitmentHash: sha256Hex(value.toLowerCase()) };
  }
  if (Array.isArray(value)) return value.map(redactConstructorArg);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, nested]) => [key, redactConstructorArg(nested)]));
  }
  return value;
}

function publicConstructorArgs(info: ChainInfo) {
  return info.isMainnet ? redactConstructorArg(constructorArgs) : constructorArgs;
}

function constructorArgsCommitmentHash() {
  return sha256Hex(JSON.stringify(constructorArgs, jsonReplacer));
}

function chainInfo(chainId: number): ChainInfo {
  if (chainId === 1) return { label: "ethereum-mainnet", file: "ethereum-mainnet.agialpha.latest.json", chainId, isMainnet: true };
  if (chainId === 11155111) return { label: "ethereum-sepolia", file: "ethereum-sepolia.agialpha.latest.json", chainId, isMainnet: false };
  throw new Error(`Unsupported network chainId ${chainId}; expected Ethereum mainnet 1 or Sepolia 11155111.`);
}

function requireEnvAddress(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required deployment address: ${name}`);
  if (!ethers.isAddress(value) || value === ethers.ZeroAddress) throw new Error(`Invalid deployment address for ${name}: ${value}`);
  return value;
}

function optionalEnvAddress(name: string): string | undefined {
  const value = process.env[name];
  if (!value) return undefined;
  if (!ethers.isAddress(value) || value === ethers.ZeroAddress) throw new Error(`Invalid deployment address for ${name}: ${value}`);
  return value;
}

function evidencePath(entry: any, fallback: string): string {
  return (entry && typeof entry === "object" && entry.path) ? entry.path : (typeof entry === "string" ? entry : fallback);
}

function hashPublicFile(relativePath: string): string | undefined {
  if (!relativePath) return undefined;
  const absolutePath = path.join(__dirname, "..", relativePath);
  if (!fs.existsSync(absolutePath)) {
    if (process.env.NODE_ENV === "test") return undefined;
    throw new Error(`Mainnet deployment blocked. Public evidence file is missing: ${relativePath}`);
  }
  return "0x" + crypto.createHash("sha256").update(fs.readFileSync(absolutePath)).digest("hex");
}

function certificateEvidencePaths(): Record<string, string> {
  const certificatePath = path.join(__dirname, "..", "qa/mainnet-authorization-certificate.json");
  if (!fs.existsSync(certificatePath)) return {};
  const certificate = JSON.parse(fs.readFileSync(certificatePath, "utf8"));
  return certificate.evidence || {};
}

function enforceEthereumMainnetGates(info: ChainInfo) {
  if (!info.isMainnet) return;
  if (process.env.MAINNET_TARGET !== "ethereum") throw new Error("MAINNET_TARGET must be ethereum.");
  if (process.env.ALLOW_MAINNET_DEPLOYMENT !== "YES_PUBLIC_REPOSITORY_AUTHORIZED_MANUAL_DEPLOYMENT") throw new Error("Ethereum mainnet deployment blocked. Set ALLOW_MAINNET_DEPLOYMENT=YES_PUBLIC_REPOSITORY_AUTHORIZED_MANUAL_DEPLOYMENT only after public evidence-computed authorization is YES and the manual local deployer has typed confirmation.");
  const token = requireEnvAddress("AGIALPHA_TOKEN_ADDRESS");
  if (token.toLowerCase() !== AGIALPHA_MAINNET.toLowerCase()) throw new Error(`Ethereum mainnet deployment blocked. AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA_MAINNET}.`);
  if (process.env.MOCK_AGIALPHA_ADDRESS) throw new Error("Ethereum mainnet deployment blocked. MOCK_AGIALPHA_ADDRESS must not be set.");
  if (process.env.DEPLOY_NEW_AGIALPHA_TOKEN === "true") throw new Error("Ethereum mainnet deployment blocked. Deploying a new AGIALPHA token is forbidden.");
  requireEnvAddress("FOUNDER_ADDRESS");
  requireEnvAddress("TREASURY_ADDRESS");
  requireEnvAddress("COMMERCIALIZATION_PERFORMANCE_ADMIN");
  requireEnvAddress("PROOF_REWARDS_ADMIN");
  requireEnvAddress("LIQUIDITY_ADMIN");
  requireEnvAddress("SECURITY_ADMIN");
  requireEnvAddress("COMMUNITY_ADMIN");
}

async function deploy(name: string, args: any[] = []) {
  const Factory = await ethers.getContractFactory(name);
  constructorArgs[name] = args;
  const contract = await Factory.deploy(...args);
  const tx = contract.deploymentTransaction();
  if (tx?.hash) transactions.push(tx.hash);
  await contract.waitForDeployment();
  const address = await contract.getAddress();
  console.log(`${name}: ${address}`);
  return contract;
}

async function grant(contract: any, role: string, account: string, label: string) {
  const tx = await contract.grantRole(role, account);
  transactions.push(tx.hash);
  await tx.wait();
  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) === 1) {
    console.log(`grant ${label}: commitment ${sha256Hex(account.toLowerCase())}`);
  } else {
    console.log(`grant ${label}: ${account}`);
  }
}

export async function deployGoalOSAGIALPHAAscension() {
  const [deployer] = await ethers.getSigners();
  const net = await ethers.provider.getNetwork();
  const info = chainInfo(Number(net.chainId));
  if (info.isMainnet) applyRuntimeAddressesToEnv(deployer.address);
  enforceEthereumMainnetGates(info);

  const admin = deployer.address;
  const founder = requireEnvAddress("FOUNDER_ADDRESS");
  const treasury = requireEnvAddress("TREASURY_ADDRESS");
  const commercializationAdmin = requireEnvAddress("COMMERCIALIZATION_PERFORMANCE_ADMIN");
  const proofRewardsAdmin = requireEnvAddress("PROOF_REWARDS_ADMIN");
  const liquidityAdmin = requireEnvAddress("LIQUIDITY_ADMIN");
  const securityAdmin = requireEnvAddress("SECURITY_ADMIN");
  const communityAdmin = requireEnvAddress("COMMUNITY_ADMIN");

  let agialphaToken = optionalEnvAddress("AGIALPHA_TOKEN_ADDRESS");
  const mainnetTokenProvidedOnNonMainnet = Boolean(agialphaToken) && !info.isMainnet && agialphaToken!.toLowerCase() === AGIALPHA_MAINNET.toLowerCase();
  if ((!agialphaToken || mainnetTokenProvidedOnNonMainnet) && !info.isMainnet) {
    const mock = await deploy("MockAGIALPHA", [deployer.address]);
    agialphaToken = await mock.getAddress();
    console.log(`Non-mainnet rehearsal deployed MockAGIALPHA: ${agialphaToken}`);
  }
  if (!agialphaToken) throw new Error("AGIALPHA_TOKEN_ADDRESS required.");
  let tokenCode = await ethers.provider.getCode(agialphaToken);
  if (tokenCode === "0x") {
    if (!info.isMainnet && process.env.ALLOW_NONMAINNET_MOCK_ON_MISSING_TOKEN === "YES") {
      const mock = await deploy("MockAGIALPHA", [deployer.address]);
      agialphaToken = await mock.getAddress();
      tokenCode = await ethers.provider.getCode(agialphaToken);
      console.log(`Non-mainnet token address had no code; deployed MockAGIALPHA due to explicit override: ${agialphaToken}`);
    } else {
      throw new Error(`No ERC20 contract code found at AGIALPHA_TOKEN_ADDRESS ${agialphaToken}`);
    }
  }
  const legacyAGIJobManager = optionalEnvAddress("LEGACY_AGI_JOB_MANAGER_ADDRESS") || LEGACY_AGI_JOB_MANAGER_MAINNET;

  console.log(`Deploying GoalOS AGIALPHA Ascension v4.3 to ${info.label}`);
  if (info.isMainnet) {
    console.log({ deployerCommitmentHash: sha256Hex(deployer.address), adminCommitmentHash: sha256Hex(admin), founderCommitmentHash: sha256Hex(founder), treasuryCommitmentHash: sha256Hex(treasury), agialphaToken, legacyAGIJobManager });
  } else {
    console.log({ deployer: deployer.address, admin, founder, treasury, agialphaToken, legacyAGIJobManager });
  }

  const performanceVaultArgs = [commercializationAdmin, agialphaToken];
  const proofRewardsVaultArgs = [proofRewardsAdmin, agialphaToken, "AGIALPHA Proof Jobs / Builder Rewards"];
  const liquidityVaultArgs = [liquidityAdmin, agialphaToken, "AGIALPHA Liquidity / Operations"];
  const securityVaultArgs = [securityAdmin, agialphaToken, "Security / Audits / Bug Bounties"];
  const communityVaultArgs = [communityAdmin, agialphaToken, "AGI Club / Genesis Community / Credentials"];
  const performanceVault = await deploy("CommercializationPerformanceVault", performanceVaultArgs);
  const proofRewardsVault = await deploy("TokenReserveVault", proofRewardsVaultArgs);
  constructorArgs.ProofRewardsVault = proofRewardsVaultArgs;
  const liquidityVault = await deploy("TokenReserveVault", liquidityVaultArgs);
  constructorArgs.LiquidityVault = liquidityVaultArgs;
  const securityVault = await deploy("TokenReserveVault", securityVaultArgs);
  constructorArgs.SecurityVault = securityVaultArgs;
  const communityVault = await deploy("TokenReserveVault", communityVaultArgs);
  constructorArgs.CommunityVault = communityVaultArgs;

  const proofSeeds = await deploy("ProofSeedRegistry", [admin, agialphaToken, treasury]);
  const legacyRegistry = await deploy("LegacyAGIJobManagerRegistry", [admin, legacyAGIJobManager]);
  const reputation = await deploy("ReputationRegistry", [admin]);
  const referrals = await deploy("ReferralRegistry", [admin]);
  const proofCards = await deploy("ProofCardRegistry", [admin]);
  const credentials = await deploy("ProofCredentialRegistry", [admin]);
  const jobRegistry = await deploy("JobRegistry", [admin, agialphaToken, treasury]);
  const claimBond = await deploy("JobClaimBondManager", [admin, agialphaToken, await jobRegistry.getAddress(), treasury]);
  const premiumAccess = await deploy("PremiumAccessRegistry", [admin, agialphaToken, await reputation.getAddress()]);
  const proofSubmissions = await deploy("ProofSubmissionRegistry", [admin, agialphaToken, await jobRegistry.getAddress(), await claimBond.getAddress(), await proofCards.getAddress(), await credentials.getAddress(), await reputation.getAddress(), treasury]);
  const reviewerBonds = await deploy("ReviewerBondRegistry", [admin, agialphaToken, await proofSubmissions.getAddress(), treasury]);
  const treasuryRouter = await deploy("TreasuryRouter", [admin, treasury]);
  const protocolConfig = await deploy("ProtocolConfigRegistry", [admin]);
  const launchGates = await deploy("LaunchGateRegistry", [admin]);
  const disputes = await deploy("DisputeRegistry", [admin, await reputation.getAddress()]);
  const appeals = await deploy("AppealRegistry", [admin]);
  const sponsors = await deploy("SponsorRegistry", [admin]);
  const builders = await deploy("BuilderProfileRegistry", [admin]);
  const revocations = await deploy("CredentialRevocationRegistry", [admin, await credentials.getAddress()]);

  // AEP-001 / GoalOS proof-of-evolution spine.
  const aepAgents = await deploy("AEPAgentRegistry", [admin]);
  const aepArtifacts = await deploy("AEPArtifactRegistry", [admin]);
  const aepCommits = await deploy("AEPGoalOSCommitRegistry", [admin, agialphaToken, treasury]);
  const aepRuns = await deploy("AEPRunCommitmentRegistry", [admin]);
  const aepProofLedger = await deploy("AEPProofLedger", [admin]);
  const aepEvalRegistry = await deploy("AEPEvalRegistry", [admin]);
  const aepAttestations = await deploy("AEPAttestationRegistry", [admin]);
  const aepSelectionGate = await deploy("AEPSelectionGate", [admin]);
  const aepRolloutRouter = await deploy("AEPRolloutRouter", [admin]);
  const aepRollbackRegistry = await deploy("AEPRollbackRegistry", [admin]);
  const aepEvidenceDockets = await deploy("AEPEvidenceDocketRegistry", [admin]);
  const aepProofBundles = await deploy("AEPProofBundleRegistry", [admin]);
  const alphaWorkUnits = await deploy("AlphaWorkUnitLedger", [admin]);
  const mandateEpochs = await deploy("MandateEpochRegistry", [admin, agialphaToken, treasury]);
  const agiEthNamespace = await deploy("AGIEthNamespaceRegistry", [admin]);
  const aepConformance = await deploy("AEPConformanceRegistry", [admin]);
  const aepClaimBoundaries = await deploy("AEPClaimBoundaryRegistry", [admin]);
  const aepReplayRegistry = await deploy("AEPReplayRegistry", [admin]);
  const aepCommitReveal = await deploy("AEPCommitRevealValidationRegistry", [admin]);
  const aepEvaluatorStaking = await deploy("AEPEvaluatorStakingRegistry", [admin, agialphaToken, treasury]);
  const aepSlashingCourt = await deploy("AEPSlashingCourt", [admin, await aepEvaluatorStaking.getAddress()]);
  const aepRewardVault = await deploy("AEPRewardVault", [admin, agialphaToken]);
  const aepChronicle = await deploy("AEPChronicleRegistry", [admin]);
  const aepFalsification = await deploy("AEPFalsificationRegistry", [admin]);

  const OPERATOR_ROLE = await jobRegistry.OPERATOR_ROLE();
  await grant(jobRegistry, OPERATOR_ROLE, await claimBond.getAddress(), "JobRegistry <- ClaimBond");
  await grant(jobRegistry, OPERATOR_ROLE, await proofSubmissions.getAddress(), "JobRegistry <- ProofSubmissions");
  await grant(claimBond, OPERATOR_ROLE, await proofSubmissions.getAddress(), "ClaimBond <- ProofSubmissions");
  await grant(proofSubmissions, OPERATOR_ROLE, await reviewerBonds.getAddress(), "ProofSubmissions <- ReviewerBonds");
  await grant(proofCards, OPERATOR_ROLE, await proofSubmissions.getAddress(), "ProofCards <- ProofSubmissions");
  await grant(credentials, OPERATOR_ROLE, await proofSubmissions.getAddress(), "Credentials <- ProofSubmissions");
  await grant(credentials, OPERATOR_ROLE, await revocations.getAddress(), "Credentials <- Revocations");
  await grant(reputation, OPERATOR_ROLE, await proofSubmissions.getAddress(), "Reputation <- ProofSubmissions");
  await grant(referrals, OPERATOR_ROLE, await proofSubmissions.getAddress(), "Referrals <- ProofSubmissions");
  await grant(proofSeeds, OPERATOR_ROLE, deployer.address, "ProofSeeds <- deployer");
  await grant(legacyRegistry, OPERATOR_ROLE, deployer.address, "LegacyRegistry <- deployer");
  await grant(protocolConfig, OPERATOR_ROLE, deployer.address, "ProtocolConfig <- deployer");
  await grant(launchGates, OPERATOR_ROLE, deployer.address, "LaunchGates <- deployer");
  await grant(aepEvaluatorStaking, OPERATOR_ROLE, await aepSlashingCourt.getAddress(), "EvaluatorStaking <- SlashingCourt");

  const evidencePaths = info.isMainnet ? certificateEvidencePaths() : {};
  const deployment = {
    package: "GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY",
    network: info.label,
    chain: info.isMainnet ? "ethereum" : "ethereum-sepolia-or-local",
    chainId: info.chainId,
    deployedAt: new Date().toISOString(),
    commit: process.env.GITHUB_SHA || "LOCAL_PRIVATE_OPERATOR",
    deployer: info.isMainnet ? undefined : deployer.address,
    deployerCommitmentHash: sha256Hex(deployer.address),
    admin: info.isMainnet ? undefined : admin,
    founder: info.isMainnet ? undefined : founder,
    treasury: info.isMainnet ? undefined : treasury,
    agialphaToken,
    mockAgialphaUsed: false,
    newAgialphaTokenDeployed: false,
    legacyAGIJobManager,
    transactions,
    constructorArgs: publicConstructorArgs(info),
    constructorArgsRedacted: info.isMainnet,
    constructorArgsCommitmentHash: constructorArgsCommitmentHash(),
    roleAssignmentsCommitmentHash: sha256Hex(JSON.stringify({ commercializationAdmin, proofRewardsAdmin, liquidityAdmin, securityAdmin, communityAdmin }, jsonReplacer)),
    mainnetAuthorizationCertificateHash: (info.isMainnet ? hashPublicFile("qa/mainnet-authorization-certificate.json") : undefined),
    toolchainClearanceHash: (info.isMainnet ? hashPublicFile(evidencePath(evidencePaths.toolchainClearance, "qa/public-toolchain-clearance-evidence.json")) : undefined),
    localRehearsalEvidenceHash: (info.isMainnet ? hashPublicFile(evidencePath(evidencePaths.localRehearsal, "qa/local-rehearsal-report.json")) : undefined),
    agialphaTokenVerificationHash: (info.isMainnet ? hashPublicFile(evidencePath(evidencePaths.agialphaTokenVerification, "qa/public-agialpha-token-verification.json")) : undefined),
    publicGovernanceApprovalHash: (info.isMainnet ? hashPublicFile(evidencePath(evidencePaths.publicGovernanceApproval, "qa/public-governance-approval-evidence.json")) : undefined),
    mainnetGates: info.isMainnet ? {
      sourceOfTruth: "qa/mainnet-authorization-certificate.json",
      privateOperatorAuthorizationPackageRequired: false,
      externalAuditRequired: false,
      ciCanDeployMainnet: false,
      runtimeSecretsStoredInGitHub: false
    } : null,
    contracts: {
      AGIALPHA: agialphaToken,
      CommercializationPerformanceVault: await performanceVault.getAddress(),
      ProofRewardsVault: await proofRewardsVault.getAddress(),
      LiquidityVault: await liquidityVault.getAddress(),
      SecurityVault: await securityVault.getAddress(),
      CommunityVault: await communityVault.getAddress(),
      ProofSeedRegistry: await proofSeeds.getAddress(),
      LegacyAGIJobManagerRegistry: await legacyRegistry.getAddress(),
      ReputationRegistry: await reputation.getAddress(),
      ReferralRegistry: await referrals.getAddress(),
      ProofCardRegistry: await proofCards.getAddress(),
      ProofCredentialRegistry: await credentials.getAddress(),
      JobRegistry: await jobRegistry.getAddress(),
      JobClaimBondManager: await claimBond.getAddress(),
      PremiumAccessRegistry: await premiumAccess.getAddress(),
      ProofSubmissionRegistry: await proofSubmissions.getAddress(),
      ReviewerBondRegistry: await reviewerBonds.getAddress(),
      TreasuryRouter: await treasuryRouter.getAddress(),
      ProtocolConfigRegistry: await protocolConfig.getAddress(),
      LaunchGateRegistry: await launchGates.getAddress(),
      DisputeRegistry: await disputes.getAddress(),
      AppealRegistry: await appeals.getAddress(),
      SponsorRegistry: await sponsors.getAddress(),
      BuilderProfileRegistry: await builders.getAddress(),
      CredentialRevocationRegistry: await revocations.getAddress(),
      AEPAgentRegistry: await aepAgents.getAddress(),
      AEPArtifactRegistry: await aepArtifacts.getAddress(),
      AEPGoalOSCommitRegistry: await aepCommits.getAddress(),
      AEPRunCommitmentRegistry: await aepRuns.getAddress(),
      AEPProofLedger: await aepProofLedger.getAddress(),
      AEPEvalRegistry: await aepEvalRegistry.getAddress(),
      AEPAttestationRegistry: await aepAttestations.getAddress(),
      AEPSelectionGate: await aepSelectionGate.getAddress(),
      AEPRolloutRouter: await aepRolloutRouter.getAddress(),
      AEPRollbackRegistry: await aepRollbackRegistry.getAddress(),
      AEPEvidenceDocketRegistry: await aepEvidenceDockets.getAddress(),
      AEPProofBundleRegistry: await aepProofBundles.getAddress(),
      AlphaWorkUnitLedger: await alphaWorkUnits.getAddress(),
      MandateEpochRegistry: await mandateEpochs.getAddress(),
      AGIEthNamespaceRegistry: await agiEthNamespace.getAddress(),
      AEPConformanceRegistry: await aepConformance.getAddress(),
      AEPClaimBoundaryRegistry: await aepClaimBoundaries.getAddress(),
      AEPReplayRegistry: await aepReplayRegistry.getAddress(),
      AEPCommitRevealValidationRegistry: await aepCommitReveal.getAddress(),
      AEPEvaluatorStakingRegistry: await aepEvaluatorStaking.getAddress(),
      AEPSlashingCourt: await aepSlashingCourt.getAddress(),
      AEPRewardVault: await aepRewardVault.getAddress(),
      AEPChronicleRegistry: await aepChronicle.getAddress(),
      AEPFalsificationRegistry: await aepFalsification.getAddress()
    },
    note: "Uses existing AGIALPHA as coordination asset. No AGIALPHA token is minted or deployed on Ethereum mainnet. Intelligence stays off-chain; proof commitments, attestations, settlement and evolution rights are coordinated on-chain."
  };

  fs.mkdirSync(path.join(__dirname, "..", "deployments"), { recursive: true });
  const manifest = JSON.stringify(deployment, null, 2) + "\n";
  const manifestPath = path.join(__dirname, "..", "deployments", info.file);
  fs.writeFileSync(manifestPath, manifest);
  if (info.isMainnet) fs.writeFileSync(path.join(__dirname, "..", "deployments", "ethereum-mainnet.agialpha.latest.sha256"), crypto.createHash("sha256").update(manifest).digest("hex") + "\n");
  console.log(`Deployment written to deployments/${info.file}`);
  return deployment;
}

if (require.main === module) {
  deployGoalOSAGIALPHAAscension().catch((error) => { console.error(error); process.exitCode = 1; });
}
