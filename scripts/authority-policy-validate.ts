import fs from "fs"; import crypto from "crypto"; import { ethers } from "ethers";
const args=process.argv.slice(2); if(args.includes("--help")){console.log("Usage: ts-node scripts/authority-policy-validate.ts --policy <file> [--json]"); process.exit(0)}
const policyPath=args[args.indexOf("--policy")+1]; if(!policyPath) throw new Error("--policy required");
const p=JSON.parse(fs.readFileSync(policyPath,"utf8"));
const required=["chainId","governanceOwner","governanceOwnerKind","operationsAddress","treasuryAddress","founderAddress","vaultOwners"];
for(const k of required) if(p[k]===undefined) throw new Error(`missing ${k}`);
for(const [k,v] of Object.entries({governanceOwner:p.governanceOwner, operationsAddress:p.operationsAddress, treasuryAddress:p.treasuryAddress, founderAddress:p.founderAddress, ...p.vaultOwners})) if(!ethers.isAddress(String(v))||String(v)===ethers.ZeroAddress) throw new Error(`invalid address ${k}`);
if(p.governanceOwnerKind==="LEDGER_EOA" && p.allowSingleLedgerEOAGovernance!=="I_ACCEPT_SINGLE_KEY_AND_RECOVERY_RISK") throw new Error("LEDGER_EOA requires explicit acknowledgement");
if(p.disposableDeployer){ for(const [k,v] of Object.entries({governanceOwner:p.governanceOwner, operationsAddress:p.operationsAddress, treasuryAddress:p.treasuryAddress, founderAddress:p.founderAddress, ...p.vaultOwners})) if(String(v).toLowerCase()===String(p.disposableDeployer).toLowerCase()) throw new Error(`disposable deployer appears in ${k}`); }
const out={schemaVersion:"1.0.0", status:"PASSED", policyHash:"0x"+crypto.createHash("sha256").update(fs.readFileSync(policyPath)).digest("hex"), claimBoundary:"LOCAL_POLICY_SCHEMA_ONLY"};
fs.mkdirSync("qa",{recursive:true}); fs.writeFileSync("qa/authority-policy-validation.json",JSON.stringify(out,null,2)+"\n"); console.log(JSON.stringify(out,null,2));
