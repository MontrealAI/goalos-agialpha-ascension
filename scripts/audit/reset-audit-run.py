#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, json, os, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
reports=ROOT/'audit'/'reports'; reports.mkdir(parents=True, exist_ok=True)
for name in ['current-run.txt','latest.txt']:
    try: (reports/name).unlink()
    except FileNotFoundError: pass
run=reports/(dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d-%H%M%S')+'-'+subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=ROOT,text=True).strip())
run.mkdir()
rel=run.relative_to(ROOT)
(reports/'current-run.txt').write_text(str(rel)+'\n')
(reports/'latest.txt').write_text(str(rel)+'\n')
manifest={'schemaVersion':'2.0','sourceSha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'node':subprocess.getoutput('node -v'),'npm':subprocess.getoutput('npm -v'),'python':subprocess.getoutput('python --version'),'runDirectory':str(rel),'generatedAt':dt.datetime.now(dt.timezone.utc).isoformat()}
(run/'run-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(rel)
