import { expect } from "chai";
import { ethers } from "hardhat";

async function deployAEP() {
  const [deployer, treasury, sponsor, worker] = await ethers.getSigners();
  const MockAGIALPHA = await ethers.getContractFactory("MockAGIALPHA");
  const token = await MockAGIALPHA.deploy(deployer.address);
  await token.waitForDeployment();
  await token.transfer(sponsor.address, ethers.parseEther("10000"));

  const GoalOSCommit = await ethers.getContractFactory("AEPGoalOSCommitRegistry");
  const commits = await GoalOSCommit.deploy(deployer.address, await token.getAddress(), treasury.address);
  const Runs = await ethers.getContractFactory("AEPRunCommitmentRegistry");
  const runs = await Runs.deploy(deployer.address);
  const Proofs = await ethers.getContractFactory("AEPProofLedger");
  const proofs = await Proofs.deploy(deployer.address);
  const Evals = await ethers.getContractFactory("AEPEvalRegistry");
  const evals = await Evals.deploy(deployer.address);
  const Att = await ethers.getContractFactory("AEPAttestationRegistry");
  const attestations = await Att.deploy(deployer.address);
  const Sel = await ethers.getContractFactory("AEPSelectionGate");
  const selection = await Sel.deploy(deployer.address);
  const Rollouts = await ethers.getContractFactory("AEPRolloutRouter");
  const rollouts = await Rollouts.deploy(deployer.address);
  const Rollbacks = await ethers.getContractFactory("AEPRollbackRegistry");
  const rollbacks = await Rollbacks.deploy(deployer.address);
  const Dockets = await ethers.getContractFactory("AEPEvidenceDocketRegistry");
  const dockets = await Dockets.deploy(deployer.address);
  const Bundles = await ethers.getContractFactory("AEPProofBundleRegistry");
  const bundles = await Bundles.deploy(deployer.address);
  const AWU = await ethers.getContractFactory("AlphaWorkUnitLedger");
  const awu = await AWU.deploy(deployer.address);
  const Epochs = await ethers.getContractFactory("MandateEpochRegistry");
  const epochs = await Epochs.deploy(deployer.address, await token.getAddress(), treasury.address);
  return { deployer, treasury, sponsor, worker, token, commits, runs, proofs, evals, attestations, selection, rollouts, rollbacks, dockets, bundles, awu, epochs };
}

describe("AEP-001 / AGIALPHA Ascension proof-of-evolution spine", function () {
  it("runs Aim -> Act -> Prove -> Evolve on-chain commitments", async function () {
    const x = await deployAEP();
    await x.token.connect(x.sponsor).approve(await x.commits.getAddress(), ethers.parseEther("1000"));
    await x.commits.connect(x.sponsor).createCommit(
      ethers.keccak256(ethers.toUtf8Bytes("GoalOSCommit")),
      ethers.keccak256(ethers.toUtf8Bytes("success criteria")),
      ethers.keccak256(ethers.toUtf8Bytes("constraints")),
      ethers.keccak256(ethers.toUtf8Bytes("authority")),
      ethers.keccak256(ethers.toUtf8Bytes("data boundary")),
      ethers.keccak256(ethers.toUtf8Bytes("rollback obligations")),
      ethers.keccak256(ethers.toUtf8Bytes("claim boundary")),
      1,
      "ipfs://goalos-commit"
    );
    await x.runs.commitRun(1, ethers.keccak256(ethers.toUtf8Bytes("run commitment")), ethers.ZeroHash, ethers.ZeroHash, ethers.ZeroHash, ethers.ZeroHash, ethers.ZeroHash, ethers.ZeroHash, 1000000, 3600, "ipfs://run");
    await x.proofs.appendProofRoot(1, ethers.keccak256(ethers.toUtf8Bytes("proof")), ethers.keccak256(ethers.toUtf8Bytes("evidence-root")), ethers.keccak256(ethers.toUtf8Bytes("eval-root")), 100, 5, ethers.keccak256(ethers.toUtf8Bytes("signatures")), "ipfs://proof");
    await x.evals.registerEvalSchema(ethers.keccak256(ethers.toUtf8Bytes("refund-policy-eval")), "ipfs://eval-schema", 86400);
    await x.evals.recordEval(1, 1, ethers.keccak256(ethers.toUtf8Bytes("baseline")), ethers.keccak256(ethers.toUtf8Bytes("candidate")), 1, ethers.keccak256(ethers.toUtf8Bytes("pass")));
    const gateBitmap = await x.selection.GATE_PROOF_VALID() | await x.selection.GATE_EVAL_PASS() | await x.selection.GATE_RISK_OK() | await x.selection.GATE_ROLLBACK_READY() | await x.selection.GATE_SCOPE_AUTHORIZED();
    await x.selection.issueSelectionCertificate(1, ethers.keccak256(ethers.toUtf8Bytes("support-workflow")), ethers.keccak256(ethers.toUtf8Bytes("v1.1")), 2, ethers.keccak256(ethers.toUtf8Bytes("season-001")), ethers.ZeroHash, ethers.keccak256(ethers.toUtf8Bytes("v1.0")), 0, gateBitmap, "ipfs://selection");
    await x.rollouts.recordRollout(1, 1000, ethers.keccak256(ethers.toUtf8Bytes("pilot")), ethers.keccak256(ethers.toUtf8Bytes("monitoring")), ethers.keccak256(ethers.toUtf8Bytes("safety")), "ipfs://rollout");
    await x.dockets.registerEvidenceDocket(ethers.keccak256(ethers.toUtf8Bytes("docket")), ethers.keccak256(ethers.toUtf8Bytes("claims")), ethers.keccak256(ethers.toUtf8Bytes("public-boundary")), ethers.keccak256(ethers.toUtf8Bytes("private-appendix")), ethers.keccak256(ethers.toUtf8Bytes("cost-ledger")), ethers.keccak256(ethers.toUtf8Bytes("risk-ledger")), "ipfs://docket");
    await x.bundles.registerProofBundle(1, 1, ethers.keccak256(ethers.toUtf8Bytes("bundle")), ethers.keccak256(ethers.toUtf8Bytes("replay")), ethers.ZeroHash, ethers.ZeroHash, ethers.keccak256(ethers.toUtf8Bytes("settlement")), 1000, "ipfs://bundle");
    await x.awu.recordAlphaWorkUnits(x.worker.address, 1, 1000, ethers.keccak256(ethers.toUtf8Bytes("metrology")), 9000, 9000, 9000, ethers.keccak256(ethers.toUtf8Bytes("policy")));
    expect((await x.proofs.proofs(1)).runId).to.equal(1);
    expect((await x.awu.totalAlphaWUByWorker(x.worker.address))).to.equal(1000);
  });
});
