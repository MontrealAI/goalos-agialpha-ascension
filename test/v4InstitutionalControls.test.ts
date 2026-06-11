import { expect } from "chai";
import { ethers, network } from "hardhat";

async function futureTime(seconds: number) {
  const block = await ethers.provider.getBlock("latest");
  if (!block) throw new Error("no latest block");
  return block.timestamp + seconds;
}

async function deployV4Controls() {
  const [deployer, treasury, evaluator, reporter, recipient] = await ethers.getSigners();
  const MockAGIALPHA = await ethers.getContractFactory("MockAGIALPHA");
  const token = await MockAGIALPHA.deploy(deployer.address);
  await token.waitForDeployment();
  await token.transfer(evaluator.address, ethers.parseEther("10000"));
  await token.transfer(reporter.address, ethers.parseEther("10000"));

  const Conformance = await ethers.getContractFactory("AEPConformanceRegistry");
  const conformance = await Conformance.deploy(deployer.address);
  const Claims = await ethers.getContractFactory("AEPClaimBoundaryRegistry");
  const claims = await Claims.deploy(deployer.address);
  const Replay = await ethers.getContractFactory("AEPReplayRegistry");
  const replay = await Replay.deploy(deployer.address);
  const CommitReveal = await ethers.getContractFactory("AEPCommitRevealValidationRegistry");
  const commitReveal = await CommitReveal.deploy(deployer.address);
  const Staking = await ethers.getContractFactory("AEPEvaluatorStakingRegistry");
  const staking = await Staking.deploy(deployer.address, await token.getAddress(), treasury.address);
  const Court = await ethers.getContractFactory("AEPSlashingCourt");
  const court = await Court.deploy(deployer.address, await staking.getAddress());
  const Reward = await ethers.getContractFactory("AEPRewardVault");
  const reward = await Reward.deploy(deployer.address, await token.getAddress());
  const Chronicle = await ethers.getContractFactory("AEPChronicleRegistry");
  const chronicle = await Chronicle.deploy(deployer.address);
  const Falsification = await ethers.getContractFactory("AEPFalsificationRegistry");
  const falsification = await Falsification.deploy(deployer.address);

  const OPERATOR_ROLE = await staking.OPERATOR_ROLE();
  await staking.grantRole(OPERATOR_ROLE, await court.getAddress());

  return { deployer, treasury, evaluator, reporter, recipient, token, conformance, claims, replay, commitReveal, staking, court, reward, chronicle, falsification };
}

describe("GoalOS AGIALPHA Ascension v4 institutional controls", function () {
  it("records conformance, claim boundary, replay, chronicle and falsification records", async function () {
    const x = await deployV4Controls();
    await x.conformance.recordConformance(
      ethers.keccak256(ethers.toUtf8Bytes("system")),
      5,
      ethers.keccak256(ethers.toUtf8Bytes("docket")),
      ethers.keccak256(ethers.toUtf8Bytes("auditor")),
      ethers.keccak256(ethers.toUtf8Bytes("claims")),
      "ipfs://conformance"
    );
    await x.claims.registerClaimBoundary(
      ethers.keccak256(ethers.toUtf8Bytes("safe claim")),
      ethers.keccak256(ethers.toUtf8Bytes("not claimed")),
      ethers.keccak256(ethers.toUtf8Bytes("required evidence")),
      ethers.keccak256(ethers.toUtf8Bytes("legal review")),
      ethers.keccak256(ethers.toUtf8Bytes("copy")),
      "ipfs://claims"
    );
    await x.replay.recordReplay(
      1,
      ethers.keccak256(ethers.toUtf8Bytes("replay")),
      ethers.keccak256(ethers.toUtf8Bytes("container")),
      ethers.keccak256(ethers.toUtf8Bytes("deps")),
      ethers.keccak256(ethers.toUtf8Bytes("result")),
      1,
      "ipfs://replay"
    );
    await x.chronicle.recordEntry(ethers.keccak256(ethers.toUtf8Bytes("PROOF")), ethers.keccak256(ethers.toUtf8Bytes("entry")), ethers.keccak256(ethers.toUtf8Bytes("subject")), "ipfs://chronicle");
    await x.falsification.connect(x.reporter).reportFalsification(ethers.keccak256(ethers.toUtf8Bytes("condition")), ethers.keccak256(ethers.toUtf8Bytes("evidence")), ethers.keccak256(ethers.toUtf8Bytes("claim")), "ipfs://falsification");
    expect((await x.conformance.records(1)).active).to.equal(true);
    expect((await x.chronicle.entries(1)).entryHash).to.equal(ethers.keccak256(ethers.toUtf8Bytes("entry")));
  });

  it("supports commit-reveal validation", async function () {
    const x = await deployV4Controls();
    await x.commitReveal.setValidatorAllowed(x.evaluator.address, true);
    await x.commitReveal.openValidationRound(ethers.keccak256(ethers.toUtf8Bytes("PROOF_BUNDLE")), 1, 5, 5, 1, "ipfs://round");
    const verdictHash = ethers.keccak256(ethers.toUtf8Bytes("pass"));
    const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("evidence"));
    const salt = ethers.keccak256(ethers.toUtf8Bytes("salt"));
    const commitment = ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(["uint256","bytes32","uint16","bytes32","bytes32"], [1, verdictHash, 9000, evidenceHash, salt]));
    await x.commitReveal.connect(x.evaluator).commitVerdict(1, commitment);
    await network.provider.send("evm_increaseTime", [6]);
    await network.provider.send("evm_mine");
    await x.commitReveal.connect(x.evaluator).revealVerdict(1, verdictHash, 9000, evidenceHash, salt);
    await network.provider.send("evm_increaseTime", [6]);
    await network.provider.send("evm_mine");
    await x.commitReveal.finalizeRound(1, ethers.keccak256(ethers.toUtf8Bytes("final")));
    expect((await x.commitReveal.rounds(1)).revealCount).to.equal(1);
  });

  it("supports evaluator staking, slashing court, and reward vault", async function () {
    const x = await deployV4Controls();
    await x.token.connect(x.evaluator).approve(await x.staking.getAddress(), ethers.parseEther("1000"));
    await x.staking.connect(x.evaluator).stake(ethers.parseEther("200"), "ipfs://evaluator");
    await x.court.openCase(x.evaluator.address, ethers.parseEther("50"), ethers.keccak256(ethers.toUtf8Bytes("evidence")), ethers.keccak256(ethers.toUtf8Bytes("bad attestation")), "ipfs://case");
    await x.court.resolveCase(1, 2, ethers.parseEther("25"), ethers.keccak256(ethers.toUtf8Bytes("slash")));
    expect((await x.staking.stakes(x.evaluator.address)).amount).to.equal(ethers.parseEther("175"));

    await x.token.connect(x.reporter).approve(await x.reward.getAddress(), ethers.parseEther("1000"));
    await x.reward.connect(x.reporter).fund(ethers.parseEther("100"));
    await x.reward.payReward(x.recipient.address, ethers.parseEther("10"), 1, 1000, ethers.keccak256(ethers.toUtf8Bytes("reward")), "ipfs://reward");
    expect(await x.token.balanceOf(x.recipient.address)).to.equal(ethers.parseEther("10"));
  });
});
