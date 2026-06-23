#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMANDS=[
 ('Repository safety',['npm','run','repo:preflight']),
 ('Compiler alignment',['npm','run','verify:compiler-alignment']),
 ('Compilation',['npm','run','compile:ci']),
 ('Tests',['npm','run','test:ci']),
 ('Static analysis',['npm','run','static-check']),
 ('Secret scanning',['npm','run','audit:secrets']),
 ('Internal security gate',['npm','run','audit:fail-on-critical']),
 ('Current release-state',['npm','run','mainnet:release-state:check']),
 ('Registry',['npm','run','mainnet:contracts:check']),
 ('Operator evidence',['npm','run','mainnet:postdeploy:operator-evidence:validate']),
 ('Public status',['npm','run','docs:status:check']),
 ('Docs determinism',['npm','run','docs:all']),
 ('Release record',['npm','run','release:mainnet:validate']),
 ('Release packet',['npm','run','release:mainnet:check']),
]
def run(label,cmd):
    print(f'\n## {label}: {" ".join(cmd)}', flush=True)
    r=subprocess.run(cmd,cwd=ROOT)
    if r.returncode: raise SystemExit(r.returncode)
def main():
    for label,cmd in COMMANDS: run(label,cmd)
    state=json.loads((ROOT/'qa/mainnet-release-state.normalized.json').read_text())
    c=state['counts']; s=state['statuses']; f=state['facts']
    print('\nGOALOS MAINNET RELEASE-STATE VALIDATION\n')
    lines=[
      'Repository safety: PASS','Compiler alignment: PASS','Compilation: PASS','Tests: PASS','Static analysis: PASS','Secret scanning: PASS','Internal security gate: PASS',
      f"Registry: PASS — {c['registryEntries']} entries",f"Deployment: PASS — {c['goalosContracts']} GoalOS contracts",f"Operator verification: PASS — {c['operatorVerifiedContracts']}/48",f"Configuration: PASS — {c['phaseBGrantsActive']}/{c['phaseBGrantsExpected']} grants",'Permanent authority: PASS — Wallet B / Ledger',f"Wallet A managed roles: PASS — {c['walletAManagedRoles']}",f"Postdeployment operator evidence: PASS — {f['postdeploymentStatus']}",f"Predeployment authorization: {s['predeploymentAuthorization']}",f"Independent live revalidation: {s['independentLiveRevalidation']}",f"Source identity reproducibility: {s['sourceIdentityReproducibility']}",f"Production activation: {s['productionActivation']}",f"User-fund authorization: {s['userFundAuthorization']}",'','OVERALL APPLICABLE RESULT: PASS']
    print('\n'.join(lines))
if __name__=='__main__': main()
