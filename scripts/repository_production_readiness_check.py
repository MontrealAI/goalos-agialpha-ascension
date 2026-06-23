#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.release.current_mainnet_state import normalize, StateError
errors=[]; warnings=[]
required=["README.md","START_HERE.md","GITHUB_REPOSITORY_SETTINGS.md","CREATE_REPOSITORY_WEB_UI_GUIDE.md","SECURITY.md","CONTRIBUTING.md","GOVERNANCE.md","docs/REPOSITORY_STATUS.md","scripts/repository_safety_check.py","scripts/repository_status_check.py","scripts/repository_production_readiness_check.py"]
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f"Missing required file: {rel}")
policy_check=subprocess.run([sys.executable,"scripts/validate_workflow_policy.py"],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if policy_check.returncode: errors.append("Workflow policy validation failed: "+policy_check.stdout.strip())
try: state=normalize()
except StateError as exc: errors.append(str(exc)); state={}
readme=(ROOT/'README.md').read_text(encoding='utf-8',errors='ignore') if (ROOT/'README.md').exists() else ''
for phrase in ["GoalOS AGIALPHA Ascension","0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA","Ethereum Mainnet deployment | PASS — YES","Mainnet configuration | PASS — YES","Independent live revalidation | PENDING_EXTERNAL_INPUT","Production activation | NOT_ACTIVATED","User-fund authorization | NO"]:
    if phrase.lower() not in readme.lower(): errors.append(f"README missing required phrase: {phrase}")
if state and state.get('statuses',{}).get('productionActivation')!='NOT_ACTIVATED': errors.append('production activation must remain NOT_ACTIVATED')
if state and state.get('statuses',{}).get('userFundAuthorization')!='NO': errors.append('user-fund authorization must remain NO')
pkg=json.loads((ROOT/'package.json').read_text()) if (ROOT/'package.json').exists() else {}
for script in ['repo:safety','repo:status','repo:production-readiness','repo:all','mainnet:release-state:check','mainnet:postdeploy:operator-evidence:validate']:
    if script not in pkg.get('scripts',{}): errors.append(f'package.json missing script: {script}')
print(json.dumps({'status':'passed' if not errors else 'failed','errors':errors,'warnings':warnings,'message':'Repository/release continuity checks passed.' if not errors else 'Fix errors before release continuity.'},indent=2))
if errors: sys.exit(1)
