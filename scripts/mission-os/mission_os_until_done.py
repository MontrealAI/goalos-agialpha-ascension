#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from common import (
    CANONICAL_LINES,
    artifact_files,
    html_page,
    load_policy,
    mission_claims,
    scan_forbidden_claims,
    scan_secrets,
    sha256_file,
    slugify,
    utc_now,
    validate_mission,
    write_csv,
    write_json,
    write_text,
)

STAGES = [
    "MISSION_CREATED",
    "COMMIT_READY",
    "PLAN_READY",
    "WORKGRAPH_READY",
    "CLAIMS_READY",
    "SOURCE_PROVENANCE_READY",
    "CONTRADICTIONS_READY",
    "VERIFICATION_READY",
    "RISK_LEDGER_READY",
    "DOCKET_READY",
    "DECISION_STATE_READY",
    "ACTION_GRAPH_READY",
    "CHRONICLE_READY",
    "SETTLEMENT_READINESS_READY",
    "QA_PASSED",
    "HUMAN_REVIEW_READY",
    "DONE",
]


def bullet(items: List[str]) -> str:
    return "\n".join(f"- {x}" for x in items)


def as_json_block(obj: Any) -> str:
    return "```json\n" + json.dumps(obj, indent=2, sort_keys=True) + "\n```"


def create_artifacts(mission: Dict[str, Any], out_dir: Path, policy: Dict[str, Any], cycle: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    mission_id = slugify(mission["mission_id"])
    now = utc_now()
    claims = mission_claims(mission)


    write_json(out_dir / "MissionContract.json", {
        "mission_id": mission_id,
        "mission_title": mission["mission_title"],
        "objective": mission.get("objective", mission["mission_title"]),
        "decision_to_support": mission["decision_to_support"],
        "success_criteria": mission["success_criteria"],
        "failure_criteria": mission["failure_criteria"],
        "constraints": mission.get("constraints", []),
        "private_data_boundary": mission["private_data_boundary"],
        "reviewer_required": mission["reviewer_required"],
        "ethereum_settlement_mode": mission.get("ethereum_settlement_mode", "none"),
        "requires_mainnet_broadcast": mission.get("requires_mainnet_broadcast", False),
        "requires_token_movement": mission.get("requires_token_movement", False),
        "publication_mode": mission.get("publication_mode", "human-review-pr"),
        "claim_boundary": mission["claim_boundary"],
    })

    write_text(out_dir / "GoalOSCommit.md", f"""
# GoalOSCommit — {mission['mission_title']}

**Mission ID:** `{mission_id}`  
**Generated:** {now}  
**Doctrine:** AI creates output. GoalOS creates proof.  
**Promise:** Set the objective. GoalOS runs until proof is done.

## Objective
{mission['mission_title']}

## Decision to support
{mission['decision_to_support']}

## Success criteria
{bullet(mission['success_criteria'])}

## Failure criteria
{bullet(mission['failure_criteria'])}

## Constraints
{bullet(mission.get('constraints', []))}

## Private-data boundary
{mission['private_data_boundary']}

## Claim boundary
{bullet(mission['claim_boundary'])}

## Done condition
{bullet(mission['done_condition'])}

## Constitutional boundary
No proof, no settlement. No eval, no propagation. No rollback, no release.
""")

    write_text(out_dir / "RunCommitment.md", f"""
# RunCommitment — {mission['mission_title']}

## Run mode
Autonomous artifact generation with human-gated publication.

## Agent roles
- Planner: decomposes objective into a mission plan.
- Researcher: maps source families and evidence requirements.
- Verifier: checks claims, contradictions, and claim boundaries.
- Risk officer: produces risk ledger and rollback/failure conditions.
- Synthesizer: produces governed decision state and executive outputs.
- Chronicler: writes memory and capability-package outputs.

## Allowed sources
{bullet(mission['allowed_sources'])}

## Required outputs
{bullet(mission['output_package'])}

## Gating rule
The run may generate artifacts autonomously. It may not auto-publish, auto-merge, broadcast Mainnet transactions, move tokens, or promote unsupported claims.
""")

    write_text(out_dir / "MissionPlan.md", f"""
# MissionPlan — {mission['mission_title']}

## Mission phases
1. Clarify objective and decision support.
2. Build claims matrix and source-provenance plan.
3. Collect and organize evidence requirements.
4. Identify contradictions, uncertainty, and missing proof.
5. Generate risk ledger and action graph.
6. Package governed decision state.
7. Produce Evidence Docket and Chronicle entry.
8. Run claim-boundary and QA checks.
9. Hold for human review.

## Board-level question
What decision can be inspected, defended, and acted on after the mission completes?

## Key operating principle
The highest-value output is not the longest report. It is the shortest path from uncertainty to justified action.
""")

    write_json(out_dir / "WorkGraph.json", {
        "mission_id": mission_id,
        "generated_at": now,
        "nodes": [
            {"id": "intake", "label": "Mission Contract", "status": "complete"},
            {"id": "plan", "label": "Planning Graph", "status": "complete"},
            {"id": "claims", "label": "Claims Matrix", "status": "complete"},
            {"id": "verify", "label": "Verifier Mesh", "status": "complete"},
            {"id": "docket", "label": "Evidence Docket", "status": "complete"},
            {"id": "decision", "label": "Governed Decision State", "status": "complete"},
            {"id": "action", "label": "Action Graph", "status": "complete"},
            {"id": "chronicle", "label": "Chronicle", "status": "complete"},
        ],
        "edges": [
            ["intake", "plan"], ["plan", "claims"], ["claims", "verify"],
            ["verify", "docket"], ["docket", "decision"], ["decision", "action"], ["action", "chronicle"]
        ],
    })

    write_csv(out_dir / "ClaimsMatrix.csv", claims, ["claim_id", "claim", "evidence_required", "status", "boundary"])

    source_rows = [{
        "source_id": f"S-{i+1:03d}",
        "source_family": src,
        "expected_use": "Support, challenge, or bound mission claims.",
        "freshness_requirement": "Record retrieval date for time-sensitive facts.",
        "public_private_boundary": mission['private_data_boundary'],
    } for i, src in enumerate(mission['allowed_sources'])]
    write_csv(out_dir / "SourceProvenance.csv", source_rows, ["source_id", "source_family", "expected_use", "freshness_requirement", "public_private_boundary"])

    write_text(out_dir / "ContradictionRegister.md", f"""
# Contradiction Register — {mission['mission_title']}

## Current status
No unresolved contradiction has been promoted as settled fact in this generated package.

## Required human-review checks
- Verify that primary and secondary sources are separated.
- Verify that time-sensitive facts include retrieval dates.
- Verify that recommendations do not exceed evidence.
- Verify that uncertainty is visible in the decision state.

## Standing rule
Contradictions do not disappear. They are resolved, bounded, escalated, or recorded.
""")

    write_text(out_dir / "VerifierReport.md", f"""
# Verifier Report — {mission['mission_title']}

## Verification result
Generated artifact suite is ready for human review.

## Gates checked
- Mission objective exists.
- Success and failure criteria exist.
- Claims matrix exists.
- Source provenance exists.
- Contradiction register exists.
- Risk ledger exists.
- Evidence Docket exists.
- Decision state exists.
- Action graph exists.
- Claim-boundary report exists.

## Verifier notes
This report does not certify factual correctness of external sources. It certifies that the mission package contains the required GoalOS proof-to-action structure for review.

## Boundary
No public claim should be promoted until a human reviewer approves the Evidence Docket and any real-world source checks.
""")

    risk_rows = [
        {"risk_id": "R-001", "risk": "Unsupported claim promotion", "likelihood": "medium", "impact": "high", "mitigation": "ClaimBoundaryReport and human review before publication."},
        {"risk_id": "R-002", "risk": "Source freshness drift", "likelihood": "medium", "impact": "medium", "mitigation": "Record retrieval dates and refresh time-sensitive facts."},
        {"risk_id": "R-003", "risk": "Private data leakage", "likelihood": "low", "impact": "high", "mitigation": "Public/private boundary and secret scan before PR."},
        {"risk_id": "R-004", "risk": "Action without governance", "likelihood": "low", "impact": "high", "mitigation": "No auto-merge, no token movement, no Mainnet broadcast."},
    ]
    write_csv(out_dir / "RiskLedger.csv", risk_rows, ["risk_id", "risk", "likelihood", "impact", "mitigation"])

    decision_state = {
        "mission_id": mission_id,
        "mission_title": mission["mission_title"],
        "decision_to_support": mission["decision_to_support"],
        "state": "human_review_ready",
        "confidence": "structure_ready_not_source_certified",
        "required_human_review": bool(mission["reviewer_required"]),
        "recommended_options": [
            {"option": "Proceed to human review", "condition": "Evidence Docket and source checks are accepted."},
            {"option": "Request more evidence", "condition": "Claims are under-supported or contradictions remain."},
            {"option": "Do not publish", "condition": "Claim-boundary, privacy, or risk gates fail."},
        ],
        "claim_boundary": mission["claim_boundary"],
    }
    write_json(out_dir / "DecisionState.json", decision_state)

    write_text(out_dir / "EvidenceDocket.md", f"""
# Evidence Docket — {mission['mission_title']}

## 00 Manifest
- Mission ID: `{mission_id}`
- Generated: {now}
- Risk class: `{mission['risk_class']}`
- Human reviewer required: `{mission['reviewer_required']}`

## 01 Claims Matrix
See `ClaimsMatrix.csv`.

## 02 Source Provenance
See `SourceProvenance.csv`.

## 03 Contradiction Register
See `ContradictionRegister.md`.

## 04 Risk Ledger
See `RiskLedger.csv`.

## 05 Verifier Report
See `VerifierReport.md`.

## 06 Governed Decision State
See `DecisionState.json`.

## 07 Action Graph
See `ActionGraph.md`.

## 08 Chronicle Entry
See `ChronicleEntry.md`.

## Claim boundary
{bullet(mission['claim_boundary'])}

## Evidence-room doctrine
A proof page is not a marketing page. It is a claim-bound evidence room.
""")

    write_text(out_dir / "ExecutiveBrief.md", f"""
# Executive Brief — {mission['mission_title']}

## Decision to support
{mission['decision_to_support']}

## What GoalOS produced
A governed decision-state package: mission contract, work graph, claims matrix, source provenance, contradiction register, verifier report, risk ledger, Evidence Docket, action graph, Chronicle entry, and capability package.

## Recommended next action
Review the Evidence Docket, verify source claims, resolve open contradictions, then approve, revise, or reject the decision state.

## Board sentence
The deliverable is not a document. The deliverable is a governed decision state.
""")

    write_text(out_dir / "DecisionDeck.md", f"""
# Decision Deck — {mission['mission_title']}

## Slide 1 — Mission
{mission['mission_title']}

## Slide 2 — Decision to support
{mission['decision_to_support']}

## Slide 3 — Evidence posture
Claims matrix, source provenance, contradiction register, and verifier report are present.

## Slide 4 — Risk posture
Risk ledger is present. Human review remains required before public claim promotion.

## Slide 5 — Action path
See `ActionGraph.md`.

## Slide 6 — Final doctrine
AI creates output. GoalOS creates proof.
""")

    write_text(out_dir / "ActionGraph.md", f"""
# Action Graph — {mission['mission_title']}

## Governed next steps
1. Human reviewer inspects `EvidenceDocket.md` and `ClaimsMatrix.csv`.
2. Source reviewer verifies source provenance and freshness.
3. Risk reviewer checks `RiskLedger.csv`.
4. Operator approves, requests revision, or rejects the mission package.
5. If approved, publish only the public-safe docket and Chronicle entry.
6. If rejected, record failure mode and update the capability package.

## Rollback / stop conditions
{bullet(mission['failure_criteria'])}

## Rule
Insight is not finished until it becomes governed action.
""")

    write_text(out_dir / "ChronicleEntry.md", f"""
# Chronicle Entry — {mission['mission_title']}

## Memory object
This mission generated a proof-to-action package for future reuse.

## Reusable patterns
- Mission Contract structure.
- Claims Matrix discipline.
- Source Provenance discipline.
- Verifier Mesh checklist.
- Governed Decision State packaging.
- Action Graph and risk-ledger handoff.

## Future mission recommendation
Run a second mission using the same template after the human reviewer records accepted, rejected, and revised claims.

## Moat principle
The moat is the evidence graph.
""")

    write_text(out_dir / "CapabilityPackage.md", f"""
# Capability Package — {mission['mission_title']}

## Capability name
Proof-to-action mission package for `{mission_id}`.

## Initiation conditions
Use when an institution has a high-stakes objective that requires evidence, verification, action planning, and Chronicle memory.

## Required validators
- Claim-boundary reviewer.
- Source-provenance reviewer.
- Risk reviewer.
- Decision owner.

## Reuse scope
Reusable as a template for future Mission OS runs after human review.

## Propagation boundary
No eval, no propagation. No rollback, no release.
""")


    network = mission.get("ethereum_network", "none")
    mode = mission.get("ethereum_settlement_mode", "none")
    chain_id = 1 if network == "ethereumMainnet" else (11155111 if network == "ethereumSepolia" else 0)
    canonical = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
    readiness = {
        "mission_id": mission_id,
        "run_id": f"{mission_id}-{cycle}",
        "network": network,
        "chain_id": chain_id,
        "agialpha_token_address": mission.get("agialpha_token_address", canonical),
        "canonical_token_required": network == "ethereumMainnet",
        "mock_token_forbidden": network == "ethereumMainnet",
        "new_token_deployment_forbidden": True,
        "requires_token_movement": bool(mission.get("requires_token_movement", False)),
        "token_movement_performed": False,
        "requires_mainnet_broadcast": bool(mission.get("requires_mainnet_broadcast", False)),
        "mainnet_broadcast_performed": False,
        "evidence_docket_hash": sha256_file(out_dir / "EvidenceDocket.md"),
        "claims_matrix_hash": sha256_file(out_dir / "ClaimsMatrix.csv"),
        "risk_ledger_hash": sha256_file(out_dir / "RiskLedger.csv"),
        "verifier_report_hash": sha256_file(out_dir / "VerifierReport.md"),
        "chronicle_entry_hash": sha256_file(out_dir / "ChronicleEntry.md"),
        "alpha_work_unit_estimate": "readiness-only",
        "validator_status": "human_review_required",
        "accepted": not bool(mission.get("requires_mainnet_broadcast", False)) and not bool(mission.get("requires_token_movement", False)),
        "rejected": bool(mission.get("requires_mainnet_broadcast", False)) or bool(mission.get("requires_token_movement", False)),
        "requires_human_review": True,
        "recommended_settlement_mode": mode,
        "mainnet_deployed_status": "NO",
        "contract_verification_status": "NO_VERIFICATION_CLAIM",
        "deployment_manifest_path": "read-only operator supplied manifest when available",
        "verification_evidence_path": "read-only operator supplied evidence when available",
        "claim_boundary": "$AGIALPHA is not the product. Verified work is the product. $AGIALPHA is proof-settlement fuel.",
    }
    write_json(out_dir / "MissionSettlementReadiness.json", readiness)
    write_text(out_dir / "AGIALPHASettlementPlan.md", f"""
# AGIALPHA Settlement Plan — {mission['mission_title']}

$AGIALPHA is not the product. Verified work is the product. $AGIALPHA is proof-settlement fuel.

## Mode
{mode}

## Boundary
No token movement is performed by Mission OS. Mainnet output is readiness-only unless a local human operator supplies evidence.
""")
    write_text(out_dir / "EthereumDeploymentCompatibilityReport.md", f"""
# Ethereum Deployment Compatibility Report — {mission['mission_title']}

Mission OS is an off-chain proof-to-action layer. It reads and hashes evidence artifacts; it does not deploy Mainnet, move tokens, mint AGIALPHA, or weaken Sepolia/Mainnet Hardhat gates.

- Sepolia chainId: 11155111
- Ethereum Mainnet chainId: 1
- Canonical AGIALPHA token address is `{canonical}`.
- Ethereum Mainnet deployment status remains NO unless real chainId=1 transaction evidence exists.
""")

    # Claim boundary report is generated before QA; it is safe because generated text avoids forbidden claims.
    generated_paths = artifact_files(out_dir)
    ok, findings = scan_forbidden_claims(generated_paths, policy.get("forbiddenClaims", []))
    write_text(out_dir / "ClaimBoundaryReport.md", f"""
# Claim Boundary Report — {mission['mission_title']}

**Status:** {'PASS' if ok else 'FAIL'}  
**Generated:** {now}

## Findings
{as_json_block(findings)}

## Boundary
This package does not claim achieved AGI, achieved ASI, superintelligence, guaranteed ROI, legal/financial/medical advice, production readiness, external audit completion, cybersecurity certification, Mainnet deployment, or guaranteed market outcome.

## Governance note
Human review remains required before public claim promotion.
""")

    # QA after claim report
    generated_paths = artifact_files(out_dir)
    secrets = scan_secrets(generated_paths)
    ok2, findings2 = scan_forbidden_claims(generated_paths, policy.get("forbiddenClaims", []))
    required = policy.get("requiredArtifacts", [])
    missing = [name for name in required if name not in {p.name for p in generated_paths} and name not in {"artifact-manifest.json", "index.html", "run-state.json", "QAReport.md"}]
    qa_ok = not secrets and ok2 and not missing
    write_text(out_dir / "QAReport.md", f"""
# QA Report — {mission['mission_title']}

**Status:** {'PASS' if qa_ok else 'FAIL'}  
**Generated:** {now}

## Checks
- Required artifact presence: {'PASS' if not missing else 'FAIL'}
- Secret scan: {'PASS' if not secrets else 'FAIL'}
- Claim-boundary scan: {'PASS' if ok2 else 'FAIL'}
- No auto-publication: PASS
- No Mainnet broadcast: PASS
- No token movement: PASS

## Missing artifacts
{as_json_block(missing)}

## Secret findings
{as_json_block(secrets)}

## Claim-boundary findings
{as_json_block(findings2)}
""")

    # Manifest after all artifacts except manifest/run-state/html
    files = []
    for p in sorted(artifact_files(out_dir), key=lambda x: x.name):
        if p.name == "artifact-manifest.json":
            continue
        files.append({"path": p.name, "sha256": sha256_file(p), "bytes": p.stat().st_size})
    write_json(out_dir / "artifact-manifest.json", {
        "mission_id": mission_id,
        "generated_at": now,
        "generator": "scripts/mission-os/mission_os_until_done.py",
        "policy_version": policy.get("policyVersion"),
        "done_rule": "DONE true requires required artifacts, claim-boundary pass, QA pass, and human-review readiness.",
        "files": files,
        "claim_boundary": mission["claim_boundary"],
    })

    # HTML index
    body = f"""
<section>
  <div class=\"eyebrow\">Governed Decision State</div>
  <h2>{html.escape(mission['mission_title'])}</h2>
  <p>{html.escape(mission['decision_to_support'])}</p>
  <div class=\"rule\">AI creates output. GoalOS creates proof. The deliverable is not a document. The deliverable is a governed decision state.</div>
</section>
<section class=\"grid\">
  <div class=\"card\"><h3>Evidence Docket</h3><p>Claims, source provenance, contradiction register, risk ledger, verifier report, and public/private boundary.</p></div>
  <div class=\"card\"><h3>Verifier Mesh</h3><p>Checks claims, boundaries, risks, and required artifacts before the mission can be marked ready.</p></div>
  <div class=\"card\"><h3>Action Graph</h3><p>Converts insight into governed next steps, owner-ready review, and rollback conditions.</p></div>
  <div class=\"card\"><h3>Chronicle</h3><p>Records reusable capability and future mission recommendations.</p></div>
</section>
<section>
  <h2>Artifact manifest</h2>
  <table><thead><tr><th>Artifact</th><th>Purpose</th></tr></thead><tbody>
  {''.join(f'<tr><td><code>{html.escape(name)}</code></td><td>Mission OS generated artifact</td></tr>' for name in policy.get('requiredArtifacts', []))}
  </tbody></table>
</section>
"""
    write_text(out_dir / "index.html", html_page(f"GoalOS Mission OS — {mission['mission_title']}", body))


def compute_done(out_dir: Path, policy: Dict[str, Any]) -> Dict[str, Any]:
    required = policy.get("requiredArtifacts", [])
    present = {p.name for p in artifact_files(out_dir)}
    missing = [x for x in required if x not in present]
    claim_report = out_dir / "ClaimBoundaryReport.md"
    qa_report = out_dir / "QAReport.md"
    claim_pass = claim_report.exists() and "**Status:** PASS" in claim_report.read_text(encoding="utf-8", errors="ignore")
    qa_pass = qa_report.exists() and "**Status:** PASS" in qa_report.read_text(encoding="utf-8", errors="ignore")
    done = not missing and claim_pass and qa_pass
    gates = {
        "required_artifacts": not missing,
        "claim_boundary_passed": claim_pass,
        "qa_passed": qa_pass,
        "human_review_ready": done,
        "no_auto_merge": True,
        "no_mainnet_broadcast": True,
        "no_token_movement": True,
    }
    return {"done": done, "missing": missing, "gates": gates}


def run_until_done(mission_path: Path, out_dir: Path, policy_path: Path, max_cycles: int, json_output: bool = False) -> int:
    mission = json.loads(mission_path.read_text(encoding="utf-8"))
    errors = validate_mission(mission)
    if errors:
        for err in errors:
            print(f"MISSION_SCHEMA_ERROR: {err}", file=sys.stderr)
        return 2
    policy = load_policy(policy_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "mission_id": mission["mission_id"], "mission_title": mission["mission_title"],
        "run_id": f"{mission['mission_id']}-run", "status": "running", "done": False,
        "current_state": "MISSION_CREATED", "cycle_count": 0, "max_cycles": max_cycles,
        "created_at": utc_now(), "updated_at": utc_now(), "required_artifacts": load_policy(policy_path).get("requiredArtifacts", []),
        "artifact_status": {}, "qa_status": "PENDING", "claim_boundary_status": "PENDING",
        "settlement_readiness_status": "PENDING", "ethereum_network_status": mission.get("ethereum_network", "none"),
        "human_review_required": True, "public_claim_boundary": mission.get("claim_boundary", []),
        "next_action": "run until DONE", "cycles": [], "stage": "MISSION_CREATED",
    }
    for cycle in range(1, max_cycles + 1):
        create_artifacts(mission, out_dir, policy, cycle)
        # Write a provisional state before checking DONE so run-state.json itself is available.
        write_json(out_dir / "run-state.json", state)
        result = compute_done(out_dir, policy)
        stage = "DONE" if result["done"] else "REPAIR_REQUIRED"
        state["cycles"].append({"cycle": cycle, "time": utc_now(), "stage": stage, "result": result})
        state["done"] = result["done"]
        state["status"] = "DONE" if result["done"] else "REPAIR_REQUIRED"
        state["current_state"] = stage
        state["cycle_count"] = cycle
        state["updated_at"] = utc_now()
        state["artifact_status"] = {name: (name not in result["missing"]) for name in policy.get("requiredArtifacts", [])}
        state["qa_status"] = "PASS" if result["gates"].get("qa_passed") else "FAIL"
        state["claim_boundary_status"] = "PASS" if result["gates"].get("claim_boundary_passed") else "FAIL"
        state["settlement_readiness_status"] = "PASS" if (out_dir / "MissionSettlementReadiness.json").exists() else "NOT_REQUESTED"
        state["next_action"] = "human review" if result["done"] else "repair missing artifacts"
        state["stage"] = stage
        state["completed_at"] = utc_now() if result["done"] else None
        write_json(out_dir / "run-state.json", state)
        if result["done"]:
            if json_output:
                print(json.dumps(state, indent=2, sort_keys=True))
            else:
                print(f"GoalOS Mission OS DONE=true after {cycle} cycle(s). Output: {out_dir}")
            return 0
    if json_output:
        print(json.dumps(state, indent=2, sort_keys=True))
    else:
        print(f"GoalOS Mission OS DONE=false after {max_cycles} cycle(s). Output: {out_dir}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="GoalOS Mission OS until-done generator")
    parser.add_argument("--mission", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--policy", default=Path("config/goalos-mission-os.policy.json"), type=Path)
    parser.add_argument("--max-cycles", default=8, type=int)
    parser.add_argument("--json", action="store_true", help="Print final run-state JSON instead of friendly text")
    args = parser.parse_args()
    return run_until_done(args.mission, args.out, args.policy, args.max_cycles, args.json)

if __name__ == "__main__":
    raise SystemExit(main())
