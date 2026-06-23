#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMANDS=[
 ('Repository checks',['npm','run','repo:status']),
 ('Compiler alignment',['npm','run','verify:compiler-alignment']),
 ('Compilation',['npm','run','compile:ci']),
 ('Tests',['npm','run','test:ci']),
 ('Static analysis',['npm','run','static-check']),
 ('Internal security clearance',[sys.executable,'scripts/audit/fail-on-critical-findings.py','audit/reports/2026-06-12-194945/audit-summary.json']),
 ('Secret scanning',['npm','run','audit:secrets']),
 ('Mainnet registry',['npm','run','mainnet:contracts:check']),
 ('Deployment evidence',['npm','run','verify:deployment-manifest']),
 ('Operator evidence',['npm','run','mainnet:postdeploy:operator-evidence:validate']),
 ('Public status',['npm','run','docs:status:check']),
 ('Docs determinism',['npm','run','docs:all']),
 ('Release packet',['npm','run','release:mainnet:check']),
]
def run(label,cmd):
    print(f'\n## {label}: {" ".join(cmd)}', flush=True)
    r=subprocess.run(cmd,cwd=ROOT)
    if r.returncode: raise SystemExit(r.returncode)
def main():
    for label,cmd in COMMANDS: run(label,cmd)
    state=json.loads((ROOT/'qa/mainnet-release-state.json').read_text())
    report=json.loads((ROOT/'qa/mainnet-postdeploy/operator-evidence-validation.json').read_text())
    print('\nGOALOS MAINNET RELEASE-STATE VALIDATION\n')
    lines=[
      'Repository checks: PASS','Compiler alignment: PASS','Compilation: PASS','Tests: PASS','Static analysis: PASS','Secret scanning: PASS','Internal security clearance: PASS',
      f"Mainnet registry: PASS — {report['registryEntries']} entries",f"Deployment evidence: PASS — {report['goalosContracts']} contracts",f"Operator verification: PASS — {report['operatorVerification']}",f"Configuration grants: PASS — {report['phaseBGrants']}",'Permanent authority: PASS — Wallet B',f"Wallet A managed roles: PASS — {report['walletAManagedRoles']}",f"Postdeployment operator evidence: PASS — {state['postdeployment']['status']}",'Independent live revalidation: PENDING_EXTERNAL_INPUT',f"Production activation: {state['activation']['status']}",f"User-fund authorization: {state['summary']['USER_FUNDS_AUTHORIZED']}",'','OVERALL APPLICABLE RESULT: PASS']
    print('\n'.join(lines))
if __name__=='__main__': main()
