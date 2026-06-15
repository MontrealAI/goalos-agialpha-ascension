#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

CANONICAL_LINES = [
    "GoalOS Mission OS",
    "Set the objective. GoalOS runs until proof is done.",
    "AI creates output. GoalOS creates proof.",
    "The deliverable is not a document. The deliverable is a governed decision state.",
    "No proof, no settlement. No eval, no propagation. No rollback, no release.",
]

DEFAULT_POLICY_PATH = Path("config/goalos-mission-os.policy.json")
DEFAULT_SCHEMA_PATH = Path("schemas/goalos-mission-os-intake.schema.json")

SECRET_PATTERNS = [
    re.compile(r"0x[a-fA-F0-9]{64}"),
    re.compile(r"(?i)(api[_-]?key|private[_-]?key|secret|private[_-]?token|mnemonic|seed[_-]?phrase)\s*[:=]\s*[^\s`]+"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/=-]{16,}"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-._")
    return value or "mission"


def load_policy(path: Path | None = None) -> Dict[str, Any]:
    path = path or DEFAULT_POLICY_PATH
    return read_json(path)


def validate_mission(mission: Dict[str, Any]) -> List[str]:
    required = [
        "mission_id", "mission_title", "objective", "decision_to_support", "success_criteria",
        "failure_criteria", "constraints", "allowed_sources", "private_data_boundary",
        "risk_class", "deadline", "output_package", "reviewer_required",
        "claim_boundary", "done_condition", "ethereum_settlement_mode", "ethereum_network", "agialpha_token_address",
    ]
    errors: List[str] = []
    for key in required:
        if key not in mission:
            errors.append(f"missing required field: {key}")
    if "mission_id" in mission and not re.match(r"^[a-z0-9][a-z0-9._-]{2,96}$", str(mission["mission_id"])):
        errors.append("mission_id must be lowercase slug-like text")
    for key in ["success_criteria", "failure_criteria", "allowed_sources", "output_package", "claim_boundary", "done_condition"]:
        if key in mission and (not isinstance(mission[key], list) or not mission[key]):
            errors.append(f"{key} must be a non-empty list")
    if mission.get("risk_class") not in {"low", "medium", "high", "strategic"}:
        errors.append("risk_class must be low, medium, high, or strategic")
    if not isinstance(mission.get("reviewer_required"), bool):
        errors.append("reviewer_required must be boolean")
    if mission.get("ethereum_settlement_mode") not in {"none", "simulation", "sepolia", "mainnet-readiness", "mainnet-local-only-after-human-gate"}:
        errors.append("ethereum_settlement_mode must be none, simulation, sepolia, mainnet-readiness, or mainnet-local-only-after-human-gate")
    if mission.get("requires_mainnet_broadcast") is True or mission.get("requires_token_movement") is True:
        errors.append("Mission OS cannot request Mainnet broadcast or token movement from automation; use local operator docs.")
    return errors


def scan_forbidden_claims(paths: Iterable[Path], forbidden: Iterable[str]) -> Tuple[bool, List[Dict[str, str]]]:
    findings: List[Dict[str, str]] = []
    terms = [str(x).lower() for x in forbidden]
    ignored_names = {"ClaimBoundaryReport.md", "QAReport.md", "done-check.json", "run-state.json"}
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        if path.name in ignored_names:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        low = text.lower()
        for term in terms:
            if not term:
                continue
            start = 0
            while True:
                idx = low.find(term, start)
                if idx < 0:
                    break
                context_before = low[max(0, idx-90):idx]
                context_after = low[idx:idx+90]
                negated = any(marker in context_before for marker in ["no ", "not ", "does not", "do not", "without ", "never ", "blocked ", "forbidden ", "failure criteria", "claim boundary", "does not claim"])
                descriptive = any(marker in context_after for marker in [" framing", " boundary", " claim", " class", " classes", " checklist", " is blocked"])
                if not (negated or descriptive):
                    findings.append({"file": str(path), "term": term})
                    break
                start = idx + len(term)
    return (len(findings) == 0, findings)


def scan_secrets(paths: Iterable[Path]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    ignored_names = {"ClaimBoundaryReport.md", "QAReport.md", "done-check.json", "run-state.json"}
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        if path.name in ignored_names:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                findings.append({"file": str(path), "pattern": pat.pattern})
    return findings


def mission_claims(mission: Dict[str, Any]) -> List[Dict[str, str]]:
    title = mission["mission_title"]
    decision = mission["decision_to_support"]
    return [
        {
            "claim_id": "C-001",
            "claim": f"Mission objective is defined: {title}",
            "evidence_required": "GoalOSCommit and RunCommitment",
            "status": "supported",
            "boundary": "Objective definition only; no outcome claim.",
        },
        {
            "claim_id": "C-002",
            "claim": f"Decision to support is explicit: {decision}",
            "evidence_required": "Mission plan, claims matrix, source provenance, verifier report",
            "status": "supported",
            "boundary": "Decision support only; not legal, financial, medical, or guaranteed advice.",
        },
        {
            "claim_id": "C-003",
            "claim": "Evidence Docket and verifier workflow are required before publication.",
            "evidence_required": "EvidenceDocket, VerifierReport, ClaimBoundaryReport, QAReport",
            "status": "required",
            "boundary": "No public claim promotion without human review.",
        },
    ]


def artifact_files(out_dir: Path) -> List[Path]:
    return [p for p in out_dir.rglob("*") if p.is_file()]


def html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{ --navy:#07111f; --ink:#111827; --muted:#5b6472; --blue:#356dff; --gold:#d6a94f; --line:#d9e0ea; --card:#ffffff; --bg:#f7f8fb; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; color:var(--ink); background:var(--bg); }}
    header {{ padding:56px 7vw 48px; color:white; background: radial-gradient(circle at 70% 20%, #183a77 0, #07111f 48%, #040914 100%); }}
    .brand {{ font-family: Georgia, serif; font-size:30px; letter-spacing:-.02em; }}
    h1 {{ font-family: Georgia, serif; max-width:900px; font-size: clamp(44px, 7vw, 82px); line-height:.96; margin:70px 0 24px; }}
    .subtitle {{ max-width:760px; font-size:20px; line-height:1.55; color:#d7dfec; }}
    .chips {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:28px; }}
    .chip {{ border:1px solid rgba(255,255,255,.22); padding:10px 14px; border-radius:999px; color:#eef3ff; background:rgba(255,255,255,.07); }}
    main {{ padding:56px 7vw; }}
    section {{ max-width:1120px; margin:0 auto 34px; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(250px,1fr)); gap:18px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:22px; padding:24px; box-shadow:0 8px 24px rgba(10,20,35,.04); }}
    .eyebrow {{ color:var(--blue); font-weight:700; text-transform:uppercase; letter-spacing:.14em; font-size:12px; }}
    h2 {{ font-family: Georgia, serif; font-size:36px; margin:12px 0 18px; }}
    h3 {{ margin:0 0 10px; font-size:20px; }}
    p, li {{ line-height:1.62; color:var(--muted); }}
    table {{ width:100%; border-collapse:collapse; background:white; border-radius:18px; overflow:hidden; border:1px solid var(--line); }}
    th, td {{ text-align:left; padding:13px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
    th {{ background:#0a1424; color:#fff; }}
    code {{ background:#eef3ff; padding:2px 6px; border-radius:6px; }}
    .rule {{ background:#06101f; color:#fff; border-left:5px solid var(--gold); padding:18px 22px; border-radius:16px; font-weight:700; }}
    footer {{ text-align:center; padding:34px; color:var(--muted); }}
  </style>
</head>
<body>
<header>
  <div class=\"brand\">GoalOS</div>
  <h1>Set the objective. GoalOS runs until proof is done.</h1>
  <p class=\"subtitle\">GoalOS Mission OS turns high-stakes objectives into governed decision states: Evidence Dockets, verifier reports, risk ledgers, action graphs, Chronicle memory, and reusable capability.</p>
  <div class=\"chips\"><span class=\"chip\">Runs until DONE</span><span class=\"chip\">Proof-backed outputs</span><span class=\"chip\">Human-governed publication</span></div>
</header>
<main>{body}</main>
<footer>AI creates output. GoalOS creates proof. No proof, no propagation.</footer>
</body>
</html>"""
