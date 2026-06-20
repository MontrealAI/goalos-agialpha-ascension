#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGI = '0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
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
    if cert.get('mainnetDeploymentAuthorized') != 'YES': blockers.append('MAINNET_DEPLOYMENT_AUTHORIZED is not YES.')
    if cert.get('ethereumMainnetAuthorized') != 'YES': blockers.extend(cert.get('blockers') or ['Certificate Ethereum Mainnet authorization is not YES.'])
    if cert.get('chain') != 'ethereum' or cert.get('chainId') != 1 or str(cert.get('agialphaToken','')).lower() != AGI.lower(): blockers.append('Ethereum mainnet target or AGIALPHA token mismatch.')
    if cert.get('mainnetDeployed') != 'NO': blockers.append('mainnetDeployed must remain NO until public transaction evidence exists.')
    if cert.get('ciCanDeployMainnet') is not False: blockers.append('GitHub Actions must not be able to deploy mainnet.')
    status = 'NO' if blockers else 'YES'
    out = {'status': status, 'ETHEREUM_MAINNET_AUTHORIZED': status, 'ethereumMainnetAuthorized': status, 'commit': cert.get('commit'), 'chain': 'ethereum', 'chainId': 1, 'agialphaToken': AGI, 'mainnetDeployed': 'NO', 'MAINNET_DEPLOYED': 'NO', 'finalManualDeploymentCommand': 'npm run deploy:ethereum-mainnet:gated' if status == 'YES' else None, 'runtimeSecretsRequiredForBroadcast': True, 'runtimeSecretsStoredInGitHub': False, 'ciCanDeployMainnet': False, 'evidence': cert.get('evidence', {}), 'blockers': blockers, 'generatedAt': now(), 'generatedBy': 'scripts/ethereum-mainnet-authorization-check.py'}
    (ROOT/'qa/public-ethereum-mainnet-authorization-evidence.json').write_text(json.dumps({'redacted': True, 'containsSecrets': False, 'containsPrivateAddresses': False, **out}, indent=2)+'\n')
    print(json.dumps(out, indent=2))
    if args.require_yes and status != 'YES': sys.exit(1)
if __name__ == '__main__': main()
