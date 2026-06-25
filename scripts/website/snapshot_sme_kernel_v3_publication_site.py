#!/usr/bin/env python3
"""Snapshot a generated GoalOS site before the Kernel v3 publication layer is added."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "goalos.sme_kernel_v3.institutional_publication.prebuild_snapshot.v1"


def digest(path: Path) -> str:
  value = hashlib.sha256()
  with path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
      value.update(chunk)
  return value.hexdigest()


def main() -> int:
  root = Path(__file__).resolve().parents[2]
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--site", type=Path, default=root / "site")
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()
  site = args.site.resolve()
  output = args.output.resolve()
  if not site.is_dir():
    raise SystemExit(f"Missing generated site: {site}")
  files = {
    path.relative_to(site).as_posix(): {"sha256": digest(path), "bytes": path.stat().st_size}
    for path in sorted(item for item in site.rglob("*") if item.is_file())
  }
  payload = {"schema": SCHEMA, "site": str(site), "file_count": len(files), "files": files}
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  print(json.dumps({"status": "PASS", "files": len(files), "output": str(output)}, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
