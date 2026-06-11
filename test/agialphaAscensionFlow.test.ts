import { expect } from "chai";
import { ethers } from "hardhat";

async function futureDeadline(seconds = 86400) {
  const block = await ethers.provider.getBlock('latest');
  if (!block) throw new Error('no latest block');
  return block.timestamp + seconds;
}

async function deployCore() {
  const [deployer, treasury, sponsor, builder, reviewer] = await ethers.getSigners();
  const admin = deployer.address;

  const MockAGIALPHA = await ethers.getContractFactory("MockAGIALPHA");
  const agialpha = await MockAGIALPHA.deploy(deployer.address);
  await agialpha.waitForDeployment();

  await agialpha.transfer(sponsor.address, ethers.parseEther("10000"));
  await agialpha.transfer(builder.address, ethers.parseEther("10000"));
  await agialpha.transfer(reviewer.address, ethers.parseEther("10000"));

  const Reputation = await ethers.getContractFactory("ReputationRegistry");
  const reputation = await Reputation.deploy(admin);

  const ProofCards = await ethers.getContractFactory("ProofCardRegistry");
  const proofCards = await ProofCards.deploy(admin);

  const Credentials = await ethers.getContractFactory("ProofCredentialRegistry");
  const credentials = await Credentials.deploy(admin);

  const JobRegistry = await ethers.getContractFactory("JobRegistry");
  const jobRegistry = await JobRegistry.deploy(admin, await agialpha.getAddress(), treasury.address);

  const ClaimBond = await ethers.getContractFactory("JobClaimBondManager");
  const claimBond = await ClaimBond.deploy(admin, await agialpha.getAddress(), await jobRegistry.getAddress(), treasury.address);

  const ProofSubs = await ethers.getContractFactory("ProofSubmissionRegistry");
  const proofSubs = await ProofSubs.deploy(
    admin,
    await agialpha.getAddress(),
    await jobRegistry.getAddress(),
    await claimBond.getAddress(),
    await proofCards.getAddress(),
    await credentials.getAddress(),
    await reputation.getAddress(),
    treasury.address
  );

  const ReviewerBonds = await ethers.getContractFactory("ReviewerBondRegistry");
  const reviewerBonds = await ReviewerBonds.deploy(admin, await agialpha.getAddress(), await proofSubs.getAddress(), treasury.address);

  const ProofSeeds = await ethers.getContractFactory("ProofSeedRegistry");
  const proofSeeds = await ProofSeeds.deploy(admin, await agialpha.getAddress(), treasury.address);

  const Legacy = await ethers.getContractFactory("LegacyAGIJobManagerRegistry");
  const legacy = await Legacy.deploy(admin, "0xb3aaeb69b630f0299791679c063d68d6687481d1");

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

  return { deployer, treasury, sponsor, builder, reviewer, agialpha, reputation, proofCards, credentials, jobRegistry, claimBond, proofSubs, reviewerBonds, proofSeeds, legacy };
}

describe("GoalOS AGIALPHA Ascension flow", function () {
  it("creates a Proof Seed using AGIALPHA", async function () {
    const { sponsor, agialpha, proofSeeds } = await deployCore();
    await agialpha.connect(sponsor).approve(await proofSeeds.getAddress(), ethers.parseEther("1000"));
    await proofSeeds.connect(sponsor).createProofSeed(
      ethers.keccak256(ethers.toUtf8Bytes("customer support proof seed")),
      "ipfs://proof-seed",
      ethers.keccak256(ethers.toUtf8Bytes("customer-support"))
    );
    const seed = await proofSeeds.proofSeeds(1);
    expect(seed.sponsor).to.equal(sponsor.address);
  });

  it("runs post -> claim -> submit -> review -> proof card -> credential -> reputation with AGIALPHA", async function () {
    const { sponsor, builder, reviewer, agialpha, jobRegistry, claimBond, proofSubs, reviewerBonds, credentials, reputation } = await deployCore();

    await agialpha.connect(sponsor).approve(await jobRegistry.getAddress(), ethers.parseEther("1000"));
    await jobRegistry.connect(sponsor).postJob(
      "ipfs://job",
      ethers.keccak256(ethers.toUtf8Bytes("job metadata")),
      await agialpha.getAddress(),
      ethers.parseEther("100"),
      await futureDeadline(86400)
    );

    await agialpha.connect(builder).approve(await claimBond.getAddress(), ethers.parseEther("1000"));
    await claimBond.connect(builder).claimJob(1);

    await agialpha.connect(builder).approve(await proofSubs.getAddress(), ethers.parseEther("1000"));
    await proofSubs.connect(builder).submitProof(
      1,
      "ipfs://proof",
      ethers.keccak256(ethers.toUtf8Bytes("proof")),
      ethers.keccak256(ethers.toUtf8Bytes("proof card"))
    );

    await agialpha.connect(reviewer).approve(await reviewerBonds.getAddress(), ethers.parseEther("1000"));
    await reviewerBonds.connect(reviewer).bondAsReviewer("ipfs://reviewer");
    await reviewerBonds.connect(reviewer).reviewSubmission(
      1,
      true,
      ethers.keccak256(ethers.toUtf8Bytes("approved")),
      "ipfs://credential",
      ethers.keccak256(ethers.toUtf8Bytes("GOALOS_ASCENSION_BUILDER")),
      false
    );

    expect(await credentials.ownerOf(1)).to.equal(builder.address);
    expect(await reputation.scoreOf(builder.address)).to.be.greaterThan(0);
  });

  it("anchors a legacy AGIJobManager record as reviewed history", async function () {
    const { legacy } = await deployCore();
    await legacy.addLegacyRecord(
      88,
      ethers.keccak256(ethers.toUtf8Bytes("legacy event hash")),
      ethers.keccak256(ethers.toUtf8Bytes("legacy proof card hash")),
      "ipfs://legacy-record",
      true
    );
    const record = await legacy.records(1);
    expect(record.legacyJobId).to.equal(88);
    expect(record.accepted).to.equal(true);
  });
});
