import fs from "fs";
import crypto from "crypto";
import { redactString } from "../deployment/lib/redact";
import { assertRealMainnetManifest } from "../deployment/lib/mainnetGuards";
import { constructorArgsFor, writeConstructorArgsFile } from "./lib/constructorArgs";
import { isAddressLike } from "./lib/bytecodeChecks";
import { classifyVerificationOutput, verificationSucceeded } from "./lib/verificationStatus";
import { verifyWithEtherscan } from "./lib/verifyWithEtherscan";
import { sourcifyRequested } from "./lib/verifyWithSourcify";
import { writeVerificationReport } from "./lib/reportVerification";

const CLAIM_BOUNDARY = "This evidence reports deployment and verification mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment.";
function arg(name:string, fallback?:string){ const i=process.argv.indexOf(name); return i>=0 ? process.argv[i+1] : fallback; }
function has(name:string){ return process.argv.includes(name); }
function isMainnet(n:string){ return /mainnet/i.test(n); }
function manifestPath(network:string){ return arg("--manifest") || (isMainnet(network)?"deployments/ethereum-mainnet.agialpha.latest.json":"deployments/ethereum-sepolia.agialpha.latest.json"); }
function sha(p:string){ return crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex"); }
function contractEntries(m:any): any[] {
  if (Array.isArray(m.manifestContracts)) return m.manifestContracts;
  if (Array.isArray(m.contractsArray)) return m.contractsArray;
  if (Array.isArray(m.contracts)) return m.contracts;
  return Object.entries(m.contracts || {}).map(([name,address]) => ({ name, address, fullyQualifiedName: m.fullyQualifiedNames?.[name as string], constructorArgs: m.constructorArgs?.[name as string] }));
}
function fqcnFor(c:any){ return c.fullyQualifiedName || c.fqcn || c.contract || c.name; }
function writeManual(network:string, failed:any[]) {
  const dir = isMainnet(network) ? "verification-args/mainnet" : "verification-args/sepolia";
  fs.mkdirSync(dir,{recursive:true}); fs.mkdirSync("qa",{recursive:true});
  const lines = [`# Manual verification commands (${network})`, "", "These commands are generated only for contracts that automatic verification could not complete. Review before running. Do not add secrets.", ""];
  for (const r of failed) lines.push(`npx hardhat verify --network ${network} --contract ${r.fqcn || r.name} ${r.address} ${r.constructorArgsFile ? `--constructor-args ${r.constructorArgsFile}` : ""}`.trim());
  fs.writeFileSync(isMainnet(network)?"qa/manual-verification-commands.mainnet.md":"qa/manual-verification-commands.sepolia.md", lines.join("\n")+"\n");
}
async function main(){
  const network = arg("--network", isMainnet(process.argv.join(" "))?"ethereumMainnet":"ethereumSepolia")!;
  const expected = Number(arg("--chain-id", isMainnet(network)?"1":"11155111"));
  const p = manifestPath(network);
  if (!fs.existsSync(p)) throw new Error(`Verification doctor blocked: missing manifest ${p}. Run a deployment first or pass --manifest <path>.`);
  const raw = fs.readFileSync(p,"utf8");
  if (/"[^"]*(SECRET|PRIVATE|MNEMONIC|BEARER|RPC|PRIVATE_KEY)[^"]*"\s*:\s*"[^"]+"/i.test(raw)) throw new Error(`Secret-like value found in manifest ${p}; redact/regenerate before verification.`);
  const m = JSON.parse(raw);
  if (Number(m.chainId) !== expected) throw new Error(`Wrong chainId for verification: manifest has ${m.chainId}, expected ${expected}.`);
  if (isMainnet(network)) assertRealMainnetManifest(m);
  const contracts = contractEntries(m);
  if (!contracts.length) throw new Error("Verification blocked: manifest contains no deployed contracts.");
  const retryCount = Number(arg("--retry-count", process.env.VERIFY_RETRY_COUNT || "1"));
  const retryDelayMs = Number(arg("--retry-delay-ms", process.env.VERIFY_RETRY_DELAY_MS || "0"));
  const results:any[]=[];
  const argsDir = isMainnet(network)?"verification-args/mainnet":"verification-args/sepolia"; fs.mkdirSync(argsDir,{recursive:true});
  for (const c of contracts) {
    const address = c.address; const name = c.name || c.contractName || "UnknownContract"; const fqcn = fqcnFor(c); const args = constructorArgsFor(c,m);
    let constructorArgsFile: string | undefined;
    if (Array.isArray(args)) { constructorArgsFile = writeConstructorArgsFile(`${argsDir}/${name}.args.ts`, args); }
    const base = { name, fqcn, address, bytecodePresent: c.bytecodePresent ?? "unchecked", constructorArgsPresent: Array.isArray(args), alreadyVerified:false, verificationUrl:c.verificationUrl||null };
    if (c.verification?.status === "skipped") { results.push({...base, etherscanStatus:"skipped", sourcifyStatus:"not_run", error:c.verification?.error || "Verification skipped by manifest."}); continue; }
    if (c.constructorArgsRedacted === true || (isMainnet(network) && m.constructorArgsRedacted === true)) { results.push({...base, etherscanStatus:"failed", sourcifyStatus:"not_run", error:"Constructor args are redacted in the public Mainnet manifest; provide a private unredacted constructor-args source before automatic verification."}); continue; }
    if (!isAddressLike(address)) { results.push({...base, etherscanStatus:"failed", sourcifyStatus:"not_run", error:"Invalid or missing deployed contract address"}); continue; }
    if (!Array.isArray(args)) { results.push({...base, etherscanStatus:"failed", sourcifyStatus:"not_run", error:"Constructor args missing; manual verification args file required"}); continue; }
    let ok=false, already=false, error="";
    for (let attempt=0; attempt<retryCount && !ok; attempt++) {
      try { const out = verifyWithEtherscan(network, fqcn, String(address), constructorArgsFile!); const status = classifyVerificationOutput(out || "successfully verified"); ok = verificationSucceeded(status) || status === "verified"; already = status === "already_verified"; }
      catch(e:any){ const out=redactString(String(e.stdout||"")+String(e.stderr||"")); const status = classifyVerificationOutput(out); if(status === "already_verified"){ok=true; already=true;} else { error=out.slice(0,1200); if(retryDelayMs) await new Promise(r=>setTimeout(r,retryDelayMs)); } }
    }
    results.push({...base, etherscanStatus: ok ? "verified" : "failed", sourcifyStatus: sourcifyRequested(arg("--provider", "both")!) ? "requested" : "not_run", alreadyVerified: already, verificationProvider:"hardhat-etherscan", verificationTimestamp:new Date().toISOString(), error: ok?null:error, constructorArgsFile});
  }
  const verified = results.filter(r=>r.etherscanStatus==="verified").length;
  const alreadyVerified = results.filter(r=>r.alreadyVerified).length;
  const skipped = results.filter(r=>r.etherscanStatus==="skipped").length;
  const failed = results.filter(r=>r.etherscanStatus!=="verified" && r.etherscanStatus!=="skipped").length;
  const evidence = { network, chainId: expected, manifestPath:p, manifestHash:sha(p), verifiedAt:new Date().toISOString(), verifierToolVersions:{ hardhat:"2.28.6", solidity:"0.8.35" }, etherscanApiConfigured:Boolean(process.env.ETHERSCAN_API_KEY), sourcifyEnabled:(process.env.SOURCIFY_ENABLED||"true")!=="false", contracts:results, summary:{ totalContracts:results.length, verified, alreadyVerified, skipped, failed, partial:failed>0&&verified>0, complete:failed===0 }, claimBoundary:CLAIM_BOUNDARY };
  fs.mkdirSync("qa",{recursive:true}); fs.mkdirSync("docs",{recursive:true});
  const out = isMainnet(network)?"qa/mainnet-contract-verification-evidence.json":"qa/sepolia-contract-verification-evidence.json";
  const report = isMainnet(network)?"docs/ETHEREUM_MAINNET_CONTRACT_VERIFICATION_REPORT.md":"docs/SEPOLIA_CONTRACT_VERIFICATION_REPORT.md";
  fs.writeFileSync(out, JSON.stringify(evidence,null,2)+"\n");
  writeVerificationReport(report, `${isMainnet(network)?"Ethereum Mainnet":"Sepolia"} Contract Verification Report`, `Verified means the block explorer matched deployed bytecode to source/metadata. Already verified is counted as success. Bytecode present but unverified means source verification is missing. Missing bytecode means the address is wrong or deployment failed. Constructor args missing means automatic verification may fail. Partial verification is not production verification.\n\nSummary: ${verified}/${results.length} verified. Failed: ${failed}.`, CLAIM_BOUNDARY);
  writeManual(network, results.filter(r=>r.etherscanStatus!=="verified" && r.etherscanStatus!=="skipped"));
  console.log(JSON.stringify({ readyToVerify: failed===0?"YES":"NO", evidence:out, report, failed }, null, 2));
  if (failed && !has("--allow-partial")) process.exitCode = 1;
}
main().catch(e=>{ console.error(redactString(e.message||String(e))); process.exitCode=1; });
