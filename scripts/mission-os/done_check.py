#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
from common import artifact_files, load_policy, write_json, utc_now


def compute_done(out_dir: Path, policy: dict) -> dict:
    present = {p.name for p in artifact_files(out_dir)}
    missing = [x for x in policy.get("requiredArtifacts", []) if x not in present]
    claim_report = out_dir / "ClaimBoundaryReport.md"
    qa_report = out_dir / "QAReport.md"
    claim_pass = claim_report.exists() and "**Status:** PASS" in claim_report.read_text(encoding="utf-8", errors="ignore")
    qa_pass = qa_report.exists() and "**Status:** PASS" in qa_report.read_text(encoding="utf-8", errors="ignore")
    done = not missing and claim_pass and qa_pass
    return {
        "checked_at": utc_now(),
        "done": done,
        "missing": missing,
        "gates": {
            "required_artifacts": not missing,
            "claim_boundary_passed": claim_pass,
            "qa_passed": qa_pass,
            "human_review_ready": done,
            "no_auto_merge": True,
            "no_mainnet_broadcast": True,
            "no_token_movement": True,
        },
    }


def resolve_path(args: argparse.Namespace) -> Path:
    path = args.dir or args.path
    if path is None:
        raise SystemExit("Provide mission artifact directory as positional PATH or --dir PATH.")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="GoalOS Mission OS DONE checker")
    parser.add_argument("path", type=Path, nargs="?", help="Mission artifact directory")
    parser.add_argument("--dir", type=Path, help="Mission artifact directory")
    parser.add_argument("--policy", type=Path, default=Path("config/goalos-mission-os.policy.json"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    out_dir = resolve_path(args)
    policy = load_policy(args.policy)
    result = compute_done(out_dir, policy)
    write_json(out_dir / "done-check.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["done"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
