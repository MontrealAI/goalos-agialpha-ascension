import fs from "fs";
import { execFileSync } from "child_process";
import { loadDeploymentEnv } from "../config/loadEnv";
const ALREADY = /already verified|already been verified/i;
function arg(n:string){ const i=process.argv.indexOf(n); return i>=0?process.argv[i+1]:undefined; }
async function main(){
 const network=arg("--network") || (process.argv.includes("--mainnet")?"ethereumMainnet":"ethereumSepolia"); loadDeploymentEnv(network);
 if(!process.env.ETHERSCAN_API_KEY) throw new Error("ETHERSCAN_API_KEY is missing. Set ETHERSCAN_API_KEY before running verification.");
 const manifestPath=network.includes("Mainnet")?"deployments/ethereum-mainnet.agialpha.latest.json":"deployments/ethereum-sepolia.agialpha.latest.json";
 if(!fs.existsSync(manifestPath)) throw new Error(`Missing deployment manifest: ${manifestPath}`);
 const m=JSON.parse(fs.readFileSync(manifestPath,"utf8"));
 const results:any[]=[];
 for(const [name,address] of Object.entries(m.contracts||{})){
   if(name==="AGIALPHA") { results.push({name,address,status:"SKIPPED_EXTERNAL_TOKEN"}); continue; }
   const args=(m.constructorArgs && m.constructorArgs[name]) || [];
   const argsFile=`.verification-${network}-${name}.json`; fs.writeFileSync(argsFile, JSON.stringify(args));
   try{ execFileSync("npx",["hardhat","verify","--network",network,String(address),"--constructor-args",argsFile],{stdio:"pipe"}); results.push({name,address,status:"VERIFIED"}); }
   catch(e:any){ const out=String(e.stdout||"")+String(e.stderr||""); if(ALREADY.test(out)) results.push({name,address,status:"ALREADY_VERIFIED"}); else results.push({name,address,status:"FAILED",hint:`Manual command: npx hardhat verify --network ${network} ${address} --constructor-args ${argsFile}`,error:out.slice(0,800)}); }
 }
 const report={network,manifestPath,generatedAt:new Date().toISOString(),results};
 const out=network.includes("Mainnet")?"qa/mainnet-verification-report.json":"qa/sepolia-verification-report.json"; fs.mkdirSync("qa",{recursive:true}); fs.writeFileSync(out,JSON.stringify(report,null,2)+"\n");
 if(results.some(r=>r.status==="FAILED")) throw new Error(`Verification completed with failures. See ${out}.`);
 console.log(`Verification passed/already-verified. Report: ${out}`);
}
main().catch(e=>{console.error(e.message||e);process.exitCode=1});
