#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGI = '0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'


def git(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def sha256_path(rel: str) -> str | None:
    path = ROOT / rel
    if not path.exists():
        return None
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(p for p in path.rglob('*') if p.is_file()):
            digest.update(str(child.relative_to(ROOT)).encode())
            digest.update(child.read_bytes())
        return '0x' + digest.hexdigest()
    return '0x' + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', default='qa/mainnet-authorization-certificate.json')
    args = parser.parse_args()
    cert_path = ROOT / args.certificate
    cert = json.loads(cert_path.read_text())
    errors: list[str] = []
    warnings: list[str] = []
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
        elif head and cert_commit != head:
            # A committed generated certificate normally names the source commit that
            # existed immediately before the commit adding the regenerated artifact.
            # Do not accept stale source coverage: every evidence hash below must
            # still match the current checkout, including deployment/security scripts.
            merge_base = git(['merge-base', cert_commit, head])
            if merge_base != cert_commit:
                errors.append(f'certificate commit {cert_commit} is not an ancestor of current HEAD {head}')
            else:
                warnings.append(f'certificate commit {cert_commit} differs from current HEAD {head}; freshness is enforced by current evidence hash verification')
    else:
        errors.append('certificate commit is empty')

    evidence = cert.get('evidence')
    if not isinstance(evidence, dict):
        errors.append('evidence must be an object')
        evidence = {}
    stale_evidence: list[str] = []
    for name, entry in evidence.items():
        if not isinstance(entry, dict):
            errors.append(f'evidence.{name} must be an object with path and sha256')
            continue
        rel = entry.get('path')
        expected = entry.get('sha256')
        if not isinstance(rel, str) or not rel:
            errors.append(f'evidence.{name}.path is missing')
            continue
        if not isinstance(expected, str) or not expected.startswith('0x'):
            errors.append(f'evidence.{name}.sha256 is missing')
            continue
        actual = sha256_path(rel)
        if actual is None:
            stale_evidence.append(f'{name}: missing {rel}')
        elif actual != expected:
            stale_evidence.append(f'{name}: {rel} expected {expected} actual {actual}')
    if stale_evidence:
        errors.append('certificate evidence hashes are stale for current checkout: ' + '; '.join(stale_evidence))

    out = {
        'status': 'PASSED' if not errors else 'FAILED',
        'errors': errors,
        'warnings': warnings,
        'certificateCommit': cert_commit or None,
        'currentHead': head,
        'freshEvidenceHashes': not stale_evidence,
    }
    print(json.dumps(out, indent=2))
    if errors:
        sys.exit(1)

if __name__ == '__main__':
    main()
