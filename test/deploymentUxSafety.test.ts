import { expect } from "chai";
import fs from "fs";
import { AGIALPHA_MAINNET_TOKEN, assertAgialphaMainnetToken, assertNoMockTokenOnMainnet, getExpectedChainId, getRequiredPrivateKey, getRequiredRpcUrl } from "../scripts/config/networkConfig";
import { assertExpectedChainId } from "../scripts/deployment/lib/networkGuards";
import { assertMainnetOperatorEnv, assertRealMainnetManifest, MAINNET_ALLOW_VALUE, MAINNET_CONFIRMATION_PHRASE } from "../scripts/deployment/lib/mainnetGuards";
import { redactObject, redactString } from "../scripts/deployment/lib/redact";

const CLAIM_BOUNDARY = "This evidence reports deployment mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment.";
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



  it("blocks wrong Sepolia and Mainnet chain IDs before broadcast", async function () {
    let sepoliaError = "";
    try { await assertExpectedChainId("ethereumSepolia", { getNetwork: async () => ({ chainId: 1 }) }); } catch (error: any) { sepoliaError = error.message; }
    expect(sepoliaError).to.include("expected chainId 11155111");
    let mainnetError = "";
    try { await assertExpectedChainId("ethereumMainnet", { getNetwork: async () => ({ chainId: 11155111 }) }); } catch (error: any) { mainnetError = error.message; }
    expect(mainnetError).to.include("expected chainId 1");
  });

  it("requires exact local Mainnet operator gate values", function () {
    const env = { ...process.env, CI: "", GITHUB_ACTIONS: "", MAINNET_TARGET: "ethereum", AGIALPHA_TOKEN_ADDRESS: AGIALPHA_MAINNET_TOKEN, MAINNET_DEPLOYMENT_CONFIRMATION: MAINNET_CONFIRMATION_PHRASE, ALLOW_MAINNET_DEPLOYMENT: MAINNET_ALLOW_VALUE };
    expect(() => assertMainnetOperatorEnv(env)).not.to.throw();
    expect(() => assertMainnetOperatorEnv({ ...env, CI: "true" })).to.throw("forbidden in CI");
    expect(() => assertMainnetOperatorEnv({ ...env, GITHUB_ACTIONS: "true" })).to.throw("forbidden in CI");
    expect(() => assertMainnetOperatorEnv({ ...env, MOCK_AGIALPHA_ADDRESS: "0x0000000000000000000000000000000000000001" })).to.throw("MockAGIALPHA");
    expect(() => assertMainnetOperatorEnv({ ...env, DEPLOY_NEW_AGIALPHA_TOKEN: "true" })).to.throw("forbidden");
    expect(() => assertMainnetOperatorEnv({ ...env, MAINNET_DEPLOYMENT_CONFIRMATION: "NO" })).to.throw("Typed confirmation");
    expect(() => assertMainnetOperatorEnv({ ...env, ALLOW_MAINNET_DEPLOYMENT: "NO" })).to.throw("ALLOW_MAINNET_DEPLOYMENT");
  });

  it("rejects template or empty Mainnet manifests before verification can pass", function () {
    expect(() => assertRealMainnetManifest({ status: "TEMPLATE_NO_DEPLOYMENT", chainId: 1, contracts: {}, transactions: [] })).to.throw("template/no-deployment");
    expect(() => assertRealMainnetManifest({ chainId: 1, agialphaToken: AGIALPHA_MAINNET_TOKEN, contracts: {}, transactions: [] })).to.throw("no deployed contracts");
    expect(() => assertRealMainnetManifest({ chainId: 1, agialphaToken: AGIALPHA_MAINNET_TOKEN, contracts: { A: "0x0000000000000000000000000000000000000001" }, transactions: [] })).to.throw("no transaction hashes");
  });

  it("redacts sensitive output values", function () {
    expect(redactString("https://example.com/super-secret-rpc")).to.equal("[REDACTED]");
    expect(redactString("0x" + "a".repeat(64))).to.equal("[REDACTED]");
    expect(redactObject({ PRIVATE_KEY: "0x" + "b".repeat(64), normal: "ok" })).to.deep.equal({ PRIVATE_KEY: "[REDACTED]", normal: "ok" });
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
    const commandCenter = fs.readFileSync("scripts/deployment/goalos-deploy-command-center.ts", "utf8");
    expect(commandCenter).to.include("Mainnet evidence blocked: no real chainId=1 deployment manifest exists");
    expect(commandCenter).to.include("Mainnet deployed: ${main?\"NO unless this report was generated from a real chainId=1 manifest with transactions\":\"N/A\"}");
  });

  it("evidence and docs contain the deployment claim boundary", function () {
    expect(fs.readFileSync("scripts/deployment/goalos-deploy-command-center.ts", "utf8")).to.include(CLAIM_BOUNDARY);
    expect(fs.readFileSync("docs/DEPLOYMENT_START_HERE.md", "utf8")).to.include(CLAIM_BOUNDARY);
  });



  it("documents required Sepolia deployment role addresses", function () {
    const text = fs.readFileSync(".env.sepolia.example", "utf8");
    for (const name of ["FOUNDER_ADDRESS", "TREASURY_ADDRESS", "COMMERCIALIZATION_PERFORMANCE_ADMIN", "PROOF_REWARDS_ADMIN", "LIQUIDITY_ADMIN", "SECURITY_ADMIN", "COMMUNITY_ADMIN"]) {
      expect(text).to.include(`${name}=`);
    }
  });

  it("loads local env files when Hardhat passes --network on the CLI", function () {
    const loader = fs.readFileSync("scripts/config/loadEnv.ts", "utf8");
    expect(loader).to.include('process.argv.indexOf("--network")');
    expect(fs.readFileSync("hardhat.config.ts", "utf8")).to.include("loadDeploymentEnv();");
  });

  it("records constructor args for TokenReserveVault manifest aliases", function () {
    const source = fs.readFileSync("scripts/deploy-core.ts", "utf8");
    for (const alias of ["ProofRewardsVault", "LiquidityVault", "SecurityVault", "CommunityVault"]) {
      expect(source).to.include(`constructorArgs.${alias}`);
    }
  });

  it("verification layer treats already-verified contracts as success", function () {
    const verifier = fs.readFileSync("scripts/deployment/verify-deployment-friendly.ts", "utf8");
    expect(verifier).to.include("already verified|already been verified");
    expect(verifier).to.include("ALREADY_VERIFIED");
    expect(verifier).to.include("manifest has no contracts");
    expect(verifier).to.include("constructorArgs are redacted");
    expect(verifier).to.include("Constructor args for ${name} are missing from manifest");
  });

  it("committed examples and docs do not contain obvious secret values", function () {
    for (const file of [".env.sepolia.example", ".env.mainnet.example", "docs/DEPLOYMENT_START_HERE.md"]) {
      const text = fs.readFileSync(file, "utf8");
      expect(text).not.to.match(/0x[0-9a-fA-F]{64}/);
      expect(text).not.to.match(/https:\/\/[^\s]*(alchemy|infura)[^\s]*[A-Za-z0-9_-]{20,}/i);
    }
  });
});
