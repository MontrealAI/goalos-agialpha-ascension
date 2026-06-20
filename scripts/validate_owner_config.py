#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, sys

def main():
    if len(sys.argv)!=2:
        print('usage: validate_owner_config.py <base64-json>', file=sys.stderr); return 2
    raw=base64.b64decode(sys.argv[1], validate=True)
    data=json.loads(raw)
    missing=[k for k in ('ownerKind','ownerAddress','chainId') if k not in data]
    if missing: print(json.dumps({'valid':False,'missing':missing})); return 2
    public={'ownerKind':data['ownerKind'],'ownerAddress':data['ownerAddress'],'chainId':data['chainId'],'configHash':hashlib.sha256(raw).hexdigest()}
    print(json.dumps({'valid':True,'publicCommitment':public},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
