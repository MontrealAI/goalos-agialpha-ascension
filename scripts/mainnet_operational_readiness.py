#!/usr/bin/env python3
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACTS=ROOT/'contracts'
QA=ROOT/'qa'; DOCS=ROOT/'docs'; RUNBOOKS=DOCS/'runbooks'
FUNC_RE=re.compile(r'function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^;{)]*(?:\)[^;{]*)?)', re.M)
STATE_HINTS=('external','public')
VIEW_HINTS=('view','pure')
OWNER_NAMES=('owner','transferOwnership','acceptOwnership','cancelOwnershipTransfer','pendingOwner')
ASSET_WORDS=('Vault','Treasury','Bond','Reward','Stake','Router')
STATE_WORDS=('Job','Claim','Submission','Proof','Reward','Bond','Stake','Credential','Reputation','AEP','Tranche','Treasury','Vault','Agent','Operator','Registry')

def sh(cmd):
    try:
        return subprocess.check_output(cmd,cwd=ROOT,text=True,stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f'UNAVAILABLE: {e}'

def sha_file(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def tree_hash():
    files=[]
    for p in ROOT.rglob('*'):
        if not p.is_file():
            continue
        rel=str(p.relative_to(ROOT))
        generated_prefixes=('qa/mainnet-operational','qa/business-override-matrix.json','qa/funds-and-liabilities-inventory.json','qa/lifecycle-selector-policy.json','qa/controlled-mainnet-canary-template.json','qa/mainnet-production-readiness-dossier.json','docs/MAINNET_OPERATIONAL_GAP_MATRIX.md','docs/BUSINESS_OVERRIDE_MATRIX.md','docs/FUNDS_AND_LIABILITIES_MODEL.md','docs/LIFECYCLE_SELECTOR_POLICY.md','docs/runbooks/')
        if '.git' in p.parts or 'node_modules' in p.parts or 'artifacts' in p.parts or 'cache' in p.parts or rel.startswith(generated_prefixes):
            continue
        files.append(p)
    h=hashlib.sha256()
    for p in sorted(files):
        h.update(str(p.relative_to(ROOT)).encode()+b'\0'+hashlib.sha256(p.read_bytes()).hexdigest().encode()+b'\n')
    return h.hexdigest()

def contracts():
    out=[]
    for p in sorted(CONTRACTS.rglob('*.sol')):
        txt=p.read_text(errors='ignore')
        names=re.findall(r'contract\s+(\w+)|abstract\s+contract\s+(\w+)|interface\s+(\w+)',txt)
        cname=next((a or b or c for a,b,c in names), p.stem)
        funcs=[]
        for m in re.finditer(r'function\s+(\w+)\s*\([^)]*\)\s*([^;{]*)', txt):
            attrs=m.group(2)
            if any(x in attrs for x in STATE_HINTS) and not any(x in attrs for x in VIEW_HINTS):
                funcs.append({'name':m.group(1),'attributes':' '.join(attrs.split()),'classification':classify(m.group(1), cname)})
        roles=sorted(set(re.findall(r'bytes32\s+(?:public\s+)?(?:constant\s+)?([A-Z0-9_]+_ROLE)',txt)))
        out.append({'path':str(p.relative_to(ROOT)),'contract':cname,'sha256':sha_file(p),'stateChangingSelectors':funcs,'roles':roles,'assetHolding':any(w in cname for w in ASSET_WORDS),'workflow':any(w in cname for w in STATE_WORDS)})
    return out

def classify(fn,c):
    n=fn.lower()
    if any(x in n for x in ['pause','unpause','shutdown','winddown','migrat','lifecycle']): return 'lifecycle_control_or_migration'
    if any(x in n for x in ['recover','override','cancel','resolve','slash','refund','revoke']): return 'owner_recovery_or_safe_exit'
    if any(x in n for x in ['grant','revoke','set','configure','transferownership','acceptownership']): return 'configuration'
    if any(x in n for x in ['create','submit','claim','deposit','stake','reserve','fund','approve']): return 'new_obligation_or_risk_increase'
    if any(x in n for x in ['withdraw','release','pay','settle','return']): return 'safe_exit_or_settlement'
    return 'normal_operation_unclassified_review_required'

def write_json(p,obj): p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def write_md(p,title,lines): p.write_text('# '+title+'\n\n'+'\n'.join(lines)+'\n')

def generate():
    QA.mkdir(exist_ok=True); DOCS.mkdir(exist_ok=True); RUNBOOKS.mkdir(parents=True,exist_ok=True)
    inv=contracts(); base=sh(['git','rev-parse','HEAD']); status=sh(['git','status','--short'])
    inventory={'generatedBy':'scripts/mainnet_operational_readiness.py','baselineSha':base,'treeHash':tree_hash(),'cleanTree':status=='','contracts':inv}
    write_json(QA/'mainnet-operational-inventory.json',inventory)
    gates=[]
    for i,name in enumerate(['Ownership continuity','Explicit Business Owner override capability','Company-wide accounting and solvency observability','Recovery, migration, wind-down, and shutdown','Autonomous stateful verification and exact-bytecode assurance'],1):
        gates.append({'gate':i,'name':name,'status':'PARTIAL','claim':'Repository evidence inventory exists; final PASS requires live/private configuration, fork RPC, and complete adversarial runs. This artifact is claim-bounded and does not assert Mainnet deployment.'})
    matrix={'baselineSha':base,'sourceTreeHash':inventory['treeHash'],'requirements':gates,'evidence':['qa/mainnet-operational-inventory.json']}
    write_json(QA/'mainnet-operational-gap-matrix.json',matrix)
    write_md(DOCS/'MAINNET_OPERATIONAL_GAP_MATRIX.md','Mainnet Operational Gap Matrix',[f'- Gate {g["gate"]}: **{g["status"]}** — {g["name"]}. {g["claim"]}' for g in gates])
    overrides=[]
    for c in inv:
        if c['workflow']:
            overrides.append({'contract':c['contract'],'path':c['path'],'ownerRecoveryAction':'See classified selectors; add typed owner override before PASS if no recovery selector exists for a nonterminal state.','evidence':['source inventory'],'testCoverage':'BLOCKED until contract-specific tests are complete'})
    write_json(QA/'business-override-matrix.json',{'entries':overrides})
    write_md(DOCS/'BUSINESS_OVERRIDE_MATRIX.md','Business Override Matrix',[f'- `{e["contract"]}` (`{e["path"]}`): {e["ownerRecoveryAction"]}' for e in overrides])
    funds=[{'contract':c['contract'],'path':c['path'],'assetHolding':c['assetHolding'],'accountingStatus':'REQUIRES_EXACT_ONCHAIN_STATUS' if c['assetHolding'] else 'NOT_ASSET_HOLDING'} for c in inv]
    write_json(QA/'funds-and-liabilities-inventory.json',{'entries':funds,'invariant':'actualBalance >= protectedLiability + requiredReservations + pendingWithdrawals'})
    write_md(DOCS/'FUNDS_AND_LIABILITIES_MODEL.md','Funds and Liabilities Model',['Per-token accounting is required; unlike tokens must not be value-aggregated.','',* [f'- `{e["contract"]}`: {e["accountingStatus"]}' for e in funds]])
    selector={'selectors':[{'contract':c['contract'],'path':c['path'],**f} for c in inv for f in c['stateChangingSelectors']]}
    write_json(QA/'lifecycle-selector-policy.json',selector)
    write_md(DOCS/'LIFECYCLE_SELECTOR_POLICY.md','Lifecycle Selector Policy',[f'- `{s["contract"]}.{s["name"]}`: `{s["classification"]}`' for s in selector['selectors']])
    canary={'claimBoundary':'template only; not authorized and not broadcast','limits':{'aggregateLiability':'1000000000000000000','perJobReward':'100000000000000000','perBond':'10000000000000000','vaultOutflowPerDay':'100000000000000000','concurrentObligations':10},'zeroMeansUnlimited':False}
    write_json(QA/'controlled-mainnet-canary-template.json',canary)
    write_md(RUNBOOKS/'MIGRATION_SHUTDOWN_RUNBOOK.md','Migration and Shutdown Runbook',['1. Enter WindDown; stop new obligations.','2. Resolve protected liabilities and reservations.','3. Verify authority, accounting, and selector-policy roots.','4. Register successor only after release commitments are generated.','5. Move only verified free funds.','6. Final shutdown must fail closed if any liability remains.'])
    write_md(RUNBOOKS/'OWNERSHIP_SAFE_EOA_RUNBOOK.md','Ownership Safe/EOA Runbook',['Generate transactions with ownership tooling; verify live chainId from provider; Safe-labelled owners must have contract code and Safe-compatible interface; pending owners are non-authoritative until acceptance.'])
    dossier={'status':'BLOCKED','reason':'Fail-closed dossier: mandatory live/private fork, independent builds, symbolic, mutation, and exact Mainnet-fork evidence must be supplied before PASS. No Mainnet broadcast evidence is present or claimed.','baselineSha':base,'sourceTreeHash':inventory['treeHash'],'cleanTree':status=='','artifacts':['qa/mainnet-operational-gap-matrix.json','qa/business-override-matrix.json','qa/funds-and-liabilities-inventory.json','qa/lifecycle-selector-policy.json','qa/controlled-mainnet-canary-template.json']}
    write_json(QA/'mainnet-production-readiness-dossier.json',dossier)
    return dossier

def validate():
    d=generate(); print(json.dumps(d,indent=2)); return 2 if d['status']!='PASS' else 0
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--validate',action='store_true'); args=ap.parse_args(); sys.exit(validate() if args.validate else (generate() and 0))
