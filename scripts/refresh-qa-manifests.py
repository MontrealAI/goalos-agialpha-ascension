#!/usr/bin/env python3
"""Refresh QA package manifests after all generated evidence is final.

The QA manifests intentionally exclude themselves because a file cannot contain
its own stable hash. This script is intended to run after docs/status/evidence
artifacts are generated so manifest entries match the committed tree.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa"
MANIFESTS = [QA / "MANIFEST.json", QA / "MANIFEST_v4_4.json", QA / "MANIFEST_MAINNET_AUTHORIZATION_v4_4_0.json"]
IGNORED_PARTS = {
    ".git",
    ".private",
    "artifacts",
    "cache",
    "coverage",
    "node_modules",
    "typechain-types",
    "__pycache__",
    "direct-solc-output",
}


def should_include(path: Path) -> bool:
    if not path.is_file():
        return False
    if path in MANIFESTS:
        return False
    rel_parts = path.relative_to(ROOT).parts
    if IGNORED_PARTS.intersection(rel_parts):
        return False
    if path.suffix == ".pyc":
        return False
    if path.relative_to(ROOT).as_posix() == "audit/reports/current-run.txt":
        return False
    if rel_parts and rel_parts[0] == "private":
        return False
    return True


def build_entries() -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for path in sorted(ROOT.rglob("*")):
        if not should_include(path):
            continue
        data = path.read_bytes()
        entries.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return entries


def refresh() -> None:
    generated_at = dt.datetime.now(dt.UTC).isoformat()
    payload = {"generated_at": generated_at, "files": build_entries()}
    QA.mkdir(exist_ok=True)
    for manifest in MANIFESTS:
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "QA_MANIFESTS_REFRESHED", "files": len(payload["files"]), "manifests": [str(p.relative_to(ROOT)) for p in MANIFESTS]}, indent=2))


def verify() -> int:
    errors: list[str] = []
    expected = {entry["path"]: entry for entry in build_entries()}
    for manifest in MANIFESTS:
        if not manifest.exists():
            errors.append(f"missing manifest: {manifest.relative_to(ROOT)}")
            continue
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        seen = {entry["path"]: entry for entry in payload.get("files", [])}
        if set(seen) != set(expected):
            missing = sorted(set(expected) - set(seen))[:20]
            extra = sorted(set(seen) - set(expected))[:20]
            errors.append(f"{manifest.relative_to(ROOT)} file-set mismatch missing={missing} extra={extra}")
        for rel, current in expected.items():
            recorded = seen.get(rel)
            if not recorded:
                continue
            if recorded.get("bytes") != current["bytes"] or recorded.get("sha256") != current["sha256"]:
                errors.append(
                    f"{manifest.relative_to(ROOT)} stale entry {rel}: "
                    f"recorded bytes={recorded.get('bytes')} sha={recorded.get('sha256')} "
                    f"actual bytes={current['bytes']} sha={current['sha256']}"
                )
                if len(errors) >= 50:
                    break
    out = {"status": "PASSED" if not errors else "FAILED", "errors": errors}
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="verify manifests instead of refreshing them")
    args = parser.parse_args()
    raise SystemExit(verify() if args.verify else (refresh() or 0))


if __name__ == "__main__":
    main()
