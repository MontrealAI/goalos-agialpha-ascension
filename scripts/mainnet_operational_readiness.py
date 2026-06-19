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
GENERATED_PREFIXES = (
    "qa/mainnet-operational",
    "qa/business-override-matrix.json",
    "qa/funds-and-liabilities-inventory.json",
    "qa/lifecycle-selector-policy.json",
    "qa/controlled-mainnet-canary-template.json",
    "qa/mainnet-production-readiness-dossier.json",
    "docs/MAINNET_OPERATIONAL_GAP_MATRIX.md",
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


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_source_tree_hash():
    """Hash the staged source content, excluding generated readiness outputs.

    The index is used so generated artifacts can be regenerated before commit and
    remain tied to the exact non-generated content that will be committed, while
    unrelated working-tree dirt is ignored.
    """
    listing = sh(["git", "ls-files"])
    h = hashlib.sha256()
    for rel in sorted(x for x in listing.splitlines() if x):
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


def functions_from_body(body):
    funcs = []
    for match in re.finditer(r"function\s+(\w+)\s*\([^)]*\)\s*([^;{]*)", body):
        attrs = match.group(2)
        if any(x in attrs for x in STATE_HINTS) and not any(x in attrs for x in VIEW_HINTS):
            funcs.append({
                "name": match.group(1),
                "attributes": " ".join(attrs.split()),
                "classification": classify(match.group(1)),
            })
    return funcs


def roles_from_body(body):
    return sorted(set(re.findall(r"bytes32\s+(?:public\s+)?(?:constant\s+)?([A-Z0-9_]+_ROLE)", body)))


def inherited_goalos_surface():
    access_path = CONTRACTS / "access" / "GoalOSAccessControl.sol"
    text = access_path.read_text(errors="ignore")
    for block in contract_blocks(text):
        if block["name"] == "GoalOSAccessControl":
            return functions_from_body(block["body"]), sorted(set(roles_from_body(block["body"]) + ["DEFAULT_ADMIN_ROLE"]))
    return [], []


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


def excluded_mainnet_inventory_path(path):
    rel = str(path.relative_to(ROOT))
    return (
        rel.startswith("contracts/test/")
        or rel.startswith("contracts/test-harnesses/")
        or rel == "contracts/token/MockAGIALPHA.sol"
    )


def merge_funcs(primary, inherited):
    seen = {item["name"] for item in primary}
    return primary + [item for item in inherited if item["name"] not in seen]


def contracts():
    out = []
    goalos_funcs, goalos_roles = inherited_goalos_surface()
    for path in sorted(CONTRACTS.rglob("*.sol")):
        if excluded_mainnet_inventory_path(path):
            continue
        text = path.read_text(errors="ignore")
        infos = concrete_contract_infos(text)
        if not infos:
            continue
        for info in infos:
            funcs = functions_from_body(info["body"])
            roles = roles_from_body(info["body"])
            if "GoalOSAccessControl" in info["bases"]:
                funcs = merge_funcs(funcs, goalos_funcs)
                roles = sorted(set(roles + goalos_roles))
            name = info["name"]
            deployment_names = TOKEN_RESERVE_VAULT_ALIASES if name == "TokenReserveVault" else (name,)
            for deployment_name in deployment_names:
                out.append({
                    "path": str(path.relative_to(ROOT)),
                    "contract": deployment_name,
                    "sourceContract": name,
                    "deploymentAlias": deployment_name if deployment_name != name else None,
                    "sha256": sha_file(path),
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
    if any(x in words for x in ["withdraw", "release", "pay", "settle", "return", "unstake"]):
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
    inv = contracts()
    source_hash = tracked_source_tree_hash()
    inventory = {
        "generatedBy": "scripts/mainnet_operational_readiness.py",
        "sourceTreeHash": source_hash,
        "sourceTreeHashScope": "tracked HEAD content excluding generated readiness artifacts",
        "contracts": inv,
    }
    write_json(QA / "mainnet-operational-inventory.json", inventory)
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
    write_json(QA / "mainnet-operational-gap-matrix.json", {
        "sourceTreeHash": source_hash,
        "sourceTreeHashScope": inventory["sourceTreeHashScope"],
        "requirements": gates,
        "evidence": ["qa/mainnet-operational-inventory.json"],
    })
    write_md(DOCS / "MAINNET_OPERATIONAL_GAP_MATRIX.md", "Mainnet Operational Gap Matrix", [
        f'- Gate {g["gate"]}: **{g["status"]}** — {g["name"]}. {g["claim"]}' for g in gates
    ])
    overrides = [{
        "contract": c["contract"],
        "path": c["path"],
        "ownerRecoveryAction": "See classified selectors; add typed owner override before PASS if no recovery selector exists for a nonterminal state.",
        "evidence": ["source inventory"],
        "testCoverage": "BLOCKED until contract-specific tests are complete",
    } for c in inv if c["workflow"]]
    write_json(QA / "business-override-matrix.json", {"entries": overrides})
    write_md(DOCS / "BUSINESS_OVERRIDE_MATRIX.md", "Business Override Matrix", [
        f'- `{e["contract"]}` (`{e["path"]}`): {e["ownerRecoveryAction"]}' for e in overrides
    ])
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
    write_md(DOCS / "FUNDS_AND_LIABILITIES_MODEL.md", "Funds and Liabilities Model", [
        "Per-token accounting is required; unlike tokens must not be value-aggregated.",
        "",
        *[f'- `{e["contract"]}`: {e["accountingStatus"]} ({e["assetHoldingEvidence"]})' for e in funds],
    ])
    selector = {"selectors": [{"contract": c["contract"], "path": c["path"], **f} for c in inv for f in c["stateChangingSelectors"]]}
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
    dossier = {
        "status": "BLOCKED",
        "reason": "Fail-closed dossier: mandatory live/private fork, independent builds, symbolic, mutation, and exact Mainnet-fork evidence must be supplied before PASS. No Mainnet broadcast evidence is present or claimed.",
        "sourceTreeHash": source_hash,
        "sourceTreeHashScope": inventory["sourceTreeHashScope"],
        "artifacts": [
            "qa/mainnet-operational-gap-matrix.json",
            "qa/business-override-matrix.json",
            "qa/funds-and-liabilities-inventory.json",
            "qa/lifecycle-selector-policy.json",
            "qa/controlled-mainnet-canary-template.json",
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
