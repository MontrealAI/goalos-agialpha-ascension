import { expect } from "chai";
import fs from "fs";
import { AGIALPHA_MAINNET_TOKEN, assertAgialphaMainnetToken, assertNoMockTokenOnMainnet, getExpectedChainId, getRequiredPrivateKey, getRequiredRpcUrl } from "../scripts/config/networkConfig";

const CLAIM_BOUNDARY = "This evidence reports deployment mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, or production safety.";
const CONFIRM_PHRASE = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET";

describe("deployment UX safety layer", function () {
  const saved = { ...process.env };
  afterEach(() => { process.env = { ...saved }; });

  it("resolves Ethereum Sepolia and Ethereum Mainnet chain IDs", function () {
    expect(getExpectedChainId("ethereumSepolia")).to.equal(11155111);
    expect(getExpectedChainId("sepolia")).to.equal(11155111);
    expect(getExpectedChainId("ethereumMainnet")).to.equal(1);
    expect(getExpectedChainId("mainnet")).to.equal(1);
  });

  it("gives friendly missing RPC and private-key errors", function () {
    delete process.env.PRIVATE_SEPOLIA_RPC_URL;
    delete process.env.SEPOLIA_RPC_URL;
    delete process.env.ETHEREUM_SEPOLIA_RPC_URL;
    expect(() => getRequiredRpcUrl("ethereumSepolia")).to.throw("Missing private RPC URL");
    delete process.env.PRIVATE_SEPOLIA_DEPLOYER_PRIVATE_KEY;
    delete process.env.SEPOLIA_DEPLOYER_PRIVATE_KEY;
    delete process.env.PRIVATE_DEPLOYER_PRIVATE_KEY;
    delete process.env.DEPLOYER_PRIVATE_KEY;
    delete process.env.PRIVATE_KEY;
    expect(() => getRequiredPrivateKey("ethereumSepolia")).to.throw("Missing deployer private key");
  });

  it("blocks invalid private-key shape", function () {
    process.env.PRIVATE_SEPOLIA_DEPLOYER_PRIVATE_KEY = "not-a-key";
    expect(() => getRequiredPrivateKey("ethereumSepolia")).to.throw("Invalid private-key shape");
  });

  it("keeps mainnet gates local-only, canonical-token-only, and confirmation-gated", function () {
    const source = fs.readFileSync("scripts/deploy-ethereum-mainnet-gated.ts", "utf8");
    expect(source).to.include("GITHUB_ACTIONS");
    expect(source).to.include("CI");
    expect(source).to.include("MOCK_AGIALPHA_ADDRESS");
    expect(source).to.include("DEPLOY_NEW_AGIALPHA_TOKEN");
    expect(source).to.include(CONFIRM_PHRASE);
    expect(() => assertAgialphaMainnetToken(AGIALPHA_MAINNET_TOKEN)).not.to.throw();
    expect(() => assertNoMockTokenOnMainnet(1, "0x0000000000000000000000000000000000000001")).to.throw("MockAGIALPHA is forbidden");
  });

  it("does not let generated mainnet docs claim deployed YES without transaction evidence", function () {
    const commandCenter = fs.readFileSync("scripts/wizard/deploy-command-center.ts", "utf8");
    expect(commandCenter).to.include("Mainnet evidence blocked: no real chainId=1 deployment manifest exists");
    expect(commandCenter).to.include("Mainnet deployed: ${main?\"NO unless this report was generated from a real chainId=1 manifest with transactions\":\"N/A\"}");
  });

  it("evidence and docs contain the deployment claim boundary", function () {
    expect(fs.readFileSync("scripts/wizard/deploy-command-center.ts", "utf8")).to.include(CLAIM_BOUNDARY);
    expect(fs.readFileSync("docs/DEPLOYMENT_START_HERE.md", "utf8")).to.include(CLAIM_BOUNDARY);
  });

  it("verification layer treats already-verified contracts as success", function () {
    const verifier = fs.readFileSync("scripts/deployment/verify-deployment-friendly.ts", "utf8");
    expect(verifier).to.include("already verified|already been verified");
    expect(verifier).to.include("ALREADY_VERIFIED");
  });

  it("committed examples and docs do not contain obvious secret values", function () {
    for (const file of [".env.sepolia.example", ".env.mainnet.example", "docs/DEPLOYMENT_START_HERE.md"]) {
      const text = fs.readFileSync(file, "utf8");
      expect(text).not.to.match(/0x[0-9a-fA-F]{64}/);
      expect(text).not.to.match(/https:\/\/[^\s]*(alchemy|infura)[^\s]*[A-Za-z0-9_-]{20,}/i);
    }
  });
});
