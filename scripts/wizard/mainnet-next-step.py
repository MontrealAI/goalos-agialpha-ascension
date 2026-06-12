#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
def j(p):
    try: return json.loads((ROOT/p).read_text())
    except Exception: return {}
cert=j('qa/mainnet-authorization-certificate.json')
if cert.get('ethereumMainnetAuthorized')=='YES':
    print('Next action: A. Public repo authorized. Founder/deployer may run npm run deploy:ethereum-mainnet:gated with local runtime RPC/key.')
elif cert.get('blockers'):
    print('Next action: B. Blocked, with exact blockers:')
    [print(f'- {b}') for b in cert['blockers']]
else:
    print('Next action: run npm run mainnet:public-authorize && npm run docs:status.')
