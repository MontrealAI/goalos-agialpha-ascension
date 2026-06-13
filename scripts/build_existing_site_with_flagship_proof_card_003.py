#!/usr/bin/env python3
from pathlib import Path
import shutil, subprocess, sys
OUT=Path('site')
if not OUT.exists() or not (OUT/'index.html').exists():
    OUT.mkdir(exist_ok=True)
    if Path('app/index.html').exists(): shutil.copytree('app',OUT,dirs_exist_ok=True)
    else: (OUT/'index.html').write_text('<html><body><main><h1>GoalOS AGIALPHA Ascension</h1></main></body></html>',encoding='utf-8')
subprocess.run([sys.executable,'scripts/add_goalos_agialpha_flagship_proof_card_003_to_site.py'],check=True)
