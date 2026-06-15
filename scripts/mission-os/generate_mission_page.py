#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from common import html_page, write_text
c=json.loads(Path('content/mission-os.page.json').read_text())
body='''<section><div class="eyebrow">The Proof OS for Autonomous AI Work</div><h2>GoalOS Mission OS</h2><p>Set the objective. GoalOS runs until proof is done.</p><div class="rule">AI creates output. GoalOS creates proof. The deliverable is not a document. The deliverable is a governed decision state.</div></section><section class="grid"><div class="card"><h3>Beyond research</h3><p>Mission OS turns objectives into Evidence Dockets, verifier reports, risk ledgers, action graphs, and Chronicle memory.</p></div><div class="card"><h3>AGIALPHA settlement readiness</h3><p>$AGIALPHA is not the product. Verified work is the product. $AGIALPHA is proof-settlement fuel.</p></div><div class="card"><h3>Resources</h3><p><a href="docs/papers/mission-os/GoalOS_Mission_OS_Paper.pdf">Mission OS paper</a> · <a href="docs/papers/mission-os/GoalOS_Mission_OS_One_Page_Field_Card.pdf">One-page field card</a></p></div></section>'''
write_text(Path('mission-os.html'), html_page(c.get('title','GoalOS Mission OS'), body))
print('generated mission-os.html')
