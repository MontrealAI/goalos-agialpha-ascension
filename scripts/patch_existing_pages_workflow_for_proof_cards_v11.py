#!/usr/bin/env python3
from pathlib import Path
import re
wf = Path('.github/workflows/autonomous-github-pages.yml')
if not wf.exists():
    raise SystemExit('ERROR: .github/workflows/autonomous-github-pages.yml not found')
text = wf.read_text(encoding='utf-8')
# Remove older add/verify steps if present.
patterns = [
    r"\n\s*- name: Add Proof Cards 001-004 to the existing main website\n(?:\s+.*\n){0,5}",
    r"\n\s*- name: Verify main website and Proof Cards 001-004\n(?:\s+.*\n){0,5}",
    r"\n\s*- name: Add Proof Cards 001-005 to the existing main website\n(?:\s+.*\n){0,5}",
    r"\n\s*- name: Verify main website and Proof Cards 001-005\n(?:\s+.*\n){0,5}",
]
for pat in patterns:
    text = re.sub(pat, '\n', text)
if 'add_goalos_agialpha_main_site_proof_cards_v11.py' not in text:
    needle = '      - name: Validate generated website artifact\n'
    insert = """      - name: Add Proof Cards 001-005 to the existing main website
        shell: bash
        run: python3 scripts/add_goalos_agialpha_main_site_proof_cards_v11.py --site site

      - name: Verify main website and Proof Cards 001-005
        shell: bash
        run: python3 scripts/verify_goalos_agialpha_main_site_proof_cards_v11.py --site site

"""
    if needle not in text:
        raise SystemExit('ERROR: could not find validation step. Add the proof-card steps manually before Upload GitHub Pages artifact.')
    text = text.replace(needle, insert + needle, 1)
wf.write_text(text, encoding='utf-8')
print('Patched autonomous-github-pages.yml to add Proof Cards 001-005 to the existing main website.')
