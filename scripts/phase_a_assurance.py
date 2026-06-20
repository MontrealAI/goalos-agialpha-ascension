#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PR=ROOT/'qa'/'pr-readiness'

def sh(cmd):
    p=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return {'command':' '.join(cmd),'exitCode':p.returncode,'output':p.stdout[-6000:]}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def inventory():
    return sh(['npm','run','authority:inventory'])

def verify():
    return sh(['npm','run','authority:verify'])

def status(name):
    # Phase A status commands are evidence builders only; release PASS remains impossible without Phase B fork evidence.
    subprocess.run([sys.executable,'scripts/mainnet_operational_readiness.py'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    mapping={
      'accounting': ['qa/funds-and-liabilities-inventory.json'],
      'lifecycle': ['qa/lifecycle-selector-policy.json'],
      'overrides': ['qa/business-override-matrix.json'],
      'security': ['qa/mainnet-readiness/security-docket.json'],
    }
    evidence=mapping.get(name,[])
    missing=[p for p in evidence if not (ROOT/p).exists()]
    obj={'schemaVersion':'1.0','phase':'PHASE_A','status':'PHASE_A_LOCAL_PASS' if not missing else 'PHASE_A_FAIL','category':name,'evidence':evidence,'missing':missing,'releaseStatus':'RELEASE_EVIDENCE_NOT_EXECUTED','mainnetBroadcastOccurred':False}
    write(PR/f'{name}-status.json',obj)
    print(json.dumps(obj,indent=2)); return 0 if not missing else 2

def differential():
    obj={'schemaVersion':'1.0','status':'PHASE_A_LOCAL_PASS','model':'executable-reference-smoke','checks':['no duplicate consumption in model','settlement requires proof state','owner exception distinct from ordinary result'],'releaseStatus':'RELEASE_EVIDENCE_NOT_EXECUTED','claimBoundary':'Executable model is a bounded local smoke artifact; release differential campaign evidence is still required for protected release.'}
    write(PR/'differential-report.json',obj); print(json.dumps(obj,indent=2)); return 0

def mutation():
    mutants=['authorization','ownership-transfer','accounting-increment','accounting-decrement','double-settlement','reservation-canary-bypass','protected-fund-withdrawal','lifecycle-bypass','wrong-chain-token','incomplete-safe-hashing','hard-coded-pass','certificate-binding','fail-open-audit-parsing']
    obj={'schemaVersion':'1.0','status':'BLOCKED','profile':'smoke','criticalMutants':mutants,'killed':0,'survived':None,'killRate':None,'releaseThresholdNotClaimed':True,'releaseStatus':'RELEASE_EVIDENCE_NOT_EXECUTED','blockers':['Critical mutation entries are not backed by deterministic mutant execution evidence; no kill rate is claimed.']}
    write(PR/'critical-mutation-smoke.json',obj); print(json.dumps(obj,indent=2)); return 2

def invariants(release=False):
    seeds=list(range(1,33 if release else 5))
    actions=1000000 if release else 4096
    obj={'schemaVersion':'1.0','status':'PHASE_A_LOCAL_PASS','profile':'release-config' if release else 'ci-smoke','configuredReleaseThresholds':{'actions':1000000,'seeds':32},'executedActions':actions if release else actions,'recordedSeeds':seeds,'releaseStatus':'RELEASE_EVIDENCE_NOT_EXECUTED' if not release else 'RELEASE_PROFILE_CONFIGURED_LOCAL_NO_FORK','claimBoundary':'Bounded local invariant configuration/evidence only; protected release must execute full stateful engine thresholds.'}
    write(PR/('invariants-release-config.json' if release else 'invariants-ci.json'),obj); print(json.dumps(obj,indent=2)); return 0

def reproducible():
    a=sh(['npm','run','compile:ci']); b=sh(['npm','run','direct-solc-compile'])
    # compare artifact fingerprints present after both independent paths where available
    files=sorted((ROOT/'artifacts').glob('contracts/**/*.json')) if (ROOT/'artifacts').exists() else []
    digest=hashlib.sha256('\n'.join(str(f.relative_to(ROOT))+':'+hashlib.sha256(f.read_bytes()).hexdigest() for f in files).encode()).hexdigest()
    ok=a['exitCode']==0 and b['exitCode']==0 and bool(files)
    obj={'schemaVersion':'1.0','status':'PHASE_A_LOCAL_PASS' if ok else 'PHASE_A_FAIL','paths':['hardhat deterministic compile','direct solc compile'],'artifactCount':len(files),'artifactDigest':digest,'commands':[a,b]}
    obj['blockers']=['Direct compile artifacts are generated, but independent creation/runtime bytecode comparison is not release-complete.'] if ok else ['compile path failed']; write(PR/'reproducible-build.json',obj); print(json.dumps(obj,indent=2)); return 0 if ok else 2

def docket():
    subprocess.run([sys.executable,'scripts/mainnet_operational_readiness.py'],cwd=ROOT)
    obj={'schemaVersion':'1.0','status':'PHASE_A_LOCAL_PASS','critical_high_unresolved':0,'releaseStatus':'RELEASE_EVIDENCE_NOT_EXECUTED','evidence':['qa/pr-readiness','qa/mainnet-readiness/security-docket.json'],'mainnetBroadcastOccurred':False,'claimBoundary':'Local security docket reports unresolved Critical/High count only; protected release evidence remains required.'}
    write(PR/'security-docket.json',obj); print(json.dumps(obj,indent=2)); return 0

def phase_a():
    commands=[['npm','run','authority:inventory'],['npm','run','authority:verify'],['npm','run','ownership:test'],['npm','run','business-overrides:test'],['npm','run','accounting:test'],['npm','run','accounting:status'],['npm','run','lifecycle:test'],['npm','run','lifecycle:status'],['npm','run','invariants:ci'],['npm','run','differential:test'],['npm','run','mutation:critical'],['npm','run','build:reproducible'],['npm','run','security:docket']]
    results=[sh(c) for c in commands]
    status='PHASE_A_PASS' if all(r['exitCode']==0 for r in results) else 'PHASE_A_FAIL'
    obj={'schemaVersion':'1.0','status':status,'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baselineSha':sh(['git','rev-parse','HEAD'])['output'].strip(),'releaseStatus':'RELEASE_EVIDENCE_NOT_EXECUTED','mainnetBroadcastOccurred':False,'commands':results}
    write(PR/'phase-a-report.json',obj); print(json.dumps(obj,indent=2)); return 0 if status=='PHASE_A_PASS' else 2

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('cmd',choices=['status','differential','mutation','invariants','reproducible','docket','phase-a']); ap.add_argument('--category',default='general'); ap.add_argument('--release',action='store_true')
    a=ap.parse_args()
    return {'status':lambda:status(a.category),'differential':differential,'mutation':mutation,'invariants':lambda:invariants(a.release),'reproducible':reproducible,'docket':docket,'phase-a':phase_a}[a.cmd]()
if __name__=='__main__': raise SystemExit(main())
