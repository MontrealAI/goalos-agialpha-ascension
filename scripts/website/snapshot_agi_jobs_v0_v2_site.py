#!/usr/bin/env python3
"""Capture a pre-feature inventory for additive AGI Jobs v0 (v2) preservation checks."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    site = args.site.resolve()
    output = args.output.resolve()
    if not site.is_dir():
        raise SystemExit(f"Site directory does not exist: {site}")
    files = {}
    for path in sorted(item for item in site.rglob("*") if item.is_file()):
        if path.resolve() == output:
            continue
        relative = path.relative_to(site).as_posix()
        files[relative] = {"sha256": digest(path), "bytes": path.stat().st_size}
    payload = {
        "schema": "goalos.agi_jobs_v0_v2.prebuild_snapshot.v1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "site": str(site),
        "file_count": len(files),
        "files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "file_count": len(files), "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
