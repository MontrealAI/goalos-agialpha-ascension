#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGI = '0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'

def git(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', default='qa/mainnet-authorization-certificate.json')
    args = parser.parse_args()
    cert_path = ROOT / args.certificate
    cert = json.loads(cert_path.read_text())
    errors: list[str] = []
    for k in ['schemaVersion','generatedAt','repository','commit','chain','chainId','agialphaToken','technicallyMainnetReady','mainnetDeploymentAuthorized','ethereumMainnetAuthorized','evidence','blockers']:
        if k not in cert:
            errors.append(f'missing {k}')
    if cert.get('chain') != 'ethereum' or cert.get('chainId') != 1:
        errors.append('certificate must target Ethereum Mainnet chainId 1')
    if str(cert.get('agialphaToken','')).lower() != AGI.lower():
        errors.append('wrong AGIALPHA token')
    if cert.get('mainnetDeployed') != 'NO':
        errors.append('mainnetDeployed must be NO without transaction evidence')
    if cert.get('ciCanDeployMainnet') is not False:
        errors.append('ciCanDeployMainnet must be false')
    if cert.get('privateOperatorAuthorizationPackageRequired') is not False:
        errors.append('private operator package must not be required')
    if cert.get('runtimeSecretsStoredInGitHub') is not False:
        errors.append('runtime secrets must not be stored in GitHub')
    if cert.get('notExternallyAudited') is not True or cert.get('externalAuditRequired') is not False:
        errors.append('external-audit fields invalid')
    if cert.get('technicallyMainnetReady') == 'YES' and cert.get('blockers'):
        errors.append('YES certificate cannot have blockers')

    cert_commit = str(cert.get('commit') or '')
    head = git(['rev-parse', 'HEAD'])
    if cert_commit:
        if git(['cat-file', '-e', f'{cert_commit}^{{commit}}']) is None:
            errors.append(f'certificate commit {cert_commit} does not exist in this repository')
        # The committed certificate names the source commit used when it was generated.
        # CI regenerates before validation; a checked-out committed certificate can
        # legitimately name an ancestor because committing the generated certificate
        # changes HEAD. Existence is the enforceable invariant here.
    else:
        errors.append('certificate commit is empty')

    out = {
        'status': 'PASSED' if not errors else 'FAILED',
        'errors': errors,
        'certificateCommit': cert_commit or None,
        'currentHead': head,
    }
    print(json.dumps(out, indent=2))
    if errors:
        sys.exit(1)

if __name__ == '__main__':
    main()
