#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', default='qa/mainnet-authorization-certificate.json')
    parser.add_argument('--public-only-final', action='store_true', help='Backward-compatible no-op; certificate is always used.')
    parser.add_argument('--with-redacted-private-evidence', action='store_true', help='Deprecated no-op; private evidence is not required.')
    parser.add_argument('--require-yes', action='store_true', help='Exit nonzero unless the computed decision is YES. Use only in protected release gates.')
    args = parser.parse_args()
    cert = json.loads((ROOT/args.certificate).read_text())
    blockers: list[str] = []
    if cert.get('technicallyMainnetReady') != 'YES': blockers.append('TECHNICALLY_MAINNET_READY is not YES.')
    if cert.get('mainnetDeploymentAuthorized') != 'YES': blockers.extend(cert.get('blockers') or ['Certificate deployment authorization is not YES.'])
    if cert.get('ciCanDeployMainnet') is not False: blockers.append('CI deployment must be disabled.')
    if cert.get('runtimeSecretsStoredInGitHub') is not False: blockers.append('Runtime secrets must not be stored in GitHub.')
    if cert.get('privateOperatorAuthorizationPackageRequired') is not False: blockers.append('Private operator authorization package must not be required.')
    status = 'NO' if blockers else 'YES'
    out = {'status': status, 'MAINNET_DEPLOYMENT_AUTHORIZED': status, 'mainnetDeploymentAuthorized': status, 'commit': cert.get('commit'), 'chain': 'ethereum', 'chainId': 1, 'agialphaToken': cert.get('agialphaToken'), 'mainnetDeployed': 'NO', 'MAINNET_DEPLOYED': 'NO', 'runtimeSecretsRequiredForBroadcast': True, 'runtimeSecretsStoredInGitHub': False, 'privateOperatorAuthorizationPackageRequired': False, 'evidence': cert.get('evidence', {}), 'blockers': blockers, 'generatedAt': now(), 'generatedBy': 'scripts/mainnet-deployment-authorization-check.py'}
    (ROOT/'qa/public-mainnet-deployment-authorization-evidence.json').write_text(json.dumps({'redacted': True, 'containsSecrets': False, 'containsPrivateAddresses': False, **out}, indent=2)+'\n')
    print(json.dumps(out, indent=2))
    if args.require_yes and status != 'YES': sys.exit(1)
if __name__ == '__main__': main()
