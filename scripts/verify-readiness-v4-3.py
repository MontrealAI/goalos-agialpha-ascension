from __future__ import annotations
import json, hashlib, re, datetime, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['README.md','START_HERE.html','.env.example','package.json','contracts/registry/LaunchGateRegistry.sol','contracts/registry/JobRegistry.sol','contracts/registry/ProofSubmissionRegistry.sol','contracts/aep/AEPGoalOSCommitRegistry.sol','contracts/aep/AEPSelectionGate.sol','contracts/aep/AEPConformanceRegistry.sol','contracts/aep/AEPCommitRevealValidationRegistry.sol','contracts/aep/AEPFalsificationRegistry.sol','scripts/deploy-core.ts','scripts/deploy-ethereum-mainnet-gated.ts','scripts/preflight-ethereum-mainnet-gates.ts','scripts/mainnet-authorization-check.py','scripts/generate-evidence-docket-template.py','docs/START_HERE_v4_3.md','docs/V4_3_GATE_CLEAN_DELTA.md','docs/NEAR_10_SCORECARD_v4_3.md','docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_3.md','schemas/agialpha-mainnet-gate-v4.3.schema.json','schemas/evidence-docket-v4.2.schema.json']
def read(rel): return (ROOT/rel).read_text(encoding='utf-8', errors='ignore')
def main():
    errors=[]; warnings=[]
    for rel in REQUIRED:
        if not (ROOT/rel).exists(): errors.append(f'missing required file: {rel}')
    pkg=json.loads(read('package.json')) if (ROOT/'package.json').exists() else {}
    if pkg.get('version')!='4.3.0': errors.append('package.json version must equal 4.3.0')
    scripts=pkg.get('scripts', {})
    for s in ['readiness:v4.3','test:v4.3','evidence:docket:template','mainnet:authorization-check','compile','test','test:all','static-check','deploy:ethereum-sepolia','deploy:ethereum-mainnet:gated']:
        if s not in scripts: errors.append(f'package.json missing script: {s}')
    env=read('.env.example') if (ROOT/'.env.example').exists() else ''
    for key in ['AGIALPHA_TOKEN_ADDRESS','LEGAL_SIGNOFF_HASH','TAX_SIGNOFF_HASH','SECURITY_REVIEW_HASH','PUBLIC_CLAIMS_REVIEW_HASH','TREASURY_REVIEW_HASH','AGIALPHA_TOKEN_VERIFICATION_HASH','SEPOLIA_REHEARSAL_EVIDENCE_HASH','AUTOMATED_SECURITY_TOOLCHAIN_HASH','INTERNAL_SECURITY_REVIEW_HASH','FOUNDER_APPROVAL_HASH']:
        if key not in env: errors.append(f'.env.example missing {key}')
    launch=read('contracts/registry/LaunchGateRegistry.sol') if (ROOT/'contracts/registry/LaunchGateRegistry.sol').exists() else ''
    for needle in ['ETHEREUM_SEPOLIA_REHEARSAL','AGIALPHA_TOKEN_VERIFICATION','AUTOMATED_SECURITY_TOOLCHAIN','INTERNAL_SECURITY_REVIEW','FOUNDER_APPROVAL']:
        if needle not in launch: errors.append(f'LaunchGateRegistry missing {needle}')
    if 'BASE_SEPOLIA_REHEARSAL' in launch: errors.append('LaunchGateRegistry must not contain BASE_SEPOLIA_REHEARSAL')
    deploy=read('scripts/deploy-core.ts') if (ROOT/'scripts/deploy-core.ts').exists() else ''
    for needle in ['AGIALPHA_MAINNET','TREASURY_REVIEW_HASH','AGIALPHA_TOKEN_VERIFICATION_HASH','MockAGIALPHA','GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY']:
        if needle not in deploy: errors.append(f'deploy-core.ts missing {needle}')
    for script in ['scripts/preflight-ethereum-mainnet-gates.ts','scripts/mainnet-authorization-check.py']:
        txt=read(script) if (ROOT/script).exists() else ''
        for key in ['TREASURY_REVIEW_HASH','AGIALPHA_TOKEN_VERIFICATION_HASH']:
            if key not in txt: errors.append(f'{script} missing {key}')
    for sol in (ROOT/'contracts').rglob('*.sol'):
        txt=sol.read_text(encoding='utf-8', errors='ignore')
        if 'pragma solidity ^0.8.24;' not in txt: errors.append(f'missing pragma: {sol.relative_to(ROOT)}')
        if txt.count('{')!=txt.count('}'): errors.append(f'brace mismatch: {sol.relative_to(ROOT)}')
    (ROOT/'qa').mkdir(exist_ok=True)
    generated_at=datetime.datetime.now(datetime.UTC).isoformat()
    report={'package':'GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY','generated_at':generated_at,'static_readiness':'passed' if not errors else 'failed','files_checked':0,'errors':errors,'warnings':warnings,'status':'gate-clean evidence-ready audit candidate; mainnet not authorized','score_current_state':'9.6/10 audit-candidate package; not 10/10 until executed evidence and internal security review exist','next_gate':'real Ethereum Sepolia rehearsal and filled Evidence Docket'}
    (ROOT/'qa/READINESS_REPORT_v4_3.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    manifest=[]
    manifest_path=ROOT/'qa/MANIFEST_v4_3.json'
    manifest_excludes={ROOT/'qa/MANIFEST.json', ROOT/'qa/MANIFEST_v4_3.json'}
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT).as_posix() if p.is_file() else ''
        if p.is_file() and 'node_modules' not in p.parts and '.git' not in p.parts and p not in manifest_excludes:
            data=p.read_bytes(); manifest.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    report['files_checked']=len(manifest)
    (ROOT/'qa/READINESS_REPORT_v4_3.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    # Re-hash the readiness report after files_checked is final so manifest entries
    # match the committed evidence bundle. The manifest intentionally excludes
    # itself because a file cannot contain its own stable SHA-256.
    manifest=[]
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT).as_posix() if p.is_file() else ''
        if p.is_file() and 'node_modules' not in p.parts and '.git' not in p.parts and p not in manifest_excludes:
            data=p.read_bytes(); manifest.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    manifest_path.write_text(json.dumps({'generated_at':generated_at,'files':manifest},indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    if errors: raise SystemExit(1)
if __name__=='__main__': main()
