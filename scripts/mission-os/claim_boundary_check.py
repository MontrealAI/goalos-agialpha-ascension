#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from common import artifact_files, load_policy, scan_forbidden_claims, write_text, utc_now


def resolve_path(args: argparse.Namespace) -> Path:
    path = args.dir or args.path
    if path is None:
        raise SystemExit("Provide mission artifact directory as positional PATH or --dir PATH.")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="GoalOS Mission OS claim-boundary checker")
    parser.add_argument("path", type=Path, nargs="?", help="Mission artifact directory")
    parser.add_argument("--dir", type=Path, help="Mission artifact directory")
    parser.add_argument("--policy", type=Path, default=Path("config/goalos-mission-os.policy.json"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    out_dir = resolve_path(args)
    policy = load_policy(args.policy)
    ok, findings = scan_forbidden_claims(artifact_files(out_dir), policy.get("forbiddenClaims", []))
    result = {"passed": ok, "checked_at": utc_now(), "findings": findings}
    report = out_dir / "ClaimBoundaryReport.md"
    write_text(report, f"""
# Claim Boundary Report

**Status:** {'PASS' if ok else 'FAIL'}  
**Generated:** {result['checked_at']}

## Findings
```json
{json.dumps(findings, indent=2, sort_keys=True)}
```

## Rule
No public claim promotion without an Evidence Docket and human review.
""")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif ok:
        print(f"Claim-boundary check passed: {out_dir}")
    else:
        print(f"Claim-boundary check failed: {findings}", file=sys.stderr)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
