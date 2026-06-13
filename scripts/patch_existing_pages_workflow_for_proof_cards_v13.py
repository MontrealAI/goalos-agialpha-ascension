#!/usr/bin/env python3
from pathlib import Path
src=Path('.github/workflows/autonomous-github-pages.yml')
if not src.exists(): raise SystemExit('No autonomous-github-pages.yml found.')
text=src.read_text(encoding='utf-8')
text=text.replace('proof-card-005','proof-card-007').replace('Proof Cards 001-005','Proof Cards 001-007').replace('proof-card-006','proof-card-007')
text=text.replace('add_goalos_agialpha_main_site_proof_cards_v12.py','add_goalos_agialpha_main_site_proof_cards_v13.py')
text=text.replace('verify_goalos_agialpha_main_site_proof_cards_v12.py','verify_goalos_agialpha_main_site_proof_cards_v13.py')
text=text.replace('add_goalos_agialpha_main_site_proof_cards_v11.py','add_goalos_agialpha_main_site_proof_cards_v13.py')
text=text.replace('verify_goalos_agialpha_main_site_proof_cards_v11.py','verify_goalos_agialpha_main_site_proof_cards_v13.py')
src.write_text(text, encoding='utf-8')
print('Patched workflow references to Proof Cards 001-007.')
