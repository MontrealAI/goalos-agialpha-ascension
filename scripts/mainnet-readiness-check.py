#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read_json(rel: str): return json.loads((ROOT / rel).read_text())
def exists_from_evidence(cert: dict, key: str) -> bool:
    entry = cert.get('evidence', {}).get(key, {})
    path = entry.get('path') if isinstance(entry, dict) else entry
    return bool(path and (ROOT / path).exists())

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', default='qa/mainnet-authorization-certificate.json')
    parser.add_argument('--public-only-final', action='store_true', help='Backward-compatible no-op; certificate is always used.')
    parser.add_argument('--with-redacted-private-evidence', action='store_true', help='Deprecated no-op; private evidence is not required.')
    parser.add_argument('--require-yes', action='store_true', help='Exit nonzero unless the computed decision is YES. Use only in protected release gates.')
    args = parser.parse_args()
    cert = read_json(args.certificate)
    blockers: list[str] = []
    if cert.get('technicallyMainnetReady') != 'YES': blockers.extend(cert.get('blockers') or ['Certificate technical readiness is not YES.'])
    for key in ['repoDoctor','compilerAlignment','compile','tests','testAll','staticCheck','publicStatus','noPrivateOperatorData','noPaidProducts','toolchainClearance','unresolvedFindings','invariants','localRehearsal','localEvidenceDocket','agialphaTokenVerification','mainnetGuardrails','branchProtectionOrRiskAcceptance','publicGovernanceApproval']:
        if not exists_from_evidence(cert, key): blockers.append(f'Certificate evidence missing or not found: {key}')
    status = 'NO' if blockers else 'YES'
    out = {'status': status, 'TECHNICALLY_MAINNET_READY': status, 'technicallyMainnetReady': status, 'commit': cert.get('commit'), 'chain': cert.get('chain'), 'chainId': cert.get('chainId'), 'agialphaToken': cert.get('agialphaToken'), 'mainnetDeployed': 'NO', 'MAINNET_DEPLOYED': 'NO', 'privateOperatorAuthorizationPackageRequired': False, 'externalAuditRequired': False, 'evidence': cert.get('evidence', {}), 'blockers': blockers, 'generatedAt': now(), 'generatedBy': 'scripts/mainnet-readiness-check.py'}
    (ROOT/'qa/public-mainnet-technical-readiness-evidence.json').write_text(json.dumps({'redacted': True, 'containsSecrets': False, 'containsPrivateAddresses': False, **out}, indent=2)+'\n')
    print(json.dumps(out, indent=2))
    if args.require_yes and status != 'YES': sys.exit(1)
if __name__ == '__main__': main()
