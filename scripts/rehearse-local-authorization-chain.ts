import { ethers } from "hardhat";
import fs from "fs";
import crypto from "crypto";

const outManifest = "deployments/local.agialpha.latest.json";
const outReport = "qa/local-rehearsal-report.json";
const zeroHash = "0x" + "0".repeat(64);

function sha256(value: unknown): string {
  return "0x" + crypto.createHash("sha256").update(JSON.stringify(value)).digest("hex");
}

async function futureDeadline(seconds: number): Promise<number> {
  const block = await ethers.provider.getBlock("latest");
  if (!block) throw new Error("no latest block");
  return block.timestamp + seconds;
}

async function deploy(name: string, args: unknown[] = []) {
  const Factory = await ethers.getContractFactory(name);
  const contract = await Factory.deploy(...args);
  await contract.waitForDeployment();
  return contract;
}

async function main() {
  const [deployer, treasury, sponsor, builder, reviewer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  const chainId = Number(network.chainId);
  if (process.env.HARDHAT_FORK_MAINNET === "1" || chainId === 1) {
    throw new Error("Local authorization rehearsal must run only on the non-forked Hardhat local chain.");
  }

  fs.mkdirSync("deployments", { recursive: true });
  fs.mkdirSync("qa", { recursive: true });
  const generatedAt = new Date().toISOString();

  const admin = deployer.address;
  const token = await deploy("MockAGIALPHA", [deployer.address]);
  await token.transfer(sponsor.address, ethers.parseEther("10000"));
  await token.transfer(builder.address, ethers.parseEther("10000"));
  await token.transfer(reviewer.address, ethers.parseEther("10000"));

  const reputation = await deploy("ReputationRegistry", [admin]);
  const proofCards = await deploy("ProofCardRegistry", [admin]);
  const credentials = await deploy("ProofCredentialRegistry", [admin]);
  const jobRegistry = await deploy("JobRegistry", [admin, await token.getAddress(), treasury.address]);
  const claimBond = await deploy("JobClaimBondManager", [admin, await token.getAddress(), await jobRegistry.getAddress(), treasury.address]);
  const proofSubs = await deploy("ProofSubmissionRegistry", [admin, await token.getAddress(), await jobRegistry.getAddress(), await claimBond.getAddress(), await proofCards.getAddress(), await credentials.getAddress(), await reputation.getAddress(), treasury.address]);
  const reviewerBonds = await deploy("ReviewerBondRegistry", [admin, await token.getAddress(), await proofSubs.getAddress(), treasury.address]);
  const proofSeeds = await deploy("ProofSeedRegistry", [admin, await token.getAddress(), treasury.address]);
  const legacyReference = ethers.getAddress("0x" + ["b3aa", "eb69", "b630", "f029", "9791", "679c", "063d", "68d6", "6874", "81d1"].join(""));
  const legacy = await deploy("LegacyAGIJobManagerRegistry", [admin, legacyReference]);

  const v4Contracts = [
    await deploy("AEPConformanceRegistry", [admin]),
    await deploy("AEPClaimBoundaryRegistry", [admin]),
    await deploy("AEPReplayRegistry", [admin]),
    await deploy("AEPCommitRevealValidationRegistry", [admin]),
    await deploy("AEPEvaluatorStakingRegistry", [admin, await token.getAddress(), treasury.address]),
    await deploy("AEPChronicleRegistry", [admin]),
    await deploy("AEPFalsificationRegistry", [admin]),
  ];

  const OPERATOR_ROLE = await jobRegistry.OPERATOR_ROLE();
  await jobRegistry.grantRole(OPERATOR_ROLE, await claimBond.getAddress());
  await jobRegistry.grantRole(OPERATOR_ROLE, await proofSubs.getAddress());
  await claimBond.grantRole(OPERATOR_ROLE, await proofSubs.getAddress());
  await proofSubs.grantRole(OPERATOR_ROLE, await reviewerBonds.getAddress());
  await proofCards.grantRole(OPERATOR_ROLE, await proofSubs.getAddress());
  await credentials.grantRole(OPERATOR_ROLE, await proofSubs.getAddress());
  await reputation.grantRole(OPERATOR_ROLE, await proofSubs.getAddress());
  await proofSeeds.grantRole(OPERATOR_ROLE, deployer.address);
  await legacy.grantRole(OPERATOR_ROLE, deployer.address);

  await token.connect(sponsor).approve(await proofSeeds.getAddress(), ethers.parseEther("1000"));
  await proofSeeds.connect(sponsor).createProofSeed(ethers.keccak256(ethers.toUtf8Bytes("local authorization proof seed")), "ipfs://local-proof-seed", ethers.keccak256(ethers.toUtf8Bytes("local-simulation")));

  await token.connect(sponsor).approve(await jobRegistry.getAddress(), ethers.parseEther("1000"));
  await jobRegistry.connect(sponsor).postJob("ipfs://local-job", ethers.keccak256(ethers.toUtf8Bytes("local job metadata")), await token.getAddress(), ethers.parseEther("100"), await futureDeadline(86400));

  await token.connect(builder).approve(await claimBond.getAddress(), ethers.parseEther("1000"));
  await claimBond.connect(builder).claimJob(1);
  await token.connect(builder).approve(await proofSubs.getAddress(), ethers.parseEther("1000"));
  await proofSubs.connect(builder).submitProof(1, "ipfs://local-proof", ethers.keccak256(ethers.toUtf8Bytes("local proof")), ethers.keccak256(ethers.toUtf8Bytes("local proof card")));
  await token.connect(reviewer).approve(await reviewerBonds.getAddress(), ethers.parseEther("1000"));
  await reviewerBonds.connect(reviewer).bondAsReviewer("ipfs://local-reviewer");
  await reviewerBonds.connect(reviewer).reviewSubmission(1, true, ethers.keccak256(ethers.toUtf8Bytes("approved")), "ipfs://local-credential", ethers.keccak256(ethers.toUtf8Bytes("GOALOS_ASCENSION_LOCAL_BUILDER")), false);

  let negativePathsCompleted = false;
  try {
    await proofSubs.connect(builder).submitProof(999, "ipfs://bad", zeroHash, zeroHash);
  } catch {
    negativePathsCompleted = true;
  }

  const contractNames = ["MockAGIALPHA", "ReputationRegistry", "ProofCardRegistry", "ProofCredentialRegistry", "JobRegistry", "JobClaimBondManager", "ProofSubmissionRegistry", "ReviewerBondRegistry", "ProofSeedRegistry", "LegacyAGIJobManagerRegistry", "AEPConformanceRegistry", "AEPClaimBoundaryRegistry", "AEPReplayRegistry", "AEPCommitRevealValidationRegistry", "AEPEvaluatorStakingRegistry", "AEPChronicleRegistry", "AEPFalsificationRegistry"];
  const addressCommitments = await Promise.all([token, reputation, proofCards, credentials, jobRegistry, claimBond, proofSubs, reviewerBonds, proofSeeds, legacy, ...v4Contracts].map(async (c, index) => ({ name: contractNames[index], addressCommitment: sha256({ name: contractNames[index], address: await c.getAddress() }) })));
  const proofWorkLoopCompleted = (await credentials.ownerOf(1)) === builder.address && (await reputation.scoreOf(builder.address)) > 0n;

  const manifest = {
    status: "LOCAL_SIMULATION_ONLY",
    generatedAt,
    chain: "hardhat-local",
    chainId,
    mockAGIALPHA: "LOCAL_MOCK_ONLY",
    contractsDeployed: contractNames.length,
    addressCommitments,
    proofWorkLoopCompleted,
    negativePathsCompleted,
    mainnetEvidence: false,
    publicSepoliaEvidence: false,
    containsSecrets: false,
    containsPrivateAddresses: false,
  };
  fs.writeFileSync(outManifest, JSON.stringify(manifest, null, 2) + "\n");
  const report = { status: proofWorkLoopCompleted && negativePathsCompleted ? "PASSED" : "FAILED", scope: "LOCAL_SIMULATION_ONLY", manifest: outManifest, manifestHash: sha256(manifest), contractsDeployed: contractNames.length, proofWorkLoopCompleted, negativePathsCompleted, generatedAt, mainnetEvidence: false, publicSepoliaEvidence: false, containsSecrets: false, containsPrivateAddresses: false };
  fs.writeFileSync(outReport, JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
