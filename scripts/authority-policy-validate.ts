import fs from "fs"; import crypto from "crypto"; import { ethers } from "ethers";
const args=process.argv.slice(2); if(args.includes("--help")){console.log("Usage: ts-node scripts/authority-policy-validate.ts --policy <file> [--json]"); process.exit(0)}
const policyPath=args[args.indexOf("--policy")+1]; if(!policyPath) throw new Error("--policy required");
const raw=fs.readFileSync(policyPath); const p=JSON.parse(raw.toString("utf8"));
const schema=JSON.parse(fs.readFileSync("schemas/authority-policy.schema.json","utf8"));
const required=schema.required as string[];
for(const k of required) if(p[k]===undefined) throw new Error(`schema violation: missing ${k}`);
function requireEnum(name:string, value:any, allowed:any[]){ if(!allowed.includes(value)) throw new Error(`schema violation: ${name} must be one of ${allowed.join(",")}`); }
requireEnum("chainId", p.chainId, schema.properties.chainId.enum);
requireEnum("profile", p.profile, schema.properties.profile.enum);
requireEnum("governanceOwnerKind", p.governanceOwnerKind, schema.properties.governanceOwnerKind.enum);
const vaultRequired=schema.properties.vaultOwners.required as string[];
for(const key of vaultRequired) if(!p.vaultOwners || p.vaultOwners[key]===undefined) throw new Error(`schema violation: missing vaultOwners.${key}`);
for(const [k,v] of Object.entries({governanceOwner:p.governanceOwner, operationsAddress:p.operationsAddress, treasuryAddress:p.treasuryAddress, founderAddress:p.founderAddress, ...p.vaultOwners})) if(!ethers.isAddress(String(v))||ethers.getAddress(String(v))===ethers.ZeroAddress) throw new Error(`invalid address ${k}`);
if(p.governanceOwnerKind==="LEDGER_EOA" && p.allowSingleLedgerEOAGovernance!=="I_ACCEPT_SINGLE_KEY_AND_RECOVERY_RISK") throw new Error("LEDGER_EOA requires explicit acknowledgement");
if(p.disposableDeployer){ for(const [k,v] of Object.entries({governanceOwner:p.governanceOwner, operationsAddress:p.operationsAddress, treasuryAddress:p.treasuryAddress, founderAddress:p.founderAddress, ...p.vaultOwners})) if(String(v).toLowerCase()===String(p.disposableDeployer).toLowerCase()) throw new Error(`disposable deployer appears in ${k}`); }
const out={schemaVersion:"1.0.0", status:"PASSED", policyHash:"0x"+crypto.createHash("sha256").update(raw).digest("hex"), schemaHash:"0x"+crypto.createHash("sha256").update(fs.readFileSync("schemas/authority-policy.schema.json")).digest("hex"), claimBoundary:"LOCAL_POLICY_SCHEMA_ONLY"};
fs.mkdirSync("qa",{recursive:true}); fs.writeFileSync("qa/authority-policy-validation.json",JSON.stringify(out,null,2)+"\n"); console.log(JSON.stringify(out,null,2));
