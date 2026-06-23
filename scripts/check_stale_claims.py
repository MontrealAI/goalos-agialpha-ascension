#!/usr/bin/env python3
import pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
terms=['Ethereum Mainnet deployed: NO','Mainnet configured: NO','ownership acceptance required for this deployment','Stage-B operator evidence: BLOCKED','external audit completion required','Stage-B/live postdeployment check | BLOCKED','External audit completion | NO']
allowed_prefixes=('docs/archive/','qa/','release/','docs/adr/','docs/dormant-mainnet/')
allowed_files={'docs/AUTOMATED_SECURITY_TOOLCHAIN_REQUEST_v4_2.md','docs/LEGAL_TAX_PUBLIC_CLAIMS_GATE_MEMO.md','docs/CODEX_PRODUCTION_HANDOFF_PROMPT.md','docs/PRODUCTION_CONTINUATION_PLAN.md','docs/FOUNDATION_HANDOFF_MEMO.md','docs/MAINNET_AUTHORIZATION_CERTIFICATE.md','docs/MAINNET_TECHNICAL_READINESS_DECISION.md','docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md','docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.md'}
hits=[]
for base in [root, root/'docs', root/'website']:
    patterns=['*.md'] if base!=root/'website' else ['*.html','*.md']
    files=[]
    for pat in patterns: files += list(base.rglob(pat) if base!=root else base.glob(pat))
    for p in files:
        rel=str(p.relative_to(root))
        if rel.startswith(allowed_prefixes): continue
        text=p.read_text(errors='ignore')
        if rel in allowed_files: continue
        for t in terms:
            if t in text: hits.append(f'{rel}: {t}')
        if 'externally audited' in text.lower() and 'not externally audited' not in text.lower(): hits.append(f'{rel}: externally audited')
if hits:
    print('\n'.join(hits)); sys.exit(1)
print('no stale current documentation claims')
