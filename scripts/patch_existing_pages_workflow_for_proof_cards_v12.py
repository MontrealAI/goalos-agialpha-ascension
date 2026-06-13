#!/usr/bin/env python3
from pathlib import Path
import re

wf = Path('.github/workflows/autonomous-github-pages.yml')
if not wf.exists():
    raise SystemExit('autonomous-github-pages.yml not found')
text = wf.read_text(encoding='utf-8')
needle = '      - ".github/workflows/autonomous-github-pages.yml"\n'
add = (
    '      - "scripts/add_goalos_agialpha_main_site_proof_cards_v12.py"\n'
    '      - "scripts/verify_goalos_agialpha_main_site_proof_cards_v12.py"\n'
    '      - "docs/examples/**"\n'
    '      - "data/examples/**"\n'
    '      - "evidence/examples/**"\n'
)
if 'add_goalos_agialpha_main_site_proof_cards_v12.py' not in text and needle in text:
    text = text.replace(needle, add + needle)

# Remove older add/verify proof-card steps if a previous patch inserted them.
text = re.sub(
    r'\n\s+- name: Add Proof Cards 001-\d+.*?\n\s+run: python3 scripts/add_goalos_agialpha_main_site_proof_cards_v\d+\.py --site site\n\s+- name: Verify main website.*?\n\s+run: python3 scripts/verify_goalos_agialpha_main_site_proof_cards_v\d+\.py --site site\n',
    '\n',
    text,
    flags=re.S,
)
insert = (
    '\n      - name: Add Proof Cards 001-006 to the main website\n'
    '        shell: bash\n'
    '        run: python3 scripts/add_goalos_agialpha_main_site_proof_cards_v12.py --site site\n\n'
    '      - name: Verify main website and Proof Cards 001-006\n'
    '        shell: bash\n'
    '        run: python3 scripts/verify_goalos_agialpha_main_site_proof_cards_v12.py --site site\n'
)
marker = '      - name: Validate generated website artifact\n'
if 'Add Proof Cards 001-006 to the main website' not in text:
    if marker not in text:
        raise SystemExit('validate step marker not found')
    text = text.replace(marker, insert + '\n' + marker)
wf.write_text(text, encoding='utf-8')
print('Patched autonomous GitHub Pages workflow for Proof Cards 001-006.')
