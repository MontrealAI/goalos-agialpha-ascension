#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--site',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();site=a.site.resolve()
 files={str(p.relative_to(site)).replace('\\','/'):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(site.rglob('*')) if p.is_file()}
 payload={'schema':'goalos.sovereign_machine_economy.site_snapshot.v1','site':str(site),'file_count':len(files),'files':files}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','file_count':len(files),'output':str(a.output)},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
