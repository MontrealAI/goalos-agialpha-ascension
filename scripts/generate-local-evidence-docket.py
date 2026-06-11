#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
manifest=ROOT/'deployments/local.agialpha.latest.json'
out_json=ROOT/'evidence/local/EVIDENCE_DOCKET.json'
out_md=ROOT/'evidence/local/EVIDENCE_DOCKET.md'
out_json.parent.mkdir(parents=True, exist_ok=True)
def sha(p): return '0x'+hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
docket={'status':'LOCAL_SIMULATION_ONLY','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest':'deployments/local.agialpha.latest.json','manifestHash':sha(manifest),'mainnetEvidence':False,'publicSepoliaEvidence':False}
out_json.write_text(json.dumps(docket, indent=2)+'\n')
out_md.write_text(f"# Local Evidence Docket\n\nStatus: **LOCAL_SIMULATION_ONLY**\n\nManifest hash: `{docket['manifestHash']}`\n\nThis does not count as public Sepolia or Ethereum Mainnet evidence.\n")
print(json.dumps(docket, indent=2))
