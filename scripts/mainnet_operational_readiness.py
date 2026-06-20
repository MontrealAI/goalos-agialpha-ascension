#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
QA = ROOT / "qa"
DOCS = ROOT / "docs"
RUNBOOKS = DOCS / "runbooks"
ARCHITECTURE = DOCS / "architecture"
OPERATIONS = DOCS / "operations"
MAINNET_READINESS = QA / "mainnet-readiness"
RELEASE_ROOTS = (
    "contracts/",
    "scripts/",
    "test/",
    "qa/",
    "docs/",
    "schemas/",
    "ignition/",
    "package.json",
    "package-lock.json",
    "hardhat.config.ts",
    "foundry.toml",
    "tsconfig.json",
)
GENERATED_PREFIXES = (
    "qa/mainnet-operational",
    "qa/mainnet-readiness/",
    "qa/monitoring-event-catalog.json",
    "qa/business-override-matrix.json",
    "qa/funds-and-liabilities-inventory.json",
    "qa/lifecycle-selector-policy.json",
    "qa/controlled-mainnet-canary-template.json",
    "qa/mainnet-production-readiness-dossier.json",
    "docs/MAINNET_OPERATIONAL_GAP_MATRIX.md",
    "docs/architecture/",
    "docs/operations/",
    "docs/BUSINESS_OVERRIDE_MATRIX.md",
    "docs/FUNDS_AND_LIABILITIES_MODEL.md",
    "docs/LIFECYCLE_SELECTOR_POLICY.md",
    "docs/runbooks/",
)
STATE_HINTS = ("external", "public")
VIEW_HINTS = ("view", "pure")
ASSET_WORDS = ("Vault", "Treasury", "Bond", "Reward", "Stake", "Router", "Escrow")
TOKEN_RESERVE_VAULT_ALIASES = ("ProofRewardsVault", "LiquidityVault", "SecurityVault", "CommunityVault")
STATE_WORDS = (
    "Job", "Claim", "Submission", "Proof", "Reward", "Bond", "Stake", "Credential",
    "Reputation", "AEP", "Tranche", "Treasury", "Vault", "Agent", "Operator", "Registry",
)
TOKEN_FLOW_PATTERNS = (
    "safeTransferFrom", "transferFrom", "address(this)", "msg.value", "receive() external payable",
)


def sh(cmd):
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"UNAVAILABLE: {exc}"



def release_relevant_dirty_paths():
    # Only unstaged release-relevant dirt is recorded here. Staged content is
    # already represented by sourceTreeHash, and generated artifacts are excluded
    # so pre-commit generation does not embed transient self-dirt.
    status = sh(["git", "diff", "--name-only"])
    if status.startswith("UNAVAILABLE:"):
        return [status]
    dirty = []
    for rel in status.splitlines():
        if not rel.startswith(RELEASE_ROOTS):
            continue
        if rel.startswith(GENERATED_PREFIXES):
            continue
        dirty.append(rel)
    return sorted(set(dirty))

def git_index_text(rel):
    return subprocess.check_output(["git", "show", f":{rel}"], cwd=ROOT).decode("utf-8", errors="ignore")


def git_index_bytes(rel):
    return subprocess.check_output(["git", "show", f":{rel}"], cwd=ROOT)


def tracked_contract_paths():
    listing = sh(["git", "ls-files", "contracts", "*.sol"])
    return sorted(rel for rel in listing.splitlines() if rel.startswith("contracts/") and rel.endswith(".sol"))


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def tracked_source_tree_hash():
    """Hash the staged source content, excluding generated readiness outputs.

    The index is used so generated artifacts can be regenerated before commit and
    remain tied to the exact non-generated release-relevant content that will be
    committed, while unrelated working-tree dirt is ignored.
    """
    listing = sh(["git", "ls-files"])
    h = hashlib.sha256()
    for rel in sorted(x for x in listing.splitlines() if x):
        if not rel.startswith(RELEASE_ROOTS):
            continue
        if rel.startswith(GENERATED_PREFIXES):
            continue
        if rel.startswith(("node_modules/", "artifacts/", "cache/")):
            continue
        try:
            blob = subprocess.check_output(["git", "show", f":{rel}"], cwd=ROOT)
        except subprocess.CalledProcessError:
            blob = subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=ROOT)
        h.update(rel.encode() + b"\0" + hashlib.sha256(blob).hexdigest().encode() + b"\n")
    return h.hexdigest()


def contract_blocks(text):
    cleaned = strip_comments(text)
    blocks = []
    pattern = re.compile(r"\b(abstract\s+contract|contract|interface)\s+(\w+)(?:\s+is\s+([^\{]+))?\s*\{")
    for match in pattern.finditer(cleaned):
        depth = 1
        pos = match.end()
        while pos < len(cleaned) and depth:
            if cleaned[pos] == "{":
                depth += 1
            elif cleaned[pos] == "}":
                depth -= 1
            pos += 1
        kind, name, bases = match.groups()
        blocks.append({
            "kind": kind,
            "name": name,
            "bases": [b.strip().split()[0] for b in (bases or "").split(",") if b.strip()],
            "body": cleaned[match.end():pos - 1],
        })
    return blocks


def concrete_contract_infos(text):
    return [block for block in contract_blocks(text) if block["kind"] == "contract"]


def canonical_param(param):
    words = [w for w in re.split(r"\s+", param.strip()) if w]
    words = [w for w in words if w not in {"memory", "calldata", "storage", "payable"}]
    if not words:
        return ""
    typ = words[0]
    suffix = ""
    while typ.endswith("]") and "[" in typ:
        idx = typ.rfind("[")
        suffix = typ[idx:] + suffix
        typ = typ[:idx]
    if typ == "ReleaseRecord":
        return "(bytes32,bytes32,bytes32,bytes32,bytes32,bytes32,bytes32,address,address,uint8,uint256)" + suffix
    if typ.startswith("uint") or typ.startswith("int") or typ.startswith("bytes") or typ in {"address", "bool", "string"}:
        return typ + suffix
    if typ == "byte":
        return "bytes1" + suffix
    # Contract/interface values are ABI-encoded as address; enum values in this repo are ABI-encoded as uint8.
    return ("address" if typ.startswith("I") else "uint8") + suffix


def canonical_signature(name, params):
    canonical = [canonical_param(part) for part in params.split(",") if part.strip()]
    return f"{name}({','.join(canonical)})"


def iter_function_headers(body):
    i = 0
    marker = "function"
    while True:
        start = body.find(marker, i)
        if start == -1:
            return
        before = body[start - 1] if start else " "
        after = body[start + len(marker)] if start + len(marker) < len(body) else " "
        if (before.isalnum() or before == "_") or not after.isspace():
            i = start + len(marker)
            continue
        name_match = re.match(r"function\s+(\w+)\s*\(", body[start:])
        if not name_match:
            i = start + len(marker)
            continue
        name = name_match.group(1)
        pos = start + name_match.end() - 1
        depth = 0
        end = pos
        while end < len(body):
            ch = body[end]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            end += 1
        if end >= len(body):
            return
        params = body[pos + 1:end]
        attr_start = end + 1
        attr_end_candidates = [x for x in [body.find("{", attr_start), body.find(";", attr_start)] if x != -1]
        if not attr_end_candidates:
            return
        attr_end = min(attr_end_candidates)
        yield name, params, body[attr_start:attr_end]
        i = attr_end + 1

def functions_from_body(body):
    funcs = []
    for name, params, attrs in iter_function_headers(body):
        if any(x in attrs for x in STATE_HINTS) and not any(x in attrs for x in VIEW_HINTS):
            funcs.append({
                "name": name,
                "signature": canonical_signature(name, params),
                "attributes": " ".join(attrs.split()),
                "classification": classify(name),
            })
    return funcs


def roles_from_body(body):
    return sorted(set(re.findall(r"bytes32\s+(?:public\s+)?(?:constant\s+)?([A-Z0-9_]+_ROLE)", body)))


def inherited_goalos_surface():
    text = git_index_text("contracts/access/GoalOSAccessControl.sol")
    for block in contract_blocks(text):
        if block["name"] == "GoalOSAccessControl":
            return functions_from_body(block["body"]), sorted(set(roles_from_body(block["body"]) + ["DEFAULT_ADMIN_ROLE"]))
    return [], []


def inherited_erc721_surface():
    return [
        {"name": "approve", "signature": "approve(address,uint256)", "attributes": "public inherited ERC721", "classification": classify("approve")},
        {"name": "setApprovalForAll", "signature": "setApprovalForAll(address,bool)", "attributes": "public inherited ERC721", "classification": classify("setApprovalForAll")},
        {"name": "transferFrom", "signature": "transferFrom(address,address,uint256)", "attributes": "public inherited ERC721", "classification": classify("transferFrom")},
        {"name": "safeTransferFrom", "signature": "safeTransferFrom(address,address,uint256)", "attributes": "public inherited ERC721", "classification": classify("safeTransferFrom")},
        {"name": "safeTransferFrom", "signature": "safeTransferFrom(address,address,uint256,bytes)", "attributes": "public inherited ERC721", "classification": classify("safeTransferFrom")},
    ]


def detects_asset_holding(contract_name, text):
    cleaned = strip_comments(text)
    if any(word in contract_name for word in ASSET_WORDS):
        return True
    if "safeTransferFrom" in cleaned and "address(this)" in cleaned:
        return True
    if "transferFrom" in cleaned and "address(this)" in cleaned:
        return True
    if "receive() external payable" in cleaned or "msg.value" in cleaned:
        return True
    return False


def excluded_mainnet_inventory_path(rel):
    return (
        rel.startswith("contracts/test/")
        or rel.startswith("contracts/test-harnesses/")
        or rel == "contracts/token/MockAGIALPHA.sol"
    )


def selector_key(item):
    return item.get("signature") or item["name"]


def merge_funcs(primary, inherited):
    seen = {selector_key(item) for item in primary}
    return primary + [item for item in inherited if selector_key(item) not in seen]


def contracts():
    out = []
    goalos_funcs, goalos_roles = inherited_goalos_surface()
    erc721_funcs = inherited_erc721_surface()
    for rel in tracked_contract_paths():
        if excluded_mainnet_inventory_path(rel):
            continue
        text = git_index_text(rel)
        infos = concrete_contract_infos(text)
        if not infos:
            continue
        for info in infos:
            funcs = functions_from_body(info["body"])
            roles = roles_from_body(info["body"])
            if "GoalOSAccessControl" in info["bases"]:
                funcs = merge_funcs(funcs, goalos_funcs)
                roles = sorted(set(roles + goalos_roles))
            if "ERC721" in info["bases"]:
                funcs = merge_funcs(funcs, erc721_funcs)
            name = info["name"]
            deployment_names = TOKEN_RESERVE_VAULT_ALIASES if name == "TokenReserveVault" else (name,)
            for deployment_name in deployment_names:
                out.append({
                    "path": rel,
                    "contract": deployment_name,
                    "sourceContract": name,
                    "deploymentAlias": deployment_name if deployment_name != name else None,
                    "sha256": sha_bytes(git_index_bytes(rel)),
                    "stateChangingSelectors": funcs,
                    "roles": roles,
                    "assetHolding": detects_asset_holding(name, text),
                    "assetHoldingEvidence": "token/native inbound flow or asset-bearing name" if detects_asset_holding(name, text) else "none detected",
                    "workflow": bool(funcs) or any(word in deployment_name for word in STATE_WORDS),
                })
    return out


def selector_words(fn):
    return [w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|[0-9]+", fn)]


def classify(fn):
    name = fn.lower()
    words = selector_words(fn)
    if any(x in words for x in ["pause", "unpause", "shutdown", "winddown", "lifecycle"]) or "migrat" in name:
        return "lifecycle_control_or_migration"
    if any(x in words for x in ["recover", "override", "cancel", "resolve", "slash", "refund", "revoke"]):
        return "owner_recovery_or_safe_exit"
    if any(x in words for x in ["grant", "set", "configure"]) or name in ["transferownership", "acceptownership"]:
        return "configuration"
    if any(x in words for x in ["withdraw", "release", "pay", "settle", "return", "unstake", "transfer"]):
        return "safe_exit_or_settlement"
    if any(x in words for x in ["create", "submit", "claim", "deposit", "stake", "reserve", "fund", "approve", "post", "propose"]):
        return "new_obligation_or_risk_increase"
    return "normal_operation_unclassified_review_required"


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def write_md(path, title, lines):
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n")


def generate():
    QA.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    RUNBOOKS.mkdir(parents=True, exist_ok=True)
    ARCHITECTURE.mkdir(parents=True, exist_ok=True)
    OPERATIONS.mkdir(parents=True, exist_ok=True)
    MAINNET_READINESS.mkdir(parents=True, exist_ok=True)
    inv = contracts()
    source_hash = tracked_source_tree_hash()
    inventory = {
        "generatedBy": "scripts/mainnet_operational_readiness.py",
        "sourceTreeHash": source_hash,
        "sourceTreeHashScope": "tracked git index content excluding generated readiness artifacts",
        "contracts": inv,
    }
    write_json(QA / "mainnet-operational-inventory.json", inventory)
    write_json(MAINNET_READINESS / "system-inventory.json", inventory)
    gates = []
    for i, name in enumerate([
        "Ownership continuity",
        "Explicit Business Owner override capability",
        "Company-wide accounting and solvency observability",
        "Recovery, migration, wind-down, and shutdown",
        "Autonomous stateful verification and exact-bytecode assurance",
    ], 1):
        gates.append({
            "gate": i,
            "name": name,
            "status": "PARTIAL",
            "claim": "Repository evidence inventory exists; final PASS requires live/private configuration, fork RPC, and complete adversarial runs. This artifact is claim-bounded and does not assert Mainnet deployment.",
        })
    selector_count = sum(len(c["stateChangingSelectors"]) for c in inv)
    unclassified = [
        {"contract": c["contract"], "path": c["path"], **f}
        for c in inv
        for f in c["stateChangingSelectors"]
        if f["classification"] == "normal_operation_unclassified_review_required"
    ]
    write_json(QA / "mainnet-operational-gap-matrix.json", {
        "sourceTreeHash": source_hash,
        "sourceTreeHashScope": inventory["sourceTreeHashScope"],
        "requirements": gates,
        "selectorCoverage": {
            "stateChangingSelectorCount": selector_count,
            "unclassifiedCount": len(unclassified),
            "unclassified": unclassified,
            "status": "PASS" if not unclassified else "BLOCKED",
        },
        "evidence": ["qa/mainnet-operational-inventory.json"],
    })
    write_md(DOCS / "MAINNET_OPERATIONAL_GAP_MATRIX.md", "Mainnet Operational Gap Matrix", [
        f'- Gate {g["gate"]}: **{g["status"]}** — {g["name"]}. {g["claim"]}' for g in gates
    ])
    write_md(ARCHITECTURE / "CONTRACT_AUTHORITY_INVENTORY.md", "Contract Authority Inventory", [
        f'- `{c["contract"]}` (`{c["path"]}`): roles={", ".join(c["roles"]) or "none"}; mutating selectors={len(c["stateChangingSelectors"])}; assetHolding={c["assetHolding"]}.' for c in inv
    ])
    write_md(ARCHITECTURE / "STATE_MACHINE_INVENTORY.md", "State Machine Inventory", [
        f'- `{c["contract"]}` (`{c["path"]}`): workflow={c["workflow"]}; selector classifications={", ".join(sorted(set(f["classification"] for f in c["stateChangingSelectors"]))) or "none"}.' for c in inv
    ])
    overrides = [{
        "contract": c["contract"],
        "path": c["path"],
        "ownerRecoveryAction": "See classified selectors; add typed owner override before PASS if no recovery selector exists for a nonterminal state.",
        "evidence": ["source inventory"],
        "testCoverage": "BLOCKED until contract-specific tests are complete",
    } for c in inv if c["workflow"]]
    write_json(QA / "business-override-matrix.json", {"entries": overrides})
    override_lines = [f'- `{e["contract"]}` (`{e["path"]}`): {e["ownerRecoveryAction"]}' for e in overrides]
    write_md(DOCS / "BUSINESS_OVERRIDE_MATRIX.md", "Business Override Matrix", override_lines)
    write_md(OPERATIONS / "BUSINESS_OVERRIDE_MATRIX.md", "Business Override Matrix", override_lines)
    funds = [{
        "contract": c["contract"],
        "path": c["path"],
        "assetHolding": c["assetHolding"],
        "assetHoldingEvidence": c["assetHoldingEvidence"],
        "accountingStatus": "REQUIRES_EXACT_ONCHAIN_STATUS" if c["assetHolding"] else "NOT_ASSET_HOLDING",
    } for c in inv]
    write_json(QA / "funds-and-liabilities-inventory.json", {
        "entries": funds,
        "invariant": "actualBalance >= protectedLiability + requiredReservations + pendingWithdrawals",
    })
    funds_lines = [
        "Per-token accounting is required; unlike tokens must not be value-aggregated.",
        "",
        *[f'- `{e["contract"]}`: {e["accountingStatus"]} ({e["assetHoldingEvidence"]})' for e in funds],
    ]
    write_md(DOCS / "FUNDS_AND_LIABILITIES_MODEL.md", "Funds and Liabilities Model", funds_lines)
    write_md(ARCHITECTURE / "FUNDS_AND_LIABILITIES_INVENTORY.md", "Funds and Liabilities Inventory", funds_lines)
    selector = {
        "sourceTreeHash": source_hash,
        "coverageStatus": "PASS" if not unclassified else "BLOCKED",
        "unclassifiedCount": len(unclassified),
        "selectors": [{"contract": c["contract"], "path": c["path"], **f} for c in inv for f in c["stateChangingSelectors"]],
    }
    write_json(QA / "lifecycle-selector-policy.json", selector)
    write_md(DOCS / "LIFECYCLE_SELECTOR_POLICY.md", "Lifecycle Selector Policy", [
        f'- `{s["contract"]}.{s["name"]}`: `{s["classification"]}`' for s in selector["selectors"]
    ])
    write_json(QA / "controlled-mainnet-canary-template.json", {
        "claimBoundary": "template only; not authorized and not broadcast",
        "limits": {
            "aggregateLiability": "1000000000000000000",
            "perJobReward": "100000000000000000",
            "perBond": "10000000000000000",
            "vaultOutflowPerDay": "100000000000000000",
            "concurrentObligations": 10,
        },
        "zeroMeansUnlimited": False,
    })
    write_md(RUNBOOKS / "MIGRATION_SHUTDOWN_RUNBOOK.md", "Migration and Shutdown Runbook", [
        "1. Enter WindDown; stop new obligations.",
        "2. Resolve protected liabilities and reservations.",
        "3. Verify authority, accounting, and selector-policy roots.",
        "4. Register successor only after release commitments are generated.",
        "5. Move only verified free funds.",
        "6. Final shutdown must fail closed if any liability remains.",
    ])
    write_md(RUNBOOKS / "OWNERSHIP_SAFE_EOA_RUNBOOK.md", "Ownership Safe/EOA Runbook", [
        "Generate transactions with ownership tooling; verify live chainId from provider; Safe-labelled owners must have contract code and Safe-compatible interface; pending owners are non-authoritative until acceptance.",
    ])
    local_checks = [
        {"name": "authority inventory generation", "command": "npm run authority:inventory", "status": "REQUIRED_NOT_RUN_BY_GENERATOR"},
        {"name": "authority policy validation", "command": "npm run authority:policy:validate", "status": "REQUIRED_NOT_RUN_BY_GENERATOR"},
    ]
    release_dirty_paths = release_relevant_dirty_paths()
    release_identity = {
        "schemaVersion": "1.0",
        "commit": "RESOLVED_BY_GIT_CHECKOUT_AT_VALIDATION",
        "branch": sh(["git", "branch", "--show-current"]),
        "commitBindingMode": "self-referential committed evidence uses sourceTreeHash; validators resolve the current git commit at runtime",
        "sourceTreeHash": source_hash,
        "dependencyLockHash": sha_bytes((ROOT / "package-lock.json").read_bytes()) if (ROOT / "package-lock.json").exists() else None,
        "mainnetDeployed": "NO",
        "mainnetVerified": "NO",
        "liveOwnerHandoffComplete": "NO",
        "liveCanaryComplete": "NO",
    }
    write_json(MAINNET_READINESS / "release-identity.json", release_identity)
    gate_requirements = {
        "G1": ["production_owner_config_commitment_valid", "complete_topology_fork_deployment_succeeds", "owner_handoff_readback_succeeds", "unexpected_role_holders_zero", "bootstrap_authority_denied"],
        "G2": ["typed_owner_overrides_present", "generic_arbitrary_executor_absent", "override_replay_rejected", "override_events_and_accounting_proven", "fork_financial_override_evidence_present"],
        "G3": ["asset_holders_registered", "omitted_accounting_components_zero", "all_components_solvent", "malicious_token_suite_passes", "finite_canary_limits_enforced"],
        "G4": ["single_global_lifecycle", "unclassified_selectors_zero", "no_new_obligations_outside_active", "migration_one_time_reconciled_rollbackable", "shutdown_rejects_unresolved_liabilities"],
        "G5": ["critical_high_unresolved_zero", "unit_integration_pass", "state_machine_actions_at_least_1000000", "recorded_seeds_at_least_32", "critical_mutation_kill_rate_100", "independent_builds_match", "recent_complete_topology_mainnet_fork_passes"],
    }
    gate_commands = {
        "G1": ["npm run authority:verify", "npm run ownership:test"],
        "G2": ["npm run business-overrides:test"],
        "G3": ["npm run accounting:test", "npm run accounting:status"],
        "G4": ["npm run lifecycle:test", "npm run lifecycle:status"],
        "G5": ["npm run invariants:release", "npm run differential:test", "npm run mutation:critical", "npm run build:reproducible", "npm run security:docket", "npm run mainnet:fork-rehearsal:release"],
    }
    def gate_report(gate, name, blockers):
        return {
            "gate": gate,
            "name": name,
            "status": "BLOCKED" if blockers else "PASS",
            "releaseIdentity": source_hash,
            "requirements": [{"id": r, "status": "BLOCKED", "evidenceRequired": True} for r in gate_requirements[gate]],
            "evidence": ["qa/mainnet-operational-inventory.json"],
            "commands": gate_commands[gate],
            "failures": [],
            "blockers": blockers,
        }
    gate_reports = {
        "gate-1-authority.json": gate_report("G1", "Business ownership continuity", ["Live/fork Phase A/B authority readback and private Safe/EOA commitment are absent."]),
        "gate-2-overrides.json": gate_report("G2", "Business-owner override plane", ["Typed override coverage remains inventory-derived and requires contract-level execution evidence before PASS."]),
        "gate-3-accounting.json": gate_report("G3", "Accounting solvency and canary limits", ["Exact on-chain accounting readback and canary enforcement evidence are absent."]),
        "gate-4-lifecycle.json": gate_report("G4", "Lifecycle migration wind-down shutdown", ["Global lifecycle selector enforcement and migration/shutdown rehearsal evidence are absent."]),
        "gate-5-assurance.json": gate_report("G5", "Autonomous assurance", ["One-million-action invariant campaign, secondary fuzz engine, mutation suite, independent build comparison, and real Mainnet fork RPC rehearsal are absent."]),
    }
    for filename, report in gate_reports.items():
        write_json(MAINNET_READINESS / filename, report)
    fork_rehearsal = {"status": "BLOCKED", "releaseIdentity": source_hash, "blockers": ["No live Ethereum Mainnet fork RPC/block rehearsal evidence supplied."], "mainnetBroadcastOccurred": False}
    security_docket = {"status": "BLOCKED", "releaseIdentity": source_hash, "blockers": ["Mandatory assurance categories are not all represented by fresh passing evidence."], "commands": []}
    production_readiness = {"status": "BLOCKED", "releaseIdentity": source_hash, "gates": gate_reports, "forkRehearsal": fork_rehearsal, "securityDocket": security_docket, "MAINNET_DEPLOYED": "NO", "MAINNET_VERIFIED": "NO", "LIVE_OWNER_HANDOFF_COMPLETE": "NO", "LIVE_CANARY_COMPLETE": "NO"}
    authorization_certificate = {"status": "BLOCKED", "releaseIdentity": source_hash, "authorization": "NOT_AUTHORIZED", "blockers": [b for r in gate_reports.values() for b in r["blockers"]], "mainnetBroadcastOccurred": False}
    write_json(MAINNET_READINESS / "fork-rehearsal.json", fork_rehearsal)
    write_json(MAINNET_READINESS / "security-docket.json", security_docket)
    write_json(MAINNET_READINESS / "production-readiness.json", production_readiness)
    write_json(MAINNET_READINESS / "authorization-certificate.json", authorization_certificate)
    write_md(OPERATIONS / "MONITORING_SPECIFICATION.md", "Monitoring Specification", [
        "Vendor-neutral alerts must watch ownership events, role changes, overrides, lifecycle transitions, treasury rotation, transfers, liability/free-balance changes, solvency deviations, blocked duplicate settlement attempts, failed transfers, migration, shutdown, pending ownership, code/configuration mismatch, RPC divergence, and invariant/accounting sentinel failure.",
    ])
    write_md(OPERATIONS / "INCIDENT_RESPONSE.md", "Incident Response", [
        "Use Owner-only typed recovery paths; preserve evidence hashes; avoid Mainnet broadcast from CI; never withdraw protected liabilities as free funds; keep MAINNET_DEPLOYED/VERIFIED as NO until chain-1 evidence exists.",
    ])
    write_json(QA / "monitoring-event-catalog.json", {"schemaVersion":"1.0","events":["OwnershipTransferStarted","OwnershipTransferAccepted","RoleGranted","RoleRevoked","BusinessOverrideExecuted","LifecycleTransition","SolvencyDeviation","MigrationStarted","MigrationRolledBack","ShutdownRequested","ShutdownFinalized"],"vendor":"neutral"})

    dossier = {
        "status": "BLOCKED",
        "reason": "Fail-closed dossier: mandatory live/private fork RPC, independent build comparison, symbolic execution, critical mutation, and exact Mainnet-fork evidence must be supplied before PASS. No Mainnet broadcast evidence is present or claimed.",
        "sourceTreeHash": source_hash,
        "sourceTreeHashScope": inventory["sourceTreeHashScope"],
        "baselineSha": sh(["git", "rev-parse", "HEAD"]),
        "releaseRelevantDirtyPaths": release_dirty_paths,
        "selectorCoverageStatus": selector["coverageStatus"],
        "localCheckResults": local_checks,
        "mainnetBroadcastOccurred": False,
        "releaseClaimBoundary": "Repository-local operational inventory and fail-closed readiness evidence only; not Mainnet deployed, not Mainnet verified, not Owner-authorized, and not technically ready until blocked evidence is supplied.",
        "artifacts": [
            "qa/mainnet-operational-gap-matrix.json",
            "qa/business-override-matrix.json",
            "qa/funds-and-liabilities-inventory.json",
            "qa/lifecycle-selector-policy.json",
            "qa/controlled-mainnet-canary-template.json",
            "qa/mainnet-readiness/release-identity.json",
            "qa/mainnet-readiness/production-readiness.json",
            "qa/mainnet-readiness/authorization-certificate.json",
        ],
    }
    write_json(QA / "mainnet-production-readiness-dossier.json", dossier)
    return dossier


def validate():
    dossier = generate()
    print(json.dumps(dossier, indent=2, sort_keys=True))
    return 2 if dossier["status"] != "PASS" else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    sys.exit(validate() if args.validate else (generate() and 0))
