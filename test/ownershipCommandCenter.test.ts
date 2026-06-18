import { expect } from "chai";
import { ethers } from "hardhat";

const MODULE = "../scripts/ownership/goalos-ownership-command-center";

describe("ownership command-center safety gates", function () {
  let hooks: any;
  let addrA: string;
  let addrB: string;

  before(async function () {
    process.env.GOALOS_OWNERSHIP_COMMAND_CENTER_TEST = "1";
    hooks = (await import(MODULE)).ownershipCommandCenterTestHooks;
    const [a, b] = await ethers.getSigners();
    addrA = a.address;
    addrB = b.address;
  });

  after(function () {
    delete process.env.GOALOS_OWNERSHIP_COMMAND_CENTER_TEST;
    delete process.env.CI;
    delete process.env.GITHUB_ACTIONS;
    delete process.env.OWNERSHIP_MAINNET_CONFIRMATION;
    delete process.env.OWNERSHIP_DISPOSABLE_OWNER_ADDRESS;
  });

  it("blocks Mainnet ownership operations in CI", function () {
    process.env.CI = "true";
    expect(() => hooks.forbidCiMainnet(1n)).to.throw("Mainnet ownership handoff is local-only");
    expect(() => hooks.forbidCiMainnet(11155111n)).not.to.throw();
    delete process.env.CI;
  });

  it("requires exact Mainnet typed confirmation", function () {
    const planHash = "0x" + "11".repeat(32);
    const expected = hooks.expectedMainnetConfirmation(addrA, planHash);
    process.env.OWNERSHIP_MAINNET_CONFIRMATION = expected.replace(addrA, addrB);
    expect(() => hooks.validateMainnetTypedConfirmation(1n, addrA, planHash, false)).to.throw("Missing exact OWNERSHIP_MAINNET_CONFIRMATION");
    process.env.OWNERSHIP_MAINNET_CONFIRMATION = expected;
    expect(() => hooks.validateMainnetTypedConfirmation(1n, addrA, planHash, false)).not.to.throw();
  });

  it("refuses to write public Mainnet evidence from a Hardhat fork", function () {
    expect(() => hooks.forbidForkedMainnetEvidence("ethereum-mainnet", true, "hardhat")).to.throw("Refusing to write Mainnet ownership PASSED evidence");
    expect(() => hooks.forbidForkedMainnetEvidence("ethereum-mainnet", true, "ethereumMainnet", "http://127.0.0.1:8545")).to.throw("local RPC URL");
    expect(() => hooks.forbidForkedMainnetEvidence("ethereum-mainnet", false, "hardhat")).not.to.throw();
    expect(() => hooks.forbidForkedMainnetEvidence("ethereum-sepolia", true, "hardhat")).not.to.throw();
    expect(hooks.isLocalRpcUrl("https://eth-mainnet.example.invalid")).to.equal(false);
  });

  it("rejects proof messages without exact chain binding", function () {
    const manifestHash = "0x" + "22".repeat(32);
    expect(() => hooks.proofMessageIncludesBindings(`GoalOS chainId: 1 finalOwner: ${addrA} manifest: ${manifestHash}`, 1n, addrA, manifestHash)).not.to.throw();
    expect(() => hooks.proofMessageIncludesBindings(`GoalOS nonce 1 finalOwner: ${addrA} manifest: ${manifestHash}`, 1n, addrA, manifestHash)).to.throw("missing exact chainId binding");
  });

  it("rejects empty manifests and transfer plans that do not match the manifest", function () {
    expect(() => hooks.requireManagedEntries({ contracts: { AGIALPHA: addrA } })).to.throw("No managed contracts found in manifest");
    const manifestEntries = [
      { name: "A", address: addrA },
      { name: "B", address: addrB },
    ];
    const completePlan = manifestEntries.map((entry) => ({ ...entry, currentOwner: addrA, action: "TRANSFER", gasEstimate: "1" }));
    expect(() => hooks.assertPlanCoversManifest(completePlan, manifestEntries)).not.to.throw();
    expect(() => hooks.assertPlanCoversManifest(completePlan.slice(0, 1), manifestEntries)).to.throw("missing manifest contract");
    expect(() => hooks.assertPlanCoversManifest([...completePlan, { name: "C", address: addrA, currentOwner: addrA, action: "TRANSFER", gasEstimate: "1" }], manifestEntries)).to.throw("non-manifest contract");
  });

  it("uses env or manifest deployer as the independent disposable-owner source for verification", function () {
    const fallback = addrB;
    expect(hooks.resolveDisposableOwnerWithoutPlan("ethereum-sepolia", { deployer: addrA }, fallback)).to.equal(addrA);
    process.env.OWNERSHIP_DISPOSABLE_OWNER_ADDRESS = addrB;
    expect(hooks.resolveDisposableOwnerWithoutPlan("ethereum-sepolia", { deployer: addrA }, fallback)).to.equal(addrB);
    delete process.env.OWNERSHIP_DISPOSABLE_OWNER_ADDRESS;
  });

  it("finds a matching journaled transfer before a replacement can be submitted", function () {
    const entry = { name: "A", address: addrA, currentOwner: addrA, action: "TRANSFER", gasEstimate: "1" };
    const journal = {
      transactions: [
        { name: "Other", address: addrA, hash: "0x" + "33".repeat(32) },
        { name: "A", address: addrA.toLowerCase(), hash: "0x" + "44".repeat(32) },
      ],
    };
    expect(hooks.findJournaledTransfer(journal, entry)?.hash).to.equal("0x" + "44".repeat(32));
  });
});
