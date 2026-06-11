import { expect } from "chai";
import { ethers } from "hardhat";

describe("v4.3 Ethereum launch gate consistency", function () {
  it("uses Ethereum Sepolia and complete institutional gates", async function () {
    const [admin] = await ethers.getSigners();
    const LaunchGateRegistry = await ethers.getContractFactory("LaunchGateRegistry");
    const gates = await LaunchGateRegistry.deploy(admin.address);
    await gates.waitForDeployment();
    expect(await gates.ETHEREUM_SEPOLIA_REHEARSAL()).to.equal(ethers.keccak256(ethers.toUtf8Bytes("ETHEREUM_SEPOLIA_REHEARSAL")));
    expect(await gates.AGIALPHA_TOKEN_VERIFICATION()).to.equal(ethers.keccak256(ethers.toUtf8Bytes("AGIALPHA_TOKEN_VERIFICATION")));
    expect(await gates.EXTERNAL_AUDIT_CLOSURE()).to.equal(ethers.keccak256(ethers.toUtf8Bytes("EXTERNAL_AUDIT_CLOSURE")));
    expect(await gates.FOUNDER_APPROVAL()).to.equal(ethers.keccak256(ethers.toUtf8Bytes("FOUNDER_APPROVAL")));
    const evidence = ethers.keccak256(ethers.toUtf8Bytes("evidence"));
    const uri = "ipfs://evidence";
    const gateIds = [await gates.LEGAL_REVIEW(), await gates.TAX_REVIEW(), await gates.SECURITY_REVIEW(), await gates.PUBLIC_CLAIMS_REVIEW(), await gates.TREASURY_REVIEW(), await gates.AGIALPHA_TOKEN_VERIFICATION(), await gates.ETHEREUM_SEPOLIA_REHEARSAL(), await gates.EXTERNAL_AUDIT_CLOSURE(), await gates.FOUNDER_APPROVAL()];
    for (const gateId of gateIds) await gates.setGate(gateId, true, evidence, uri);
    expect(await gates.allCoreGatesPassed()).to.equal(true);
  });
});
