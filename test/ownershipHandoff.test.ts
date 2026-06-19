import { expect } from "chai";
import { ethers } from "hardhat";

const ERC173_INTERFACE_ID = "0x7f5828d0";

async function roles(c: any) {
  return [
    await c.DEFAULT_ADMIN_ROLE(),
    await c.PROTOCOL_ADMIN_ROLE(),
    await c.OPERATOR_ROLE(),
    await c.REVIEWER_MANAGER_ROLE(),
    await c.TREASURY_ROLE(),
    await c.PAUSER_ROLE(),
    await c.VAULT_MANAGER_ROLE(),
  ];
}

describe("GoalOS ownership handoff", function () {
  it("sets constructor admin as owner and does not privilege deployer when admin differs", async function () {
    const [deployer, admin] = await ethers.getSigners();
    const Registry = await ethers.getContractFactory("ProofCardRegistry", deployer);
    const registry = await Registry.deploy(admin.address);
    await registry.waitForDeployment();

    expect(await registry.owner()).to.equal(admin.address);
    for (const role of await roles(registry)) {
      expect(await registry.hasRole(role, admin.address)).to.equal(true);
      expect(await registry.hasRole(role, deployer.address)).to.equal(false);
    }
    expect(await registry.supportsInterface(ERC173_INTERFACE_ID)).to.equal(true);
  });

  it("atomically migrates owner-held roles and preserves delegated roles", async function () {
    const [owner, finalOwner, delegated, stranger] = await ethers.getSigners();
    const Registry = await ethers.getContractFactory("ProofCardRegistry", owner);
    const registry = await Registry.deploy(owner.address);
    await registry.waitForDeployment();
    const OPERATOR_ROLE = await registry.OPERATOR_ROLE();
    await registry.grantRole(OPERATOR_ROLE, delegated.address);

    await expect(registry.connect(stranger).transferOwnership(finalOwner.address)).to.be.revertedWith("Ownable: caller is not the owner");
    await expect(registry.transferOwnership(ethers.ZeroAddress)).to.be.revertedWith("Ownable: new owner is the zero address");
    await expect(registry.transferOwnership(owner.address)).to.be.revertedWithCustomError(registry, "GoalOSOwnershipNoOp");
    await expect(registry.renounceOwnership()).to.be.revertedWithCustomError(registry, "GoalOSOwnershipRenunciationDisabled");
    await expect(registry.grantRole(await registry.DEFAULT_ADMIN_ROLE(), stranger.address)).to.be.revertedWithCustomError(registry, "GoalOSDefaultAdminRoleCoupledToOwner");
    await expect(registry.revokeRole(await registry.DEFAULT_ADMIN_ROLE(), owner.address)).to.be.revertedWithCustomError(registry, "GoalOSDefaultAdminRoleCoupledToOwner");
    await expect(registry.renounceRole(await registry.DEFAULT_ADMIN_ROLE(), owner.address)).to.be.revertedWithCustomError(registry, "GoalOSDefaultAdminRoleCoupledToOwner");

    await expect(registry.transferOwnership(finalOwner.address))
      .to.emit(registry, "OwnershipTransferStarted")
      .withArgs(owner.address, finalOwner.address);
    expect(await registry.pendingOwner()).to.equal(finalOwner.address);
    await expect(registry.connect(stranger).acceptOwnership()).to.be.revertedWithCustomError(registry, "GoalOSOwnershipTransferPending");
    await expect(registry.connect(finalOwner).acceptOwnership()).to.be.revertedWithCustomError(registry, "GoalOSOwnershipTransferDelayNotElapsed");
    await ethers.provider.send("evm_increaseTime", [24 * 60 * 60]);
    await ethers.provider.send("evm_mine", []);
    await expect(registry.connect(finalOwner).acceptOwnership())
      .to.emit(registry, "OwnershipTransferred")
      .withArgs(owner.address, finalOwner.address)
      .and.to.emit(registry, "GoalOSOwnershipRolesMigrated")
      .withArgs(owner.address, finalOwner.address);

    expect(await registry.owner()).to.equal(finalOwner.address);
    for (const role of await roles(registry)) {
      expect(await registry.hasRole(role, finalOwner.address)).to.equal(true);
      expect(await registry.hasRole(role, owner.address)).to.equal(false);
    }
    expect(await registry.hasRole(OPERATOR_ROLE, delegated.address)).to.equal(true);

    await expect(registry.connect(owner).pause()).to.be.revertedWith("GOALOS_NOT_PAUSER");
    await registry.connect(finalOwner).pause();
    expect(await registry.paused()).to.equal(true);
    await registry.connect(finalOwner).unpause();
    await registry.connect(finalOwner).transferOwnership(stranger.address);
    await ethers.provider.send("evm_increaseTime", [24 * 60 * 60]);
    await ethers.provider.send("evm_mine", []);
    await registry.connect(stranger).acceptOwnership();
    expect(await registry.owner()).to.equal(stranger.address);
  });

  it("exposes ownership helper inventory consistently", async function () {
    const [owner] = await ethers.getSigners();
    const Registry = await ethers.getContractFactory("ProofCardRegistry", owner);
    const registry = await Registry.deploy(owner.address);
    await registry.waitForDeployment();
    expect(await registry.managedOwnershipRoleCount()).to.equal(7n);
    await expect(registry.managedOwnershipRoleAt(7)).to.be.revertedWith("GOALOS_ROLE_INDEX");
  });
});
