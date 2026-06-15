#!/usr/bin/env python3
from __future__ import annotations
import json, html
from pathlib import Path
from common import write_text
content=json.loads(Path('content/mission-os.page.json').read_text())
sections=''.join(f"<section class='section'><h2>{html.escape(s['title'])}</h2><p>{html.escape(s['body'])}</p></section>" for s in content['sections'])
html_doc=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>GoalOS Mission OS — The Proof OS for Autonomous AI Work</title><style>body{{margin:0;font-family:Inter,system-ui,sans-serif;background:#fbfaf7;color:#111827}}header{{padding:80px 7vw;background:radial-gradient(circle at 70% 20%,#173a77,#06101f 60%);color:white}}h1{{font:700 clamp(44px,7vw,86px)/.96 Georgia,serif}}h2{{font:700 36px Georgia,serif}}.section{{padding:42px 7vw;max-width:1120px;margin:auto}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}.card{{border:1px solid #dbe2ed;border-radius:22px;padding:24px;background:white}}a{{color:#326bff}}</style></head><body><header><p>{content['eyebrow']}</p><h1>{content['hero']}</h1><p>{content['subhero']}</p></header><main>{sections}<section class='section'><h2>Resources</h2><div class='grid'><div class='card'><a href='docs/papers/mission-os/GoalOS_Mission_OS_Paper.pdf'>Mission OS paper</a></div><div class='card'><a href='docs/papers/mission-os/GoalOS_Mission_OS_One_Page_Field_Card.pdf'>One-page field card</a></div><div class='card'><a href='docs/GOALOS_MISSION_OS_AUTONOMOUS_WEBSITE_PUBLICATION.md'>Autonomous website publication docs</a></div><div class='card'><a href='docs/GOALOS_GOVERNED_DECISION_STATE.md'>Evidence Docket docs</a></div></div></section><section class='section'><h2>Claim boundary</h2><p>No AGI/ASI/SOTA/ROI/Mainnet/production/audit claims without evidence.</p></section></main></body></html>"""
write_text(Path('mission-os.html'), html_doc)
print('mission-os.html')
