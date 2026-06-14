#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, re
PAGES=[f"proof-card-{i:03d}.html" for i in range(1,16)]+["proof-cards.html","agialpha-ledger-route.html","sovereign-rsi-control-plane.html","evidence-docket.html"]
COMMAND_CENTER_CSS="""<style id="proof-card-atlas-v29-style">.proof-card-command-center{margin:48px auto;padding:34px;max-width:1180px;border-radius:30px;background:linear-gradient(135deg,#07172d,#0e2748);color:#fff;box-shadow:0 26px 90px rgba(7,23,45,.18)}.proof-card-command-center h2{font-size:clamp(2rem,4vw,4rem);line-height:1;margin:0 0 14px;letter-spacing:-.05em;color:#fff}.proof-card-command-center p{font-size:1.05rem;color:#e6f0ff}.proof-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:22px}.proof-card-grid a{display:block;background:#fff;color:#07172d;border:1px solid #e3dccf;border-radius:18px;padding:16px;text-decoration:none;box-shadow:0 10px 30px rgba(0,0,0,.10)}.proof-card-grid b{display:block;margin-bottom:6px}.proof-card-grid span{display:inline-block;margin-bottom:8px;background:#eef7f8;color:#0a5570;border:1px solid #cbe8ee;border-radius:999px;padding:3px 8px;font-size:.75rem;font-weight:900}</style>"""
def command_center_block():
    links=''.join(f"<a href='proof-card-{i:03d}.html'><span>Proof Card {i:03d}</span><b>Open stable page</b><small>Substantial public-safe proof dossier</small></a>" for i in range(1,16))
    return f"""{COMMAND_CENTER_CSS}<section class="proof-card-command-center" id="proof-card-command-center"><h2>Proof Card Command Center</h2><p>Proof Cards 001–015 are stable public-safe micro-dossiers connected to the main website root. Each card explains AGIALPHA usage, smart-contract routes, Evidence Dockets, RSI upgrade logic, and bounded claim discipline.</p><p><a style="color:#f1cc74;font-weight:900" href="proof-cards.html">Open the full Proof Card Atlas →</a></p><div class="proof-card-grid">{links}</div></section>"""
def inject_homepage(index_path:Path):
    if index_path.exists(): txt=index_path.read_text(encoding='utf-8',errors='replace')
    else: txt="<!doctype html><html><head><meta charset='utf-8'><title>GoalOS AGIALPHA Ascension</title></head><body><main></main></body></html>"
    txt=re.sub(r'<style id="proof-card-atlas-v\d+-style">.*?</section>','',txt,flags=re.S)
    block=command_center_block()
    if '</main>' in txt: txt=txt.replace('</main>',block+'\n</main>')
    elif '</body>' in txt: txt=txt.replace('</body>',block+'\n</body>')
    else: txt+=block
    index_path.write_text(txt,encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); args=ap.parse_args(); site=Path(args.site); site.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1]; src_dir=root/'site-assets'/'proof-pages'
    if not src_dir.exists(): raise SystemExit('Missing site-assets/proof-pages')
    for name in PAGES:
        src=src_dir/name
        if not src.exists(): raise SystemExit(f'Missing static proof page: {name}')
        shutil.copy2(src, site/name)
    inject_homepage(site/'index.html')
    print('Proof Cards 001-015 integrated into canonical main website root.')
if __name__=='__main__': main()
