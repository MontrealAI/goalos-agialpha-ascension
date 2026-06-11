import { ethers, network } from "hardhat";
import fs from "fs";
import { deployGoalOSAGIALPHAAscension } from "./deploy-core";

const MANIFEST = "deployments/ethereum-sepolia.agialpha.latest.json";
function h(label: string) { return ethers.keccak256(ethers.toUtf8Bytes(label)); }
function stringify(value: any) { return JSON.stringify(value, (_k, v) => typeof v === "bigint" ? v.toString() : v, 2); }
async function txrec(label: string, p: Promise<any>) { const tx=await p; const r=await tx.wait(); return { label, hash: tx.hash, blockNumber: r?.blockNumber, status: r?.status, gasUsed: r?.gasUsed?.toString() }; }
async function expectRevert(label: string, p: Promise<any>) { try { const tx=await p; await tx.wait(); return { label, passed:false, error:"unexpected success" }; } catch (e:any) { return { label, passed:true, error:String(e.shortMessage || e.message).slice(0,300) }; } }
async function futureDeadline(seconds=86400){ const b=await ethers.provider.getBlock('latest'); if(!b) throw new Error('no latest block'); return b.timestamp+seconds; }
function classifyRpcEndpoint(url: string | undefined) {
  if (!url) return "unset";
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.toLowerCase();
    if (["127.0.0.1", "localhost", "0.0.0.0", "::1"].includes(host)) return "local";
    return "remote";
  } catch {
    return "unknown";
  }
}
function isLocalDevClient(clientVersion: string) {
  return /hardhat|anvil|ganache|ethereumjs|foundry/i.test(clientVersion);
}
async function clientVersion(provider: any = ethers.provider) {
  try {
    return String(await provider.send("web3_clientVersion", []));
  } catch {
    return "unavailable";
  }
}
async function verifyWithIndependentPublicSepoliaRpc(txs: any[]) {
  const verificationUrl = process.env.ETHEREUM_SEPOLIA_PUBLIC_VERIFICATION_RPC_URL || process.env.SEPOLIA_PUBLIC_VERIFICATION_RPC_URL || "";
  const verificationRpcEndpointClass = classifyRpcEndpoint(verificationUrl);
  if (verificationRpcEndpointClass !== "remote") {
    return { receiptsVerified: false, reason: "missing_remote_independent_verification_rpc", verificationRpcEndpointClass };
  }
  try {
    const verificationProvider = new ethers.JsonRpcProvider(verificationUrl);
    const verificationNetwork = await verificationProvider.getNetwork();
    const publicVerificationChainId = Number(verificationNetwork.chainId);
    const verificationClientVersion = await clientVersion(verificationProvider);
    if (publicVerificationChainId !== 11155111 || isLocalDevClient(verificationClientVersion)) {
      return { receiptsVerified: false, reason: "verification_rpc_not_public_sepolia", publicVerificationChainId, verificationRpcEndpointClass, verificationClientVersion };
    }
    const receipts = await Promise.all(txs.map((tx) => verificationProvider.getTransactionReceipt(tx.hash)));
    const receiptsVerified = receipts.every((receipt, index) => receipt && Number(receipt.status) === Number(txs[index].status) && Number(receipt.blockNumber) === Number(txs[index].blockNumber));
    return { receiptsVerified, reason: receiptsVerified ? "independent_public_sepolia_receipts_verified" : "transaction_receipts_missing_or_mismatched", publicVerificationChainId, verificationRpcEndpointClass, verificationClientVersion, verifiedTransactionCount: receipts.filter(Boolean).length, expectedTransactionCount: txs.length };
  } catch (e: any) {
    return { receiptsVerified: false, reason: "independent_verification_failed", verificationRpcEndpointClass, error: String(e.shortMessage || e.message).slice(0, 300) };
  }
}

async function main() {
  const net = await ethers.provider.getNetwork();
  const latestBlock = await ethers.provider.getBlockNumber();
  const rpcClientVersion = await clientVersion();
  const chainId = Number(net.chainId);
  if (chainId === 1) throw new Error("Refusing to rehearse on Ethereum mainnet");
  if (chainId !== 11155111) throw new Error(`Sepolia rehearsal requires chainId 11155111; got ${chainId}`);
  const [deployer, treasury, sponsor, builder, reviewer, outsider] = await ethers.getSigners();
  process.env.FOUNDER_ADDRESS ||= deployer.address;
  process.env.TREASURY_ADDRESS ||= treasury.address;
  process.env.COMMERCIALIZATION_PERFORMANCE_ADMIN ||= deployer.address;
  process.env.PROOF_REWARDS_ADMIN ||= deployer.address;
  process.env.LIQUIDITY_ADMIN ||= deployer.address;
  process.env.SECURITY_ADMIN ||= deployer.address;
  process.env.COMMUNITY_ADMIN ||= deployer.address;
  delete process.env.ALLOW_MAINNET_DEPLOYMENT;
  await deployGoalOSAGIALPHAAscension();
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
  const c = manifest.contracts;
  const agialpha = await ethers.getContractAt("MockAGIALPHA", c.AGIALPHA);
  const proofSeeds = await ethers.getContractAt("ProofSeedRegistry", c.ProofSeedRegistry);
  const jobRegistry = await ethers.getContractAt("JobRegistry", c.JobRegistry);
  const claimBond = await ethers.getContractAt("JobClaimBondManager", c.JobClaimBondManager);
  const proofSubs = await ethers.getContractAt("ProofSubmissionRegistry", c.ProofSubmissionRegistry);
  const reviewerBonds = await ethers.getContractAt("ReviewerBondRegistry", c.ReviewerBondRegistry);
  const proofCards = await ethers.getContractAt("ProofCardRegistry", c.ProofCardRegistry);
  const credentials = await ethers.getContractAt("ProofCredentialRegistry", c.ProofCredentialRegistry);
  const reputation = await ethers.getContractAt("ReputationRegistry", c.ReputationRegistry);
  const referrals = await ethers.getContractAt("ReferralRegistry", c.ReferralRegistry);
  const premium = await ethers.getContractAt("PremiumAccessRegistry", c.PremiumAccessRegistry);
  const launchGates = await ethers.getContractAt("LaunchGateRegistry", c.LaunchGateRegistry);
  const txs:any[]=[]; const negatives:any[]=[]; const observations:any = {};
  for (const acct of [sponsor, builder, reviewer]) txs.push(await txrec(`fund ${acct.address}`, agialpha.transfer(acct.address, ethers.parseEther("10000"))));
  txs.push(await txrec("sponsor approve proof seed fee", agialpha.connect(sponsor).approve(c.ProofSeedRegistry, ethers.parseEther("1000"))));
  txs.push(await txrec("create ProofSeed", proofSeeds.connect(sponsor).createProofSeed(h("sepolia proof seed"), "ipfs://sepolia/proof-seed", h("audit-rehearsal"))));
  txs.push(await txrec("mark ProofSeed reviewed", proofSeeds.markReviewed(1, h("seed reviewed"))));
  observations.seed = await proofSeeds.proofSeeds(1);
  txs.push(await txrec("sponsor approve job reward", agialpha.connect(sponsor).approve(c.JobRegistry, ethers.parseEther("1000"))));
  txs.push(await txrec("post Proof Job", jobRegistry.connect(sponsor).postJob("ipfs://sepolia/job", h("job metadata"), c.AGIALPHA, ethers.parseEther("100"), await futureDeadline())));
  txs.push(await txrec("builder approve claim bond", agialpha.connect(builder).approve(c.JobClaimBondManager, ethers.parseEther("1000"))));
  txs.push(await txrec("builder claim job", claimBond.connect(builder).claimJob(1)));
  observations.claimBondLocked = (await claimBond.claimBonds(1)).amount.toString();
  negatives.push(await expectRevert("unauthorized proof submission", proofSubs.connect(outsider).submitProof(1,"ipfs://bad",h("bad"),h("bad-card"))));
  negatives.push(await expectRevert("zero proof hash rejected", proofSubs.connect(builder).submitProof(1,"ipfs://bad",ethers.ZeroHash,h("bad-card"))));
  txs.push(await txrec("builder approve proof bond", agialpha.connect(builder).approve(c.ProofSubmissionRegistry, ethers.parseEther("1000"))));
  txs.push(await txrec("builder submit ProofBundle", proofSubs.connect(builder).submitProof(1,"ipfs://sepolia/proof",h("proof bundle"),h("proof card"))));
  negatives.push(await expectRevert("unauthorized reviewer validation", reviewerBonds.connect(outsider).reviewSubmission(1,true,h("bad-review"),"ipfs://bad",h("BAD"),false)));
  txs.push(await txrec("reviewer approve bond", agialpha.connect(reviewer).approve(c.ReviewerBondRegistry, ethers.parseEther("1000"))));
  txs.push(await txrec("reviewer bonds", reviewerBonds.connect(reviewer).bondAsReviewer("ipfs://sepolia/reviewer")));
  txs.push(await txrec("reviewer approves proof", reviewerBonds.connect(reviewer).reviewSubmission(1,true,h("approved"),"ipfs://sepolia/credential",h("GOALOS_ASCENSION_BUILDER"),false)));
  observations.credentialOwner = await credentials.ownerOf(1);
  observations.reputationScore = (await reputation.scoreOf(builder.address)).toString();
  observations.proofCard = await proofCards.proofCards(1);
  txs.push(await txrec("builder assigns referral", referrals.connect(builder).assignReferral(sponsor.address)));
  negatives.push(await expectRevert("referral overwrite rejected", referrals.connect(builder).assignReferral(reviewer.address)));
  txs.push(await txrec("set premium tier", premium.setAccessTier(h("REHEARSAL"), 1, 1, true)));
  observations.premiumAccess = await premium.canAccess(builder.address, h("REHEARSAL"));
  negatives.push(await expectRevert("credential issuance without operator proof fails", credentials.connect(outsider).issueCredential(outsider.address,1,h("x"),h("Y"),"ipfs://bad")));
  negatives.push(await expectRevert("launch gate unauthorized caller rejected", launchGates.connect(outsider).setGate(await launchGates.ETHEREUM_SEPOLIA_REHEARSAL(), true, h("fake"), "ipfs://bad")));
  // rejected proof path with second job
  txs.push(await txrec("post rejected-path job", jobRegistry.connect(sponsor).postJob("ipfs://sepolia/job-reject", h("job reject"), c.AGIALPHA, ethers.parseEther("10"), await futureDeadline())));
  txs.push(await txrec("builder claim rejected-path job", claimBond.connect(builder).claimJob(2)));
  txs.push(await txrec("builder submit rejected-path proof", proofSubs.connect(builder).submitProof(2,"ipfs://sepolia/proof-reject",h("proof reject"),h("card reject"))));
  txs.push(await txrec("reviewer rejects proof", reviewerBonds.connect(reviewer).reviewSubmission(2,false,h("rejected"),"",ethers.ZeroHash,false)));
  const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes(JSON.stringify({txs: txs.map(t=>t.hash), negatives, chainId, manifest: MANIFEST})));
  txs.push(await txrec("set ETHEREUM_SEPOLIA_REHEARSAL gate", launchGates.setGate(await launchGates.ETHEREUM_SEPOLIA_REHEARSAL(), true, evidenceHash, "evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json")));
  observations.allCoreGatesPassed = await launchGates.allCoreGatesPassed();
  const rpcEndpointClass = classifyRpcEndpoint(process.env.ETHEREUM_SEPOLIA_RPC_URL);
  const independentVerification = await verifyWithIndependentPublicSepoliaRpc(txs);
  const publicSepolia = network.name === "sepolia" && rpcEndpointClass === "remote" && latestBlock >= 1_000_000 && !isLocalDevClient(rpcClientVersion) && independentVerification.receiptsVerified === true;
  const rehearsal = { status:"COMPLETED", chainId, networkEvidence: { publicSepolia, marker: publicSepolia ? "PUBLIC_SEPOLIA_RPC" : "LOCAL_OR_UNVERIFIED_CHAINID_11155111", networkName: network.name, latestBlockNumber: latestBlock, rpcEndpointClass, clientVersion: rpcClientVersion, independentVerification }, deployer:deployer.address, sponsor:sponsor.address, builder:builder.address, reviewer:reviewer.address, outsider:outsider.address, manifest: MANIFEST, mockAGIALPHA: c.AGIALPHA, evidenceHash, transactions: txs, negativePaths: negatives, observations };
  manifest.sepoliaRehearsal = rehearsal;
  manifest.blockNumbers = Object.fromEntries(txs.map(t=>[t.label,t.blockNumber]));
  manifest.transactionHashes = Object.fromEntries(txs.map(t=>[t.label,t.hash]));
  manifest.roleAssignments = { operatorContracts: [c.JobClaimBondManager,c.ProofSubmissionRegistry,c.ReviewerBondRegistry], launchGateOperator: deployer.address };
  manifest.vaultAddresses = { CommercializationPerformanceVault:c.CommercializationPerformanceVault, ProofRewardsVault:c.ProofRewardsVault, LiquidityVault:c.LiquidityVault, SecurityVault:c.SecurityVault, CommunityVault:c.CommunityVault };
  fs.writeFileSync(MANIFEST, stringify(manifest));
  fs.mkdirSync("evidence/sepolia", { recursive: true });
  fs.writeFileSync("evidence/sepolia/SEPOLIA_REHEARSAL_RAW.latest.json", stringify(rehearsal));
  console.log(JSON.stringify({status:"SEPOLIA_REHEARSAL_COMPLETED", evidenceHash, manifest:MANIFEST}, null, 2));
}
main().catch((error)=>{ console.error(error); process.exitCode=1; });
