#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

def extract_inline_builder(workflow: Path, out_py: Path) -> bool:
    if not workflow.exists(): return False
    text=workflow.read_text(encoding='utf-8',errors='replace')
    idx=text.find("python3 - <<'PY'"); marker="python3 - <<'PY'"
    if idx<0:
        idx=text.find('python3 - <<"PY"'); marker='python3 - <<"PY"'
    if idx<0: return False
    lines=text[idx+len(marker):].splitlines(); buf=[]
    for line in lines:
        if line.strip()=='PY': break
        if line.startswith('          '): line=line[10:]
        buf.append(line)
    code='\n'.join(buf).strip('\n')
    if 'OUT = Path("site")' not in code and "OUT = Path('site')" not in code: return False
    out_py.write_text(code,encoding='utf-8'); return True

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='site'); args=ap.parse_args(); site=Path(args.out)
    candidates=[['python3','scripts/build_premium_autonomous_website.py','--out',args.out],['python3','scripts/build_premium_website.py','--out',args.out],['python3','scripts/build_site.py','--out',args.out]]
    built=False
    for cmd in candidates:
        if Path(cmd[1]).exists():
            res=subprocess.run(cmd,text=True)
            if res.returncode!=0: sys.exit(res.returncode)
            built=True; break
    if not built:
        tmp=Path('.tmp_existing_site_builder.py')
        if not extract_inline_builder(Path('.github/workflows/autonomous-github-pages.yml'),tmp): raise SystemExit('Could not find existing site builder. Refusing fallback to prevent site loss.')
        res=subprocess.run(['python3',str(tmp)],text=True)
        if res.returncode!=0: sys.exit(res.returncode)
    if not site.exists(): raise SystemExit(f'Expected {site} after build.')
    res=subprocess.run(['python3','scripts/add_goalos_agialpha_proof_card_001_to_site.py','--site',str(site)],text=True)
    if res.returncode!=0: sys.exit(res.returncode)
if __name__=='__main__': main()
