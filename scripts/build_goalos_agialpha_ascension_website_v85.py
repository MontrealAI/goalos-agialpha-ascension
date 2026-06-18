#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, json, hashlib, datetime, re
ROOT=Path(__file__).resolve().parents[1]
PUBLIC_DIRS=['assets','downloads','resources','evidence','data']
ROOT_FILES={'.nojekyll','robots.txt','sitemap.xml','manifest.webmanifest','site-status.json','routes.json'}
BLOCK={'.git','.github','.private','private','node_modules','site','scripts','docs','contracts','ignition','test','tests','cache'}
SUFFIX={'.html','.svg','.png','.jpg','.jpeg','.webp','.ico','.json','.xml','.txt','.webmanifest','.css','.js','.pdf','.xlsx','.csv'}
def bad(rel):
    return any(x in BLOCK for x in rel.parts) or rel.suffix.lower() in {'.zip','.env','.key','.pem','.p12','.pfx','.db','.sqlite','.log'}
def cp(src,dst): dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='site'); a=ap.parse_args(); out=Path(a.out).resolve()
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    copied=[]
    for p in ROOT.iterdir():
        if p.is_file() and (p.suffix.lower()=='.html' or p.name in ROOT_FILES): cp(p,out/p.name); copied.append(p.name)
    for d in PUBLIC_DIRS:
        src=ROOT/d
        if not src.exists(): continue
        for p in src.rglob('*'):
            if p.is_file():
                rel=p.relative_to(ROOT)
                if not bad(rel): cp(p,out/rel); copied.append(str(rel))
    (out/'.nojekyll').write_text('')
    pages=sorted(p.name for p in out.glob('*.html'))
    status={'release':'v85-final','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'html_pages':len(pages),'proof_cards':31,'css_inline_fallback':True,'dynamic_ai':True,'claim_boundary':'active','primary_nav':['Home','Mission OS','Ascension','Proof Cards','Proof Treasury','Paper','Resources']}
    (out/'site-status.json').write_text(json.dumps(status,indent=2))
    q=out/'qa'; q.mkdir(exist_ok=True); (q/'build-manifest-v85.json').write_text(json.dumps({'pages':pages,'copied_files':len(copied)},indent=2))
    print(f'Built GoalOS v85: {len(pages)} pages, {len(copied)} files')
if __name__=='__main__': main()
