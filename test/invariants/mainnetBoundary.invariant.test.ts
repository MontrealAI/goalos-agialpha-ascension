import { expect } from "chai";
import { ethers } from "hardhat";
import fs from "fs";

const AGIALPHA_MAINNET_TOKEN = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const CONFIRM_PHRASE = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET";

describe("mainnet boundary invariants", function () {
  it("keeps canonical Ethereum Mainnet token and chain guards in the gated deployment script", async function () {
    const source = fs.readFileSync("scripts/deploy-ethereum-mainnet-gated.ts", "utf8");
    const networkConfig = fs.readFileSync("scripts/config/networkConfig.ts", "utf8");
    expect(source + networkConfig).to.include(AGIALPHA_MAINNET_TOKEN);
    expect(source).to.include("chainId) !== 1");
    expect(source).to.include("MAINNET_TARGET");
    expect(source).to.include("MOCK_AGIALPHA_ADDRESS");
    expect(source).to.include("DEPLOY_NEW_AGIALPHA_TOKEN");
    expect(source).to.include(CONFIRM_PHRASE);
    expect(source).to.include("GITHUB_ACTIONS");
    expect(source).to.include("CI");
  });

  it("requires every core launch gate before allCoreGatesPassed can become true", async function () {
    const [admin, outsider] = await ethers.getSigners();
    const Harness = await ethers.getContractFactory("LaunchGateInvariantHarness");
    const gates = await Harness.deploy(admin.address);
    await gates.waitForDeployment();

    const requiredGateIds: string[] = await gates.requiredCoreGateIds();
    expect(requiredGateIds).to.have.length(10);
    expect(requiredGateIds).to.include(await gates.ETHEREUM_SEPOLIA_REHEARSAL());
    expect(requiredGateIds).to.include(await gates.AUTOMATED_SECURITY_TOOLCHAIN());
    expect(requiredGateIds).to.include(await gates.INTERNAL_SECURITY_REVIEW());
    expect(requiredGateIds).not.to.include(ethers.keccak256(ethers.toUtf8Bytes("BASE_SEPOLIA_REHEARSAL")));
    expect(requiredGateIds).not.to.include(ethers.keccak256(ethers.toUtf8Bytes("EXTERNAL_AUDIT_CLOSURE")));

    const evidence = ethers.keccak256(ethers.toUtf8Bytes("public-safe-evidence-commitment"));
    await expect(gates.connect(outsider).setGate(requiredGateIds[0], true, evidence, "ipfs://evidence")).to.be.reverted;
    await expect(gates.setGate(requiredGateIds[0], true, ethers.ZeroHash, "ipfs://evidence")).to.be.revertedWith("GATE_ZERO_EVIDENCE");

    for (let i = 0; i < requiredGateIds.length - 1; i += 1) {
      await gates.setGate(requiredGateIds[i], true, evidence, "ipfs://evidence");
      expect(await gates.allCoreGatesPassed()).to.equal(false);
    }

    await gates.setGate(requiredGateIds[requiredGateIds.length - 1], true, evidence, "ipfs://evidence");
    expect(await gates.allCoreGatesPassed()).to.equal(true);
  });
});
