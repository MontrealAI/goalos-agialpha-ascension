#!/usr/bin/env python3
"""Generate fail-closed five-gate Mainnet readiness evidence.

This command intentionally does not broadcast transactions and does not turn
missing live/fork/private evidence into PASS. It binds generated reports to the
tracked release-relevant source tree and records precise blockers.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "mainnet-readiness"
LEGACY = ROOT / "scripts" / "mainnet_operational_readiness.py"
RELEASE_ROOTS = ("contracts/","scripts/","test/","qa/","docs/","schemas/","ignition/","package.json","package-lock.json","hardhat.config.ts","foundry.toml","tsconfig.json")
GENERATED = ("qa/mainnet-readiness/","qa/mainnet-operational", "qa/mainnet-production-readiness-dossier.json", "qa/business-override-matrix.json", "qa/funds-and-liabilities-inventory.json", "qa/lifecycle-selector-policy.json", "qa/controlled-mainnet-canary-template.json", "docs/MAINNET_OPERATIONAL_GAP_MATRIX.md", "docs/BUSINESS_OVERRIDE_MATRIX.md", "docs/FUNDS_AND_LIABILITIES_MODEL.md", "docs/LIFECYCLE_SELECTOR_POLICY.md")


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"command":" ".join(cmd), "exitCode":p.returncode, "outputSha256":hashlib.sha256(p.stdout.encode()).hexdigest(), "outputTail":p.stdout[-4000:]}

def sh(cmd):
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()

def maybe_sh(cmd):
    try: return sh(cmd)
    except Exception as e: return f"UNAVAILABLE: {e}"

def write(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n")

def file_hash(rel):
    p=ROOT/rel
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None

def tracked_files():
    return [x for x in maybe_sh(["git","ls-files"]).splitlines() if x]

def tree_hash():
    h=hashlib.sha256()
    for rel in tracked_files():
        if not rel.startswith(RELEASE_ROOTS): continue
        if rel.startswith(GENERATED): continue
        blob=subprocess.check_output(["git","show",f":{rel}"], cwd=ROOT)
        h.update(rel.encode()+b"\0"+hashlib.sha256(blob).hexdigest().encode()+b"\n")
    return h.hexdigest()

def dirty():
    diff=maybe_sh(["git","diff","--name-only"])
    if diff.startswith("UNAVAILABLE"): return [diff]
    return sorted([x for x in diff.splitlines() if x.startswith(RELEASE_ROOTS) and not x.startswith(GENERATED)])

def release_identity():
    files=[x for x in tracked_files() if x.startswith(RELEASE_ROOTS) and not x.startswith(GENERATED)]
    obj={
      "schema":"goalos.mainnetReadiness.releaseIdentity.v1",
      "commitSha": maybe_sh(["git","rev-parse","HEAD"]),
      "branch": maybe_sh(["git","branch","--show-current"]),
      "sourceTreeHash": tree_hash(),
      "dependencyLockHash": file_hash("package-lock.json"),
      "packageJsonHash": file_hash("package.json"),
      "nodeVersion": maybe_sh(["node","-v"]),
      "npmVersion": maybe_sh(["npm","-v"]),
      "solcPackageVersion": maybe_sh(["node","-e","console.log(require('solc').version())"]),
      "releaseRelevantDirtyPaths": dirty(),
      "fileInventorySha256": hashlib.sha256("\n".join(files).encode()).hexdigest(),
      "generatedAtUnix": int(time.time()),
      "claimBoundary": "No Ethereum Mainnet deployment, verification, live owner handoff, live canary, private signer action, or chain-1 transaction is claimed.",
    }
    obj["releaseIdentity"] = hashlib.sha256(json.dumps({k:v for k,v in obj.items() if k not in {"generatedAtUnix","releaseIdentity"}}, sort_keys=True).encode()).hexdigest()
    return obj

REQS={
"G1":["Complete-topology owner readback", "two-step ownership tests", "Safe/EOA payload evidence", "no residual deployer authority"],
"G2":["Typed owner overrides", "replay protection", "historically explicit exceptional states", "financial idempotency tests"],
"G3":["Per-token O(1) accounting", "system accounting lens", "finite canary limits enforced on-chain", "malicious-token tests"],
"G4":["Global lifecycle controller", "selector policy coverage", "zero-liability migration", "liability-safe terminal shutdown"],
"G5":["1,000,000 action stateful campaign", "differential model", "100% critical mutation kill", "independent build bytecode comparison", "recent real Mainnet fork rehearsal"]
}

def gate(g, status, rid, evidence, commands, blockers):
    return {"gate":g,"status":status,"releaseIdentity":rid["releaseIdentity"],"requirements":REQS[g],"evidence":evidence,"commands":commands,"failures":[],"blockers":blockers}

def generate(run_checks=False):
    OUT.mkdir(parents=True, exist_ok=True)
    rid=release_identity(); write("release-identity.json", rid)
    legacy = run([sys.executable, str(LEGACY)])
    inventory_path = ROOT/"qa/mainnet-operational-inventory.json"
    inventory = json.loads(inventory_path.read_text()) if inventory_path.exists() else {"contracts":[]}
    write("system-inventory.json", {"releaseIdentity":rid["releaseIdentity"], "legacyInventory":"qa/mainnet-operational-inventory.json", "contractCount":len(inventory.get("contracts",[])), "inventory":inventory})
    cmds=[legacy]
    if run_checks:
        for c in (["npm","run","compile:ci"],["npm","run","test:ci"]): cmds.append(run(c))
    shared_blockers=["No real Ethereum Mainnet fork RPC rehearsal evidence supplied in this environment", "No private owner/Safe signer configuration or live owner signature supplied", "No chain-1 deployment or verification evidence supplied; live statuses remain NO/LIVE_PENDING"]
    gates={
      "gate-1-authority.json": gate("G1","BLOCKED",rid,["qa/mainnet-operational-inventory.json","test/ownershipHandoff.test.ts","test/ownershipCommandCenter.test.ts"],cmds,shared_blockers),
      "gate-2-overrides.json": gate("G2","FAIL",rid,["qa/business-override-matrix.json"],cmds,["Current matrix is inventory/documentation oriented; not every nonterminal workflow has typed Solidity override coverage proven by tests"]),
      "gate-3-accounting.json": gate("G3","FAIL",rid,["qa/funds-and-liabilities-inventory.json","qa/controlled-mainnet-canary-template.json"],cmds,["Canary limits are templated/readiness evidence; full on-chain enforcement and system lens are not proven for every asset holder"]),
      "gate-4-lifecycle.json": gate("G4","FAIL",rid,["qa/lifecycle-selector-policy.json","docs/runbooks/MIGRATION_SHUTDOWN_RUNBOOK.md"],cmds,["Global lifecycle and selector enforcement are not proven across every mutating selector"]),
      "gate-5-assurance.json": gate("G5","BLOCKED",rid,["package.json","hardhat.config.ts","foundry.toml"],cmds,["Mandatory million-action campaign, second fuzzing engine, symbolic category, mutation suite, and real fork rehearsal are not all available/executed"]),
    }
    for name,obj in gates.items(): write(name,obj)
    fork={"status":"BLOCKED","releaseIdentity":rid["releaseIdentity"],"mainnetBroadcastOccurred":False,"forkMainnet":False,"blockers":["MAINNET_RPC_URL/HARDHAT_FORK_MAINNET rehearsal was not executed by this generator; local chain cannot satisfy authorization-grade fork evidence"]}; write("fork-rehearsal.json",fork)
    security={"status":"BLOCKED","releaseIdentity":rid["releaseIdentity"],"commands":cmds,"blockers":["Security docket records executed local commands only; unavailable mandatory categories remain blockers"],"toolCategories":{"unitIntegration":"RECORDED_IF_RUN","statefulFuzz":"BLOCKED","staticAnalysis":"BLOCKED_UNLESS_AUDIT_COMMANDS_RUN","symbolic":"BLOCKED","differential":"BLOCKED","mutation":"BLOCKED","secretScanning":"BLOCKED_UNLESS_AUDIT_COMMANDS_RUN","bytecodeGasSize":"BLOCKED","forkRehearsal":"BLOCKED"}}; write("security-docket.json",security)
    statuses=[x["status"] for x in gates.values()]+[fork["status"],security["status"]]
    prod={"status":"BLOCKED" if any(s!="PASS" for s in statuses) else "PASS", "technicalReadiness":"NO", "releaseIdentity":rid["releaseIdentity"], "gateStatuses":{v["gate"]:v["status"] for v in gates.values()}, "MAINNET_DEPLOYED":"NO","MAINNET_VERIFIED":"NO","LIVE_OWNER_HANDOFF_COMPLETE":"NO","LIVE_CANARY_COMPLETE":"NO","mainnetBroadcastOccurred":False,"blockers":[b for v in gates.values() for b in v["blockers"]]}; write("production-readiness.json",prod)
    cert={"status":"NOT_AUTHORIZED","releaseIdentity":rid["releaseIdentity"],"authorizationWordingEmitted":False,"reason":"Five-gate dossier is not all PASS; fail-closed certificate refuses controlled Mainnet authorization.","productionReadiness":"qa/mainnet-readiness/production-readiness.json","claimBoundary":rid["claimBoundary"]}; write("authorization-certificate.json",cert)
    return prod

def validate():
    prod=generate(False)
    print(json.dumps(prod, indent=2, sort_keys=True))
    return 0 if prod["status"] == "PASS" else 2

if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("command", choices=["generate","validate","security-docket","fork-rehearsal","certificate","certificate-validate"], nargs="?", default="generate"); ap.add_argument("--run-checks", action="store_true")
    a=ap.parse_args()
    if a.command in {"validate","certificate-validate"}: sys.exit(validate())
    prod=generate(a.run_checks)
    print(json.dumps(prod if a.command!="certificate" else json.loads((OUT/"authorization-certificate.json").read_text()), indent=2, sort_keys=True))
    sys.exit(0 if a.command in {"generate","security-docket","fork-rehearsal","certificate"} else 2)
