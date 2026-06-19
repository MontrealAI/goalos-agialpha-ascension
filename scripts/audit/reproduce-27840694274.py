#!/usr/bin/env python3
import json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
cmds=['audit:reset','audit:npm','audit:osv','audit:summarize','audit:fail-on-critical']
results=[]
for c in cmds:
    p=subprocess.run(['npm','run',c],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    results.append({'command':'npm run '+c,'exitCode':p.returncode,'tail':p.stdout[-2000:]})
print(json.dumps({'runId':27840694274,'results':results},indent=2))
sys.exit(results[-1]['exitCode'])
