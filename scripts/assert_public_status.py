#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'qa/mainnet-authorization-certificate.json'
DOCS = [ROOT / 'START_HERE.md', ROOT / 'README.md', ROOT / 'docs/CURRENT_STATUS.md', ROOT / 'docs/MAINNET_AUTHORIZATION_CERTIFICATE.md', ROOT / 'docs/MAINNET_TECHNICAL_READINESS_DECISION.md', ROOT / 'docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md', ROOT / 'docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md', ROOT / 'docs/START_HERE_MAINNET.md']
texts = {p: p.read_text(encoding='utf-8', errors='ignore') for p in DOCS if p.exists()}
combined = '\n'.join(texts.values()); low = combined.lower(); errors: list[str] = []
cert = None
if CERT.exists():
    try: cert = json.loads(CERT.read_text())
    except Exception as exc: errors.append(f'Unable to parse certificate: {exc}')
claims_yes = all(phrase in low for phrase in ['ethereum mainnet technical readiness: yes','ethereum mainnet deployment authorization: yes','ethereum mainnet authorization: yes'])
if not cert and claims_yes:
    errors.append('Public docs claim Ethereum Mainnet authorization YES but qa/mainnet-authorization-certificate.json is missing.')
if cert:
    expected = {
        'ethereum mainnet technical readiness': cert.get('technicallyMainnetReady'),
        'ethereum mainnet deployment authorization': cert.get('mainnetDeploymentAuthorized'),
        'ethereum mainnet authorization': cert.get('ethereumMainnetAuthorized'),
        'ethereum mainnet deployed': cert.get('mainnetDeployed'),
    }
    full_status_files = {
        'START_HERE.md',
        'README.md',
        'docs/CURRENT_STATUS.md',
        'docs/START_HERE_MAINNET.md',
    }
    for rel in full_status_files:
        path = ROOT / rel
        text = texts.get(path, '').lower()
        if not text:
            errors.append(f'{rel}: missing active public status document')
            continue
        for label, value in expected.items():
            phrase = f'{label}: {str(value).lower()}'
            if phrase not in text:
                errors.append(f'{rel}: missing certificate-backed status phrase: {label}: {value}')
    decision_requirements = {
        'docs/MAINNET_TECHNICAL_READINESS_DECISION.md': [('ethereum mainnet technical readiness', cert.get('technicallyMainnetReady'))],
        'docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md': [('ethereum mainnet deployment authorization', cert.get('mainnetDeploymentAuthorized'))],
        'docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md': [('ethereum mainnet authorization', cert.get('ethereumMainnetAuthorized'))],
    }
    for rel, requirements in decision_requirements.items():
        path = ROOT / rel
        text = texts.get(path, '').lower()
        if not text:
            errors.append(f'{rel}: missing active decision document')
            continue
        for label, value in requirements:
            phrase = f'{label}: **{str(value).lower()}**'
            plain_phrase = f'{label}: {str(value).lower()}'
            if phrase not in text and plain_phrase not in text:
                errors.append(f'{rel}: missing certificate-backed status phrase: {label}: {value}')
        deployed_phrase = f"mainnet_deployed: **{str(cert.get('mainnetDeployed')).lower()}**"
        if deployed_phrase not in text:
            errors.append(f"{rel}: missing certificate-backed status phrase: MAINNET_DEPLOYED: {cert.get('mainnetDeployed')}")
    certificate_doc = texts.get(ROOT / 'docs/MAINNET_AUTHORIZATION_CERTIFICATE.md', '').lower()
    if not certificate_doc:
        errors.append('docs/MAINNET_AUTHORIZATION_CERTIFICATE.md: missing active certificate document')
    else:
        certificate_requirements = {
            'technically_mainnet_ready': cert.get('technicallyMainnetReady'),
            'mainnet_deployment_authorized': cert.get('mainnetDeploymentAuthorized'),
            'ethereum_mainnet_authorized': cert.get('ethereumMainnetAuthorized'),
            'mainnet_deployed': cert.get('mainnetDeployed'),
        }
        for label, value in certificate_requirements.items():
            phrase = f'{label}: **{str(value).lower()}**'
            if phrase not in certificate_doc:
                errors.append(f'docs/MAINNET_AUTHORIZATION_CERTIFICATE.md: missing certificate-backed status phrase: {label.upper()}: {value}')
    if cert.get('mainnetDeployed') != 'NO': errors.append('Certificate must keep mainnetDeployed as NO until transaction evidence exists.')
    if cert.get('runtimeSecretsStoredInGitHub') is not False: errors.append('Certificate must state runtime secrets are not stored in GitHub.')
    if cert.get('ciCanDeployMainnet') is not False: errors.append('Certificate must state CI cannot deploy mainnet.')
if 'not externally audited' not in low: errors.append('Missing required boundary: Not externally audited.')
if 'runtime rpc url and deployer key outside github' not in low and 'runtime rpc/key' not in low:
    errors.append('Missing runtime RPC/key outside GitHub boundary.')
if 'ethereum mainnet deployed: no' not in low and 'mainnet_deployed: **no**' not in low:
    errors.append('Public docs must state Ethereum Mainnet deployed: NO.')
for forbidden, allowed_context in [
    ('externally audited', 'not externally audited'), ('legal approval', 'does not claim'), ('tax review', 'does not claim'), ('tax approved', 'does not claim'), ('guaranteed secure', 'does not claim'), ('guaranteed security', 'does not claim'), ('guaranteed non-security', 'does not claim'), ('investment opportunity', 'does not claim'), ('yield', 'does not claim'), ('price target', 'does not claim'), ('revenue share', 'does not claim'), ('production deployed', 'does not claim')]:
    for path, text in texts.items():
        for i, line in enumerate(text.splitlines(), 1):
            l=line.lower()
            if forbidden in l and allowed_context not in l and 'not ' not in l and 'no ' not in l and 'must not' not in l and 'do not' not in l and 'does not' not in l and 'unless' not in l:
                errors.append(f'{path.relative_to(ROOT)}:{i}: unsafe public claim: {forbidden}')
active_gate_files = {'START_HERE.md','README.md','docs/CURRENT_STATUS.md','docs/START_HERE_MAINNET.md','docs/MAINNET_AUTHORIZATION_CERTIFICATE.md','docs/MAINNET_TECHNICAL_READINESS_DECISION.md','docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md','docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md'}
for path, text in texts.items():
    rel=str(path.relative_to(ROOT))
    if rel in active_gate_files:
        for i,line in enumerate(text.splitlines(),1):
            l=line.lower()
            if 'external audit closure' in l or 'external_audit_closure' in line:
                errors.append(f'{rel}:{i}: stale external audit closure active-gate language')
            if ('private operator package required' in l or 'private operator evidence required' in l) and 'false' not in l and 'not required' not in l:
                errors.append(f'{rel}:{i}: stale private-operator mandatory gate language')
if errors:
    print('Public status assertion failed:')
    for e in errors: print(f'- {e}')
    sys.exit(1)
print('Public status assertion passed: certificate-backed public mainnet authorization is consistent, bounded, not externally audited, and not deployed.')
