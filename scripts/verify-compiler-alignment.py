#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
errors=[]
pkg=json.loads((ROOT/'package.json').read_text())
solc_pkg=(pkg.get('dependencies',{}).get('solc') or pkg.get('devDependencies',{}).get('solc') or '').lstrip('^~')
hardhat=(ROOT/'hardhat.config.ts').read_text()
m=re.search(r'version:\s*["\']([^"\']+)', hardhat)
hardhat_solc=m.group(1) if m else None
if not solc_pkg: errors.append('package.json must pin solc.')
if not hardhat_solc: errors.append('hardhat.config.ts must declare one Solidity compiler version.')
if solc_pkg and hardhat_solc and not solc_pkg.startswith(hardhat_solc): errors.append(f'Compiler mismatch: hardhat.config.ts uses {hardhat_solc}; package.json solc is {solc_pkg}.')
pragma_versions=set()
for f in (ROOT/'contracts').rglob('*.sol'):
    txt=f.read_text(errors='ignore')
    mm=re.search(r'pragma\s+solidity\s+([^;]+);', txt)
    if mm: pragma_versions.add(mm.group(1).strip())
try:
    out=subprocess.check_output(['node','-e','console.log(require("solc").version())'],cwd=ROOT,text=True).strip()
except Exception as e:
    errors.append(f'Unable to load local solc-js: {e}'); out='UNKNOWN'
policy=ROOT/'docs/DETERMINISTIC_SOLIDITY_COMPILER_POLICY.md'
if not policy.exists(): errors.append('Missing docs/DETERMINISTIC_SOLIDITY_COMPILER_POLICY.md')
result={'status':'PASSED' if not errors else 'FAILED','hardhatSolidityVersion':hardhat_solc,'packageSolc':solc_pkg,'runtimeSolcVersion':out,'pragmaConstraints':sorted(pragma_versions),'errors':errors}
(ROOT/'qa').mkdir(exist_ok=True)
(ROOT/'qa/compiler-alignment.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if errors: sys.exit(1)
