#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='site')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    src = root / 'site-assets' / 'main-website-v40'
    out = Path(args.out)
    if not src.exists():
        raise SystemExit('Missing site-assets/main-website-v40')
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    (out / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Built GoalOS AGIALPHA final WOW website v40 into {out}')

if __name__ == '__main__':
    main()
