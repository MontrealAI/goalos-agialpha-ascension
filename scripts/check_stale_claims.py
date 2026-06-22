#!/usr/bin/env python3
import pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
terms=['Ethereum Mainnet deployed: NO','MAINNET_DEPLOYED = NO','qa/mainnet-authorization-certificate.json is the sole source of truth','ownership handoff still required','single-deployer permanent-address mode is blocked','Solidity 0.8.35']
allowed=('docs/archive/','qa/','release/','docs/adr/','docs/dormant-mainnet/','docs/AUTOMATED_SECURITY_TOOLCHAIN_REQUEST_v4_2.md','docs/CODEX_PRODUCTION_HANDOFF_PROMPT.md','docs/PRODUCTION_CONTINUATION_PLAN.md','docs/FOUNDATION_HANDOFF_MEMO.md','docs/LEGAL_TAX_PUBLIC_CLAIMS_GATE_MEMO.md','docs/runbooks/PROTECTED_MAINNET_READINESS.md')
hits=[]
for p in list(root.glob('*.md'))+list((root/'docs').rglob('*.md'))+list((root/'website').rglob('*.html'))+list((root/'website').rglob('*.md')):
 rel=str(p.relative_to(root))
 if rel.startswith(allowed) or rel in allowed: continue
 text=p.read_text(errors='ignore')
 for t in terms:
  if t in text: hits.append(f'{rel}: {t}')
if hits:
 print('\n'.join(hits)); sys.exit(1)
print('no stale current documentation claims')
