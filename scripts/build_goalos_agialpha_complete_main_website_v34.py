#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    src = root / 'site-assets' / 'main-website-v34'
    if not src.exists():
        raise SystemExit('Missing site-assets/main-website-v34')
    out = Path(args.site)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    (out / '.nojekyll').write_text('', encoding='utf-8')
    print('GoalOS AGIALPHA Complete Main Website v34 built:', out.resolve())

if __name__ == '__main__':
    main()
