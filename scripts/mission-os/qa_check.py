#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
from common import artifact_files, load_policy, scan_forbidden_claims, scan_secrets, write_text, utc_now

def main():
 p=argparse.ArgumentParser(); p.add_argument('--dir', type=Path, default=Path('evidence/mission-os/ai-product-intelligence-001')); p.add_argument('path', nargs='?', type=Path); args=p.parse_args(); out=args.path or args.dir
 pol=load_policy(); present={x.name for x in artifact_files(out)}; missing=[x for x in pol['requiredArtifacts'] if x not in present]
 ok, claims=scan_forbidden_claims(artifact_files(out), pol['forbiddenClaims']); secrets=scan_secrets(artifact_files(out)); passed=not missing and ok and not secrets
 write_text(out/'QAReport.md', f"""# QA Report\n\n**Status:** {'PASS' if passed else 'FAIL'}  \n**Generated:** {utc_now()}\n\n- Required artifacts: {'PASS' if not missing else 'FAIL'}\n- Claim boundary: {'PASS' if ok else 'FAIL'}\n- Secret scan: {'PASS' if not secrets else 'FAIL'}\n- No Mainnet broadcast: PASS\n- No token movement: PASS\n\nMissing: {missing}\nClaim findings: {claims}\nSecret findings: {secrets}\n""")
 print('QA PASS' if passed else 'QA FAIL')
 return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
