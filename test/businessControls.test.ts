import { expect } from "chai";
import { ethers } from "hardhat";

async function deadline() {
  const block = await ethers.provider.getBlock("latest");
  if (!block) throw new Error("no block");
  return block.timestamp + 86400;
}

describe("GoalOS business override, accounting, and lifecycle controls", function () {
  it("tracks protected job liability and resolves through typed owner override", async function () {
    const [owner, treasury, sponsor, recipient] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("MockAGIALPHA");
    const token = await Token.deploy(owner.address);
    await token.transfer(sponsor.address, ethers.parseEther("1000"));

    const Jobs = await ethers.getContractFactory("JobRegistry");
    const jobs = await Jobs.deploy(owner.address, await token.getAddress(), treasury.address);
    await jobs.setPostingFee(0);
    await jobs.setRiskLimits(ethers.parseEther("500"), ethers.parseEther("250"));

    await token.connect(sponsor).approve(await jobs.getAddress(), ethers.parseEther("100"));
    await jobs.connect(sponsor).postJob("ipfs://job", ethers.keccak256(ethers.toUtf8Bytes("job")), await token.getAddress(), ethers.parseEther("100"), await deadline());

    expect(await jobs.protectedLiability(await token.getAddress())).to.equal(ethers.parseEther("100"));
    expect(await jobs.isSolvent(await token.getAddress())).to.equal(true);

    const reasonHash = ethers.keccak256(ethers.toUtf8Bytes("owner exceptional settlement"));
    const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("ticket-123"));
    await expect(jobs.ownerResolveJob(1, 5, recipient.address, reasonHash, evidenceHash))
      .to.emit(jobs, "BusinessOverrideExecuted")
      .and.to.emit(jobs, "BusinessJobResolved");

    expect(await jobs.protectedLiability(await token.getAddress())).to.equal(0);
    expect(await token.balanceOf(recipient.address)).to.equal(ethers.parseEther("100"));
  });

  it("rejects zero override evidence commitments", async function () {
    const [owner, treasury, sponsor, recipient] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("MockAGIALPHA");
    const token = await Token.deploy(owner.address);
    await token.transfer(sponsor.address, ethers.parseEther("1000"));
    const Jobs = await ethers.getContractFactory("JobRegistry");
    const jobs = await Jobs.deploy(owner.address, await token.getAddress(), treasury.address);
    await jobs.setPostingFee(0);
    await token.connect(sponsor).approve(await jobs.getAddress(), ethers.parseEther("100"));
    await jobs.connect(sponsor).postJob("ipfs://job", ethers.keccak256(ethers.toUtf8Bytes("job")), await token.getAddress(), ethers.parseEther("100"), await deadline());
    await expect(jobs.ownerResolveJob(1, 5, recipient.address, ethers.ZeroHash, ethers.keccak256(ethers.toUtf8Bytes("evidence"))))
      .to.be.revertedWithCustomError(jobs, "GoalOSOverrideMissingCommitment");
  });

  it("enforces finite lifecycle transitions and shutdown liability proof", async function () {
    const [owner] = await ethers.getSigners();
    const Lifecycle = await ethers.getContractFactory("GoalOSBusinessLifecycle");
    const lifecycle = await Lifecycle.deploy(owner.address);
    const reasonHash = ethers.keccak256(ethers.toUtf8Bytes("planned winddown"));
    const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("board-minute"));
    await lifecycle.transitionTo(2, reasonHash, evidenceHash, ethers.keccak256(ethers.toUtf8Bytes("root")), true);
    await expect(lifecycle.transitionTo(4, reasonHash, evidenceHash, ethers.keccak256(ethers.toUtf8Bytes("liability-root")), false))
      .to.be.revertedWithCustomError(lifecycle, "GoalOSLifecycleShutdownLiabilities");
    await lifecycle.transitionTo(4, reasonHash, evidenceHash, ethers.keccak256(ethers.toUtf8Bytes("zero-root")), true);
    expect(await lifecycle.mode()).to.equal(4);
  });
});
