#!/usr/bin/env python3
"""Snapshot the generated GoalOS website before adding SME Kernel v3."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def digest(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main()->int:
 root=Path(__file__).resolve().parents[2];parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--site',type=Path,default=root/'site');parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();site=args.site.resolve();output=args.output.resolve()
 if not site.is_dir():raise SystemExit(f'Missing site: {site}')
 files={p.relative_to(site).as_posix():{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(x for x in site.rglob('*') if x.is_file())}
 payload={'schema':'goalos.sme.kernel.v3.prebuild_snapshot.v1','site':str(site),'file_count':len(files),'files':files};output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','files':len(files),'output':str(output)},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
