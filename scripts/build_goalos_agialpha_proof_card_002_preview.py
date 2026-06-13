#!/usr/bin/env python3
from pathlib import Path
import shutil, subprocess, sys

out=Path('preview_site')
if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True)
(out/'index.html').write_text("""<!doctype html><html><head><meta charset='utf-8'><title>GoalOS AGIALPHA Ascension</title></head><body><main><h1>GoalOS AGIALPHA Ascension</h1><p>Existing premium site placeholder for local smoke test.</p></main></body></html>""",encoding='utf-8')
subprocess.check_call([sys.executable,'scripts/add_goalos_agialpha_proof_card_002_to_site.py','--site',str(out)])
subprocess.check_call([sys.executable,'scripts/verify_goalos_agialpha_proof_card_002_site.py','--site',str(out)])
print('Local preview site built and verified:', out)
