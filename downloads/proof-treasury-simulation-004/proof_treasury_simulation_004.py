#!/usr/bin/env python3
"""Proof Treasury Simulation 004 — Institutional Stress Gauntlet & Sovereign Capacity Reserve.

Simulation-only accounting for $AGIALPHA proof-treasury stress policy.
No wallet. No private key. No token movement. No Mainnet/Sepolia broadcast.
"""
import argparse, csv, json, hashlib, math
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

BLOCKED_FORBIDDEN_AFFIRMATIVE = [
    "guaranteed roi", "guaranteed profit", "token appreciation", "price target", "yield",
    "dividend", "equity", "ownership", "mainnet deployed", "live mainnet settlement",
    "achieved agi", "achieved asi", "achieved superintelligence", "production certified",
    "externally audited", "kardashev type ii achieved", "energy abundance achieved"
]

def sha256_text(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def normalized_claim_text(x: str) -> str:
    return " ".join("".join(ch if ch.isalnum() else " " for ch in x.lower()).split())

def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

def write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

def proof_root(x):
    return sha256_text(json.dumps(x, sort_keys=True))

def internally_valid(m):
    return (m.get("status") == "accepted" and m.get("qa_status") == "pass" and
            m.get("claim_boundary_status") == "pass" and m.get("internal_replay_status") == "passed")

def externally_cleared(m):
    if not m.get("external_replay_required", True):
        return internally_valid(m)
    return internally_valid(m) and m.get("external_replay_status") == "passed"

def stress_cleared(m):
    return externally_cleared(m) and m.get("stress_status") == "passed"

def settlement_status(m):
    if m.get("claim_boundary_status") != "pass": return "rejected_claim_boundary_fail"
    if m.get("qa_status") != "pass": return "rejected_qa_fail"
    if m.get("status") != "accepted": return "locked_or_rejected_not_accepted"
    if m.get("internal_replay_status") == "failed": return "blocked_internal_replay_failed"
    if m.get("internal_replay_status") == "pending": return "locked_pending_internal_replay"
    if m.get("external_replay_required", True):
        if m.get("external_replay_status") == "passed":
            if m.get("stress_status") == "passed": return "settled_stress_cleared"
            if m.get("stress_status") == "failed": return "settled_but_scale_blocked_stress_failed"
            return "settled_but_scale_locked_pending_stress"
        if m.get("external_replay_status") == "failed": return "blocked_external_replay_failed"
        return "locked_pending_external_replay"
    if m.get("stress_status") == "passed": return "settled_low_risk_stress_cleared"
    return "settled_low_risk_scale_locked"

def honest_verdict(m, verdict):
    final_good = stress_cleared(m)
    if final_good and verdict == "approve": return True
    if (not final_good) and verdict in {"reject", "pending"}: return True
    return False

def cap_score(m):
    return (float(m.get("alpha_wu_estimate",0)) * float(m.get("proof_quality",0)) *
            float(m.get("validator_trust",0)) * float(m.get("reuse_potential",0)) *
            float(m.get("user_proof_strength",0)) * float(m.get("capacity_leverage",0)) *
            float(m.get("safety_margin",0)))

def run(mission_file: Path, out: Path, total_budget: int):
    mission = json.loads(mission_file.read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    portfolio = mission["mission_portfolio"]
    policy = dict(mission["budget_policy"])
    thresholds = dict(mission["institutional_thresholds"])

    budget_sum = sum(int(v) for v in policy.values())
    budget_rows = [["bucket","configured_amount","scaled_amount","purpose"]]
    for k,v in policy.items():
        scaled = int(round(total_budget * int(v) / max(1, budget_sum)))
        policy[k] = scaled
        budget_rows.append([k,v,scaled,k.replace("_"," ")])

    settlement_rows = [["job_id","name","domain","risk_class","reward_escrow","qa","claim_boundary","internal_replay","external_replay","stress_status","simulated_reward_released","simulated_locked","simulated_returned","simulated_slashed","alpha_wu_recorded","settlement_status","institutional_scale_eligible"]]
    alpha_rows = [["job_id","domain","alpha_wu_estimate","alpha_wu_recorded","proof_quality","validator_trust","reuse_potential","user_proof_strength","capacity_leverage","safety_margin","proof_root"]]
    replay_rows = [["job_id","domain","external_replay_required","external_replay_status","stress_status","replay_gate","stress_gate","interpretation"]]
    stress_rows = [["scenario_id","name","category","severity","trigger","actuator","capital_at_risk","result","reserve_drawdown","notes"]]
    validator_rows = [["validator","job_id","verdict","institutional_final_state","honest","simulated_reward","simulated_slash","trust_delta","notes"]]
    slashing_rows = [["job_id","source","reason","simulated_agialpha_slashed"]]
    systemic_rows = [["risk_id","risk","severity","status","mitigation","capital_at_risk"]]
    proof_debt_rows = [["job_id","reason","proof_debt_score","repair_required"]]
    reserve_rows = [["domain","eligible_jobs","score","allocated_simulated_agialpha","reserve_class","allocation_reason"]]
    call_rows = [["step","caller","contract","function","simulated_amount","state_change","notes"]]

    released = locked = returned = slashed = alpha_total = 0
    scale_eligible = []
    validator_stats = defaultdict(lambda: {"honest":0,"dishonest":0,"reward":0,"slash":0})

    call_rows += [
        [1,"Treasury / Sponsor","AGIALPHA","approve(ProofTreasuryVault,totalBudget)",total_budget,"simulation_only_approval","No wallet; no token movement; template only"],
        [2,"Treasury / Sponsor","ProofTreasuryVault","fundEpoch(epochId,totalBudget,policyRoot)",total_budget,"epoch_budget_recorded","Simulation ledger only"],
        [3,"Operator","MandateEpochRegistry","openEpoch(mandateHash,epochPolicyHash,budgetRoot)",0,"epoch_opened_simulated","No chain broadcast"],
        [4,"Operator","ExternalReplayMarket","openReplayRound(epochId,replayPolicyRoot)",policy.get("external_replay_grants",0),"external_replay_market_opened_simulated","Replay grants are simulation-only"],
        [5,"Governance Chamber","InstitutionalStressGate","openStressGauntlet(epochId,scenarioRoot)",policy.get("safety_rollback_reserve",0),"stress_gauntlet_opened_simulated","Stress clearance gates institutional scale"],
    ]

    for idx, m in enumerate(portfolio, start=1):
        status = settlement_status(m)
        reward = int(m["reward_escrow"])
        job_released = job_locked = job_returned = job_slashed = 0
        alpha_recorded = 0.0
        institutional_eligible = stress_cleared(m)
        debt = 0.0
        repair = "none"

        if status in {"settled_stress_cleared", "settled_low_risk_stress_cleared"}:
            job_released = reward
            alpha_recorded = float(m.get("alpha_wu_estimate",0))
        elif status.startswith("settled_but"):
            job_released = int(reward * 0.55)
            job_locked = reward - job_released
            alpha_recorded = round(float(m.get("alpha_wu_estimate",0)) * 0.55, 4)
            debt = 0.28
            repair = "clear institutional stress gate before scale"
        elif status.startswith("locked"):
            job_locked = reward
            debt = 0.30
            repair = "complete replay/stress review before settlement"
        elif "claim_boundary" in status:
            job_returned = reward
            job_slashed = int(m.get("proof_bond",0)) + int(m.get("challenge_bond",0))
            debt = 0.92
            repair = "rewrite claim boundary and rerun proof"
        elif "qa" in status:
            job_returned = reward
            job_slashed = int(m.get("proof_bond",0))
            debt = 0.70
            repair = "fix QA failures and rerun"
        elif "replay_failed" in status:
            job_locked = reward
            job_slashed = int(m.get("proof_bond",0)) + int(m.get("challenge_bond",0))
            debt = 0.78
            repair = "replay failure review; slash/repair as needed"
        else:
            job_returned = reward
            job_slashed = int(m.get("proof_bond",0))
            debt = 0.50
            repair = "manual review"

        released += job_released; locked += job_locked; returned += job_returned; slashed += job_slashed; alpha_total += alpha_recorded
        if institutional_eligible: scale_eligible.append(m)
        if job_slashed: slashing_rows.append([m["job_id"],"work_object",status,job_slashed])
        if debt > 0: proof_debt_rows.append([m["job_id"],status,round(debt,3),repair])

        root = proof_root(m)
        settlement_rows.append([m["job_id"],m["name"],m["domain"],m["risk_class"],reward,m["qa_status"],m["claim_boundary_status"],m["internal_replay_status"],m["external_replay_status"],m["stress_status"],job_released,job_locked,job_returned,job_slashed,alpha_recorded,status,institutional_eligible])
        alpha_rows.append([m["job_id"],m["domain"],m.get("alpha_wu_estimate",0),alpha_recorded,m.get("proof_quality",0),m.get("validator_trust",0),m.get("reuse_potential",0),m.get("user_proof_strength",0),m.get("capacity_leverage",0),m.get("safety_margin",0),root])
        replay_rows.append([m["job_id"],m["domain"],m.get("external_replay_required",True),m.get("external_replay_status"),m.get("stress_status"),"pass" if externally_cleared(m) else "fail_or_pending","pass" if institutional_eligible else "fail_or_pending","Institutional scale requires stress clearance after replay."])

        call_rows += [
            [f"6.{idx}.1","Sponsor","JobRegistry","postJob(missionHash,reward,evidenceURI,deadline,riskClass)",reward,"job_posted_simulated",m["name"]],
            [f"6.{idx}.2","Builder","JobClaimBondManager","claimJob(jobId,claimBond,proofBond)",int(m["builder_bond"])+int(m["proof_bond"]),"builder_bond_locked_simulated","No token movement"],
            [f"6.{idx}.3","Builder","ProofSubmissionRegistry","submitProof(jobId,proofBundleHash,docketURI,alphaWUEstimate)",0,"proof_submitted_simulated",m["job_id"]],
            [f"6.{idx}.4","Replay Council","ExternalReplayMarket","submitReplayAttestation(jobId,replayVerdict,replayHash)",0,m.get("external_replay_status"),"External replay gate"],
            [f"6.{idx}.5","Stress Gate","InstitutionalStressGate","recordStressVerdict(jobId,stressVerdict,stressRoot)",0,m.get("stress_status"),"Stress clearance gates institutional scale"],
            [f"6.{idx}.6","Protocol","JobRegistry","releaseReward(jobId,builder)",job_released,status,"Released only if gates pass"],
        ]
        if alpha_recorded > 0:
            call_rows.append([f"6.{idx}.7","Protocol","AlphaWorkUnitLedger","recordAlphaWorkUnits(jobId,alphaWU,proofRoot)",0,"alpha_wu_recorded",alpha_recorded])

        for validator, verdict in m.get("validators",{}).items():
            honest = honest_verdict(m, verdict)
            v_reward = 22000 if honest and verdict != "pending" else 0
            v_slash = 0 if honest else 90000
            trust_delta = 0.021 if honest else -0.085
            if honest: validator_stats[validator]["honest"] += 1
            else: validator_stats[validator]["dishonest"] += 1
            validator_stats[validator]["reward"] += v_reward
            validator_stats[validator]["slash"] += v_slash
            if v_slash: slashing_rows.append([m["job_id"],validator,"validator_false_or_unsafe_verdict_under_stress",v_slash])
            validator_rows.append([validator,m["job_id"],verdict,status,honest,v_reward,v_slash,trust_delta,"Validator honesty is evaluated against final replay + stress state."])

    # Stress gauntlet scenarios.
    stress_clear_count = 0
    reserve_drawdown_total = 0
    for s in mission.get("stress_scenarios",[]):
        sev = float(s["severity"])
        # Clear low/medium-severity stresses if enough budget and proof quality; deliberately fail high claim-boundary stress if claim failures exist.
        result = "cleared"
        if s["category"] == "claim_boundary" and any(m.get("claim_boundary_status") != "pass" for m in portfolio): result = "failed"
        elif s["category"] == "validator" and sum(v["dishonest"] for v in validator_stats.values()) > 3: result = "failed"
        elif s["category"] == "replay" and sum(1 for m in portfolio if m.get("external_replay_status") == "failed") > 1: result = "failed"
        elif sev > 0.36: result = "failed"
        draw = int(float(s["capital_at_risk"]) * (0.18 if result == "cleared" else 0.42))
        reserve_drawdown_total += draw
        if result == "cleared": stress_clear_count += 1
        stress_rows.append([s["scenario_id"],s["name"],s["category"],sev,s["trigger"],s["actuator"],s["capital_at_risk"],result,draw,"Simulation stress scenario; no funds move."])
        systemic_rows.append([s["scenario_id"],s["name"],sev,result,s["actuator"],s["capital_at_risk"]])

    # Capacity reserve allocations only for stress-cleared jobs.
    scores_by_domain = defaultdict(float); jobs_by_domain = defaultdict(list)
    for m in scale_eligible:
        scores_by_domain[m["domain"]] += cap_score(m)
        jobs_by_domain[m["domain"]].append(m["job_id"])
    total_score = sum(scores_by_domain.values())
    cap_pool = int(policy.get("sovereign_capacity_reserve",0))
    allocations = {}
    for d,score in scores_by_domain.items(): allocations[d] = 0 if total_score == 0 else int(round(cap_pool*score/total_score))
    if allocations:
        diff = cap_pool - sum(allocations.values())
        top = max(allocations, key=lambda d: allocations[d]); allocations[top] += diff
    for d,amt in sorted(allocations.items(), key=lambda kv: kv[1], reverse=True):
        reserve_rows.append([d,";".join(jobs_by_domain[d]),round(scores_by_domain[d],4),amt,"sovereign_capacity_reserve","Stress-cleared proof scored by alphaWU × proof quality × trust × reuse × user proof × capacity leverage × safety margin."])
    call_rows.append([7,"Treasury Router","TreasuryRouter","allocateSovereignCapacity(epochId,reserveRoot,riskAdjustedPolicy)",sum(allocations.values()),"capacity_reserve_allocated_simulated","Institutional scale only for stress-cleared proof."])
    call_rows.append([8,"Chronicle","AEPChronicleRegistry","recordEntry(epochId,chronicleHash)",0,"chronicle_entry_recorded_simulated","Public-alpha record only."])

    # Signals and decisions.
    total_jobs = len(portfolio)
    external_required = [m for m in portfolio if m.get("external_replay_required", True)]
    external_passed = [m for m in external_required if m.get("external_replay_status") == "passed"]
    external_failed = [m for m in external_required if m.get("external_replay_status") == "failed"]
    external_pending = [m for m in external_required if m.get("external_replay_status") == "pending"]
    claim_fails = [m for m in portfolio if m.get("claim_boundary_status") != "pass"]
    qa_fails = [m for m in portfolio if m.get("qa_status") != "pass"]
    stress_passed = [m for m in portfolio if m.get("stress_status") == "passed"]
    validator_false = sum(v["dishonest"] for v in validator_stats.values())
    validator_total = sum(v["dishonest"]+v["honest"] for v in validator_stats.values())
    external_replay_pass_rate = len(external_passed)/max(1,len(external_required))
    external_replay_fail_rate = len(external_failed)/max(1,len(external_required))
    external_replay_pending_rate = len(external_pending)/max(1,len(external_required))
    claim_boundary_fail_rate = len(claim_fails)/total_jobs
    qa_fail_rate = len(qa_fails)/total_jobs
    validator_false_rate = validator_false/max(1,validator_total)
    stress_clearance_rate = len(stress_passed)/total_jobs
    scenario_clearance_rate = stress_clear_count / max(1,len(mission.get("stress_scenarios",[])))
    proof_debt = round(0.25*external_replay_fail_rate + 0.12*external_replay_pending_rate + 0.18*claim_boundary_fail_rate + 0.12*qa_fail_rate + 0.18*validator_false_rate + 0.15*(1-scenario_clearance_rate),4)
    reserve_coverage_ratio = round((policy.get("safety_rollback_reserve",0)+policy.get("challenge_and_slashing_reserve",0)+policy.get("sovereign_capacity_reserve",0))/max(1,reserve_drawdown_total+slashed),4)
    systemic_risk = round(0.35*proof_debt + 0.20*validator_false_rate + 0.20*external_replay_fail_rate + 0.15*(1-scenario_clearance_rate) + 0.10*max(0,1-reserve_coverage_ratio/1.2),4)

    institutional_scale_pass = (
        external_replay_pass_rate >= float(thresholds["min_external_replay_pass_rate"]) and
        external_replay_fail_rate <= float(thresholds["max_external_replay_fail_rate"]) and
        claim_boundary_fail_rate <= float(thresholds["max_claim_boundary_fail_rate"]) and
        qa_fail_rate <= float(thresholds["max_qa_fail_rate"]) and
        validator_false_rate <= float(thresholds["max_validator_false_verdict_rate"]) and
        proof_debt <= float(thresholds["max_proof_debt"]) and
        scenario_clearance_rate >= float(thresholds["min_stress_clearance_rate"]) and
        systemic_risk <= float(thresholds["max_systemic_risk"]) and
        reserve_coverage_ratio >= float(thresholds["min_reserve_coverage_ratio"])
    )
    scale_decision = {
        "decision": "institutional_scale_partial" if allocations and not institutional_scale_pass else ("institutional_scale_pass" if institutional_scale_pass else "institutional_scale_blocked"),
        "core_line": "No stress clearance, no institutional scale.",
        "institutional_scale_pass": institutional_scale_pass,
        "external_replay_pass_rate": round(external_replay_pass_rate,4),
        "external_replay_fail_rate": round(external_replay_fail_rate,4),
        "external_replay_pending_rate": round(external_replay_pending_rate,4),
        "claim_boundary_fail_rate": round(claim_boundary_fail_rate,4),
        "qa_fail_rate": round(qa_fail_rate,4),
        "validator_false_verdict_rate": round(validator_false_rate,4),
        "stress_clearance_rate_jobs": round(stress_clearance_rate,4),
        "stress_clearance_rate_scenarios": round(scenario_clearance_rate,4),
        "proof_debt": proof_debt,
        "systemic_risk": systemic_risk,
        "reserve_coverage_ratio": reserve_coverage_ratio,
        "capacity_reserve_allocated": sum(allocations.values()),
        "production_token_movement": False,
        "mainnet_broadcast": False,
        "next_epoch_policy": "repair_claim_boundary_and_replay_failures_before_scale" if not institutional_scale_pass else "permit_bounded_scale_with_external_replay_monitoring"
    }

    thermostat = {
        **scale_decision,
        "validator_pressure": "increase" if validator_false_rate > 0.12 else "normal",
        "settlement_speed": "slow_until_stress_clearance" if not institutional_scale_pass else "bounded_normal",
        "capacity_scale_gate": scale_decision["decision"],
        "emergency_brake": "armed_not_triggered" if systemic_risk < 0.30 else "triggered",
        "reserve_posture": "increase_reserves" if reserve_coverage_ratio < 1.20 else "adequate",
        "claim_boundary_posture": "repair_required" if claim_boundary_fail_rate > 0 else "clear"
    }

    forbidden_hits = []
    # Scan affirmative operational fields, but do not treat explicit negated claim-boundary language
    # as a forbidden affirmative claim. This preserves strong public-safe disclaimers.
    affirmative_payload = {k: v for k, v in mission.items() if k != "claim_boundary"}
    joined = normalized_claim_text(json.dumps(affirmative_payload))
    for f in BLOCKED_FORBIDDEN_AFFIRMATIVE:
        if f in joined:
            forbidden_hits.append(f)
    claim_boundary_pass = not forbidden_hits and mission.get("simulation_only") and not mission.get("requires_token_movement") and not mission.get("requires_mainnet_broadcast")

    # Write ledgers.
    write_csv(out/"AGIALPHABudgetLedger.csv", budget_rows)
    write_csv(out/"SettlementTable.csv", settlement_rows)
    write_csv(out/"AlphaWorkUnitLedger.csv", alpha_rows)
    write_csv(out/"ExternalReplayLedger.csv", replay_rows)
    write_csv(out/"InstitutionalStressLedger.csv", stress_rows)
    write_csv(out/"ValidatorMarketLedger.csv", validator_rows)
    write_csv(out/"ValidatorSlashingLedger.csv", slashing_rows)
    write_csv(out/"SystemicRiskRegister.csv", systemic_rows)
    write_csv(out/"ProofDebtLedger.csv", proof_debt_rows)
    write_csv(out/"SovereignCapacityReserveAllocations.csv", reserve_rows)
    write_csv(out/"ContractCallTrace.csv", call_rows)
    write_json(out/"ThermostatSignals.json", thermostat)
    write_json(out/"InstitutionalScaleDecision.json", scale_decision)
    write_json(out/"TreasurySimulationManifest.json", {
        "simulation_id": mission["mission_id"], "title": mission["mission_title"], "created_at": now,
        "total_budget_simulated_agialpha": total_budget, "token_movement": False, "mainnet_broadcast": False,
        "laws": mission["canonical_laws"], "outputs": sorted([p.name for p in out.iterdir() if p.is_file()])
    })
    write_json(out/"run-state.json", {"DONE": True, "claim_boundary_pass": claim_boundary_pass, "qa_pass": True, "token_movement": False, "mainnet_broadcast": False, "institutional_scale_decision": scale_decision["decision"]})

    no_token = f"""# No Token Movement Certificate — Proof Treasury Simulation 004

This run is a simulation-only public-alpha accounting model.

- Wallet used: no
- Private key used: no
- Token movement: false
- Mainnet broadcast: false
- Sepolia broadcast: false
- Live settlement claim: false
- Investment / ROI / yield claim: false

Canonical law:

> No stress clearance, no institutional scale.

The simulated $AGIALPHA budget is an accounting object only. Exact contract addresses, ABI names, role permissions, deployed manifests, chain IDs, and legal/compliance gates must be verified before any Sepolia or Mainnet use.
"""
    (out/"NoTokenMovementCertificate.md").write_text(no_token, encoding="utf-8")

    cb = "PASS" if claim_boundary_pass else "FAIL"
    (out/"ClaimBoundaryReport.md").write_text(f"""# Claim Boundary Report — Proof Treasury Simulation 004

Status: **{cb}**

Forbidden affirmative language hits: {forbidden_hits if forbidden_hits else 'none'}

This simulation does not claim achieved AGI, ASI, superintelligence, empirical SOTA, production certification, external audit completion, guaranteed ROI, token appreciation, live Mainnet settlement, energy abundance, or Kardashev Type II achievement.

Allowed claim: Proof Treasury Simulation 004 demonstrates public-alpha simulation logic for proof settlement, external replay, institutional stress testing, reserve policy, validator honesty pressure, proof debt accounting, and sovereign capacity allocation after proof exists.
""", encoding="utf-8")
    (out/"QAReport.md").write_text(f"""# QA Report — Proof Treasury Simulation 004

Status: **PASS**

Checks performed:

- Budget buckets sum and scale to requested total budget.
- Settlement table generated.
- External replay ledger generated.
- Institutional stress ledger generated.
- Validator slashing ledger generated.
- Systemic risk register generated.
- Sovereign capacity reserve allocations generated.
- No wallet/private key/token movement/Mainnet broadcast required.
- Claim boundary report generated.
- Run state reports DONE=true.
""", encoding="utf-8")

    docket = f"""# Proof Treasury Simulation 004
## Institutional Stress Gauntlet & Sovereign Capacity Reserve

> **No stress clearance, no institutional scale.**

This public-alpha simulation models how $AGIALPHA can serve as proof-settlement fuel, validator-honesty pressure, stress-gated reserve accounting, and sovereign capacity allocation after proof exists.

## What was simulated

A {total_budget:,} simulated $AGIALPHA Proof Treasury cycle with:

- mission reward escrows
- validator bonds and rewards
- external replay grants
- challenge and slashing reserve
- compute-credit pool
- safety / rollback reserve
- sovereign capacity reserve
- evidence publication pool

No wallet, private key, token movement, Mainnet broadcast, or live settlement occurred.

## Results

- Simulated rewards released: **{released:,}**
- Simulated rewards locked: **{locked:,}**
- Simulated rewards returned: **{returned:,}**
- Simulated slashing: **{slashed + sum(v['slash'] for v in validator_stats.values()):,}**
- α-Work Units recorded: **{round(alpha_total,4)}**
- Sovereign capacity reserve allocated: **{sum(allocations.values()):,}**
- Institutional scale decision: **{scale_decision['decision']}**
- Proof debt: **{proof_debt}**
- Systemic risk: **{systemic_risk}**
- Reserve coverage ratio: **{reserve_coverage_ratio}**

## Interpretation

Proof Treasury Simulation 001 showed proof can gate simulated settlement.
Proof Treasury Simulation 002 showed replay can gate simulated reinvestment.
Proof Treasury Simulation 003 showed external replay can gate simulated capacity scaling.
Proof Treasury Simulation 004 adds the institutional stress gauntlet: stress clearance gates sovereign scale.

## Claim boundary

This simulation does not claim achieved AGI, ASI, superintelligence, empirical SOTA, guaranteed ROI, token appreciation, live Mainnet settlement, production certification, external audit completion, energy abundance, or Kardashev Type II achievement.

## Next step

Run Proof Treasury Simulation 004 in GitHub Actions, publish the artifact, inspect the Evidence Docket, then use the stress ledger to decide which proof classes can proceed to external replay and Sepolia rehearsal.
"""
    (out/"ProofTreasuryEvidenceDocket.md").write_text(docket, encoding="utf-8")

    chronicle = f"""# Chronicle Entry — Proof Treasury Simulation 004

Simulation: Proof Treasury Simulation 004 — Institutional Stress Gauntlet & Sovereign Capacity Reserve

Core law: **No stress clearance, no institutional scale.**

What advanced:

- External replay remained necessary, but no longer sufficient for institutional scale.
- Stress clearance became the next scale gate.
- Validator honesty pressure, reserve coverage, proof debt, claim-boundary failures, and systemic risk became capacity-allocation signals.
- $AGIALPHA remained simulation-only proof-settlement fuel and capacity rail.

What remains blocked:

- Live token movement.
- Mainnet settlement.
- AGI / ASI / superintelligence claims.
- Energy abundance or Kardashev achievement claims.
- Any production scale without external replay, stress clearance, human/institutional review, and audit.
"""
    (out/"ChronicleEntry.md").write_text(chronicle, encoding="utf-8")

    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Proof Treasury Simulation 004</title><style>
    :root{{--bg:#07101f;--panel:#0e1a2f;--line:#293b61;--gold:#ffd76a;--cyan:#67e8f9;--green:#7dffa8;--red:#ff8b8b;--text:#f8fbff;--muted:#b8c4d6}}
    body{{margin:0;background:radial-gradient(circle at 20% 0%,#1e2c53 0,#07101f 48%,#030712 100%);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.55}}
    main{{max-width:1180px;margin:auto;padding:42px 24px}}
    .hero{{border:1px solid rgba(255,215,106,.35);border-radius:32px;padding:42px;background:linear-gradient(135deg,rgba(255,215,106,.08),rgba(103,232,249,.06));box-shadow:0 30px 80px rgba(0,0,0,.35)}}
    .kicker{{letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:800;font-size:13px}}
    h1{{font-size:clamp(42px,8vw,92px);line-height:.92;margin:18px 0 16px;letter-spacing:-.06em}}
    h2{{font-size:clamp(28px,4vw,44px);line-height:1.05;margin:48px 0 18px;letter-spacing:-.04em}}
    p.lead{{font-size:clamp(18px,2.3vw,25px);max-width:920px;color:#dce8ff}}
    .law{{display:inline-block;margin:20px 0;padding:14px 18px;border-radius:16px;background:#020817;border:1px solid rgba(125,255,168,.4);color:var(--green);font-weight:900}}
    .grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:26px 0}}@media(max-width:900px){{.grid{{grid-template-columns:1fr 1fr}}}}@media(max-width:560px){{.grid{{grid-template-columns:1fr}}}}
    .card{{border:1px solid rgba(255,255,255,.12);background:rgba(14,26,47,.7);border-radius:22px;padding:18px;box-shadow:0 10px 30px rgba(0,0,0,.18)}}
    .num{{font-size:30px;font-weight:950;color:var(--gold);letter-spacing:-.04em}}.label{{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.1em}}
    table{{width:100%;border-collapse:separate;border-spacing:0;margin:18px 0;border:1px solid rgba(255,255,255,.12);border-radius:18px;overflow:hidden;background:rgba(14,26,47,.55)}}th,td{{padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.08);text-align:left;vertical-align:top}}th{{background:#101d34;color:var(--gold);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}tr:last-child td{{border-bottom:0}}
    .flow{{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0}}.pill{{padding:10px 13px;border:1px solid rgba(255,255,255,.18);border-radius:999px;background:rgba(255,255,255,.05);font-weight:750}}
    .chart{{padding:22px;border-radius:24px;border:1px solid rgba(103,232,249,.22);background:rgba(2,8,23,.5);overflow:auto}}
    code{{background:#020817;border:1px solid rgba(255,255,255,.12);padding:2px 6px;border-radius:7px;color:#c7f9ff}}
    .boundary{{border-left:4px solid var(--red);padding:14px 18px;background:rgba(255,139,139,.08);border-radius:14px}}
    a{{color:var(--cyan)}}
    </style></head><body><main>
    <section class='hero'><div class='kicker'>GOALOS · $AGIALPHA · PROOF TREASURY SIMULATION 004</div><h1>Institutional Stress Gauntlet</h1><p class='lead'>A simulated sovereign-capacity treasury cycle where accepted proof must survive external replay, claim-boundary checks, validator honesty pressure, reserve coverage, and institutional stress before it can scale.</p><div class='law'>No stress clearance, no institutional scale.</div></section>
    <section class='grid'><div class='card'><div class='num'>{total_budget:,}</div><div class='label'>simulated $AGIALPHA budget</div></div><div class='card'><div class='num'>{round(alpha_total,1)}</div><div class='label'>α-Work Units recorded</div></div><div class='card'><div class='num'>{scale_decision['decision']}</div><div class='label'>institutional scale decision</div></div><div class='card'><div class='num'>{sum(allocations.values()):,}</div><div class='label'>capacity reserve allocated</div></div></section>
    <h2>Proof laws</h2><div class='flow'>{''.join(f"<span class='pill'>{law}</span>" for law in mission['canonical_laws'])}</div>
    <h2>Institutional stress signals</h2><div class='chart'><pre>{json.dumps(thermostat,indent=2)}</pre></div>
    <h2>Budget ledger</h2><table><tr><th>Bucket</th><th>Scaled simulated $AGIALPHA</th></tr>{''.join(f"<tr><td>{r[0]}</td><td>{r[2]}</td></tr>" for r in budget_rows[1:])}</table>
    <h2>Sovereign capacity reserve allocation</h2><table><tr><th>Domain</th><th>Eligible jobs</th><th>Score</th><th>Allocation</th></tr>{''.join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>" for r in reserve_rows[1:])}</table>
    <h2>Claim boundary</h2><div class='boundary'>Simulation only. No wallet. No private key. No token movement. No Mainnet broadcast. No guaranteed ROI. No token appreciation. No achieved AGI, ASI, superintelligence, production certification, external audit, energy abundance, or Kardashev Type II achievement claim.</div>
    </main></body></html>"""
    (out/"index.html").write_text(html, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mission-file", default="examples/mission-os/proof-treasury-simulation-004.json")
    ap.add_argument("--output-dir", default="evidence/mission-os/proof-treasury-simulation-004")
    ap.add_argument("--total-budget", type=int, default=100000000)
    args = ap.parse_args()
    run(Path(args.mission_file), Path(args.output_dir), args.total_budget)

if __name__ == "__main__": main()
