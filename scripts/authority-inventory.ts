import fs from "fs";
import path from "path";
import crypto from "crypto";

const root = path.join(__dirname, "..");
function sha256File(p: string) { return crypto.createHash("sha256").update(fs.readFileSync(path.join(root,p))).digest("hex"); }
function walk(dir: string): string[] { return fs.readdirSync(dir,{withFileTypes:true}).flatMap(d=> d.isDirectory()? walk(path.join(dir,d.name)) : [path.join(dir,d.name)]); }
const contracts = walk(path.join(root,"contracts")).filter(f=>f.endsWith(".sol"));
type ContractInfo = {name:string; path:string; bases:string[]};
const infos: ContractInfo[] = [];
for (const f of contracts) {
  const s=fs.readFileSync(f,"utf8");
  for (const m of s.matchAll(/(?:abstract\s+)?contract\s+(\w+)(?:\s+is\s+([^\{]+))?\s*\{/g)) {
    const bases=(m[2]||"").split(",").map(x=>x.trim().split(/\s+/)[0]).filter(Boolean);
    infos.push({name:m[1], path:path.relative(root,f), bases});
  }
}
const byName = new Map(infos.map(i=>[i.name,i]));
const memo = new Map<string, boolean>();
function inheritsGoalOS(name: string): boolean {
  if (name === "GoalOSAccessControl") return true;
  if (memo.has(name)) return memo.get(name)!;
  const info = byName.get(name);
  if (!info) return false;
  const result = info.bases.some(base => inheritsGoalOS(base));
  memo.set(name, result);
  return result;
}
const managedTypes = infos.filter(i=>i.name!=="GoalOSAccessControl" && inheritsGoalOS(i.name)).map(({name,path})=>({name,path})).sort((a,b)=>a.name.localeCompare(b.name));
const deployCore = fs.readFileSync(path.join(root,"scripts/deploy-core.ts"),"utf8");
const deployedInstances = [...deployCore.matchAll(/const\s+\w+\s*=\s*await deploy\("([^"]+)"/g)].map((m,i)=>({step:i+1,contractType:m[1],managed:m[1]!=="MockAGIALPHA"}));
const grants = [...deployCore.matchAll(/queueGrant\(([^,]+),\s*OPERATOR_ROLE,\s*([^,]+),\s*"([^"]+)"\)/g)].map(m=>({contractExpression:m[1],role:"OPERATOR_ROLE",granteeExpression:m[2],label:m[3],phase:"B_OWNER_CONFIGURATION"}));
const baseline = {schemaVersion:"1.0.0", generatedAt:"REPRODUCIBLE_STATIC_BASELINE", gitCommit:"TRACKED_BASELINE_SOURCE_HASH_BOUND", package: JSON.parse(fs.readFileSync(path.join(root,"package.json"),"utf8")), managedContractTypes: managedTypes, counts:{managedContractTypes:managedTypes.length,deployedManagedInstances:deployedInstances.filter(x=>x.managed).length,manifestEntriesIncludingAGIALPHA:49}, deployedInstances, privilegedRoles:["DEFAULT_ADMIN_ROLE","PROTOCOL_ADMIN_ROLE","OPERATOR_ROLE","REVIEWER_MANAGER_ROLE","TREASURY_ROLE","PAUSER_ROLE","VAULT_MANAGER_ROLE"], roleGrants:grants, economicNoSetterTreasuries:["AEPGoalOSCommitRegistry","MandateEpochRegistry","ReviewerBondRegistry"], sourceHashes:Object.fromEntries(["contracts/access/GoalOSAccessControl.sol","contracts/access/BusinessOverrideCore.sol","scripts/deploy-core.ts","scripts/validate-runtime-addresses.ts"].filter(p=>fs.existsSync(path.join(root,p))).map(p=>[p,sha256File(p)])), claimBoundary:"LOCAL_SOURCE_INVENTORY_ONLY; not deployment, verification, audit, Safe, Ledger, or chain evidence."};
fs.mkdirSync(path.join(root,"qa"),{recursive:true});
const out=JSON.stringify(baseline,null,2)+"\n";
fs.writeFileSync(path.join(root,"qa/authority-baseline.json"),out);
fs.writeFileSync(path.join(root,"qa/authority-baseline.json.sha256"),crypto.createHash("sha256").update(out).digest("hex")+"\n");
console.log(`authority inventory: ${managedTypes.length} managed types, ${deployedInstances.filter(x=>x.managed).length} managed deployment steps`);
if (!managedTypes.some(x=>x.name === "JobRegistry")) { console.error("JobRegistry missing from managed authority inventory"); process.exit(1); }
