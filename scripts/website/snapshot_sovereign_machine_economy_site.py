#!/usr/bin/env python3
"""Snapshot a generated GoalOS site before Sovereign Machine Economy integration."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    site = args.site.resolve()
    if not site.is_dir(): raise RuntimeError(f'missing site: {site}')
    files = {path.relative_to(site).as_posix(): {'sha256':sha(path),'bytes':path.stat().st_size} for path in sorted(site.rglob('*')) if path.is_file()}
    payload = {'schema':'goalos.sovereign_machine_economy.site_snapshot.v1','site':str(site),'file_count':len(files),'files':files}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status':'PASS','file_count':len(files),'output':str(args.output)}, indent=2))
    return 0

if __name__ == '__main__': raise SystemExit(main())
