#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from common import artifact_files, load_policy, scan_forbidden_claims, scan_secrets, write_json, utc_now

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dir', type=Path, default=Path('evidence/mission-os/ai-product-intelligence-001')); ap.add_argument('--policy', type=Path, default=Path('config/goalos-mission-os.policy.json')); args=ap.parse_args()
    pol=load_policy(args.policy); files=artifact_files(args.dir); present={p.name for p in files}
    missing=[x for x in pol.get('requiredArtifacts',[]) if x not in present]
    claims_ok, claim_findings=scan_forbidden_claims(files, pol.get('forbiddenClaims',[])); secrets=scan_secrets(files)
    ok=not missing and claims_ok and not secrets
    result={'checked_at':utc_now(),'passed':ok,'missing':missing,'claim_findings':claim_findings,'secret_findings':secrets,'no_mainnet_broadcast':True,'no_token_movement':True}
    write_json(args.dir/'mission-os-qa.json', result); print(json.dumps(result,indent=2)); return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
