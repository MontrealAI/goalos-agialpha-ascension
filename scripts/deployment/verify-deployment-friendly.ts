import fs from "fs";
import { execFileSync } from "child_process";
import { loadDeploymentEnv } from "../config/loadEnv";
import { assertRealMainnetManifest } from "./lib/mainnetGuards";

const ALREADY = /already verified|already been verified/i;
function arg(n:string){ const i=process.argv.indexOf(n); return i>=0?process.argv[i+1]:undefined; }
function isMainnetNetwork(network: string) { return network === "ethereumMainnet" || network === "mainnet" || network.toLowerCase().includes("mainnet"); }
function realAddress(value: unknown): value is string { return typeof value === "string" && /^0x[0-9a-fA-F]{40}$/.test(value); }
function assertVerifiableManifest(network: string, manifest: any) {
  const contracts = manifest.contracts || {};
  if (!contracts || Object.keys(contracts).length === 0) throw new Error("Verification blocked: deployment manifest has no contracts. A template or empty manifest cannot be verified.");
  if (!Array.isArray(manifest.transactions) || manifest.transactions.length === 0) throw new Error("Verification blocked: deployment manifest has no transaction hashes. A no-broadcast/template manifest cannot be verified.");
  if (isMainnetNetwork(network)) {
    assertRealMainnetManifest(manifest);
    if (manifest.constructorArgsRedacted === true) throw new Error("Mainnet verification blocked: manifest constructorArgs are redacted. Run verification locally with an unredacted private constructor-args source or regenerate a private verification args file; this script will not submit redacted args.");
  }
}
async function main(){
 const network=arg("--network") || (process.argv.includes("--mainnet")?"ethereumMainnet":"ethereumSepolia"); loadDeploymentEnv(network);
 if(!process.env.ETHERSCAN_API_KEY) throw new Error("ETHERSCAN_API_KEY is missing. Set ETHERSCAN_API_KEY before running verification.");
 const manifestPath=isMainnetNetwork(network)?"deployments/ethereum-mainnet.agialpha.latest.json":"deployments/ethereum-sepolia.agialpha.latest.json";
 if(!fs.existsSync(manifestPath)) throw new Error(`Missing deployment manifest: ${manifestPath}`);
 const m=JSON.parse(fs.readFileSync(manifestPath,"utf8"));
 assertVerifiableManifest(network, m);
 const results:any[]=[];
 for(const [name,address] of Object.entries(m.contracts||{})){
   if(name==="AGIALPHA") { results.push({name,address,status:"SKIPPED_EXTERNAL_TOKEN"}); continue; }
   if(!realAddress(address)) { results.push({name,address,status:"FAILED",hint:"Manifest address is not a real 20-byte contract address."}); continue; }
   if(!m.constructorArgs || !(name in m.constructorArgs)) { results.push({name,address,status:"FAILED",hint:`Constructor args for ${name} are missing from manifest; rerun deployment with the current manifest writer or provide a private args file.`}); continue; }
   const args=m.constructorArgs[name];
   if(!Array.isArray(args)) { results.push({name,address,status:"FAILED",hint:"Constructor args are unavailable or redacted; provide a private unredacted args file for manual verification."}); continue; }
   const argsFile=`.verification-${network}-${name}.json`; fs.writeFileSync(argsFile, JSON.stringify(args));
   try{ execFileSync("npx",["hardhat","verify","--network",network,String(address),"--constructor-args",argsFile],{stdio:"pipe"}); results.push({name,address,status:"VERIFIED"}); }
   catch(e:any){ const out=String(e.stdout||"")+String(e.stderr||""); if(ALREADY.test(out)) results.push({name,address,status:"ALREADY_VERIFIED"}); else results.push({name,address,status:"FAILED",hint:`Manual command: npx hardhat verify --network ${network} ${address} --constructor-args ${argsFile}`,error:out.slice(0,800)}); }
 }
 const report={network,manifestPath,generatedAt:new Date().toISOString(),results};
 const out=isMainnetNetwork(network)?"qa/mainnet-verification-report.json":"qa/sepolia-verification-report.json"; fs.mkdirSync("qa",{recursive:true}); fs.writeFileSync(out,JSON.stringify(report,null,2)+"\n");
 if(results.length === 0 || results.some(r=>r.status==="FAILED")) throw new Error(`Verification did not complete successfully. See ${out}.`);
 console.log(`Verification passed/already-verified. Report: ${out}`);
}
main().catch(e=>{console.error(e.message||e);process.exitCode=1});
