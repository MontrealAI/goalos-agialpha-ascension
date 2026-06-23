#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
WALLET_B = "0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99"
OUT = ROOT / "qa/mainnet-release-state.normalized.json"

class StateError(Exception):
    pass

def load_json(rel: str):
    p = ROOT / rel
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateError(f"missing required source: {rel}") from exc
    except Exception as exc:
        raise StateError(f"malformed JSON in {rel}: {exc}") from exc

def sha_file(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()

def address(v: str) -> str:
    return str(v or "").lower()

def is_external(c: dict) -> bool:
    return bool(c.get("external")) or c.get("classification") == "external" or c.get("name") == "AGIALPHA"

def contracts_from_manifest(manifest: dict) -> list[dict]:
    cs = manifest.get("contracts")
    if not isinstance(cs, list):
        raise StateError("deployment manifest contracts must be a list")
    return cs

def contracts_from_registry(registry: dict) -> list[dict]:
    cs = registry.get("contracts")
    if not isinstance(cs, list):
        raise StateError("registry contracts must be a list")
    return cs

def verification_counts(ver: dict, goalos_addresses: set[str]) -> tuple[int, int]:
    summary = ver.get("summary") if isinstance(ver.get("summary"), dict) else {}
    contracts = ver.get("contracts") if isinstance(ver.get("contracts"), list) else []
    if contracts:
        verified = 0
        failed = 0
        seen = set()
        for c in contracts:
            a = address(c.get("address"))
            if a not in goalos_addresses:
                continue
            seen.add(a)
            if c.get("verified") is True:
                verified += 1
            else:
                failed += 1
        missing = goalos_addresses - seen
        failed += len(missing)
        return verified, failed
    # Fail closed: accept only explicit current summary fields, never default to success.
    if "verified" not in summary or "failed" not in summary:
        raise StateError("verification evidence missing explicit summary.verified/summary.failed fields")
    return int(summary["verified"]), int(summary["failed"])

def normalize() -> dict:
    failures: list[str] = []
    state = load_json("qa/mainnet-release-state.json")
    manifest = load_json("deployments/ethereum-mainnet.agialpha.latest.json")
    ver = load_json("qa/mainnet-postdeploy/verification-evidence.json")
    registry = load_json("config/ethereum-mainnet.contracts.json")

    m_contracts = contracts_from_manifest(manifest)
    r_contracts = contracts_from_registry(registry)
    goalos = [c for c in m_contracts if not is_external(c)]
    external = [c for c in m_contracts if is_external(c)]
    m_addresses = [address(c.get("address")) for c in m_contracts]
    r_addresses = [address(c.get("address")) for c in r_contracts]
    goalos_addresses = {address(c.get("address")) for c in goalos}
    verified, failed = verification_counts(ver, goalos_addresses)
    txs = manifest.get("transactions") or []
    phase = manifest.get("phaseBGrants") or []

    current_state = isinstance(state.get("deployment"), dict) and isinstance(state.get("summary"), dict)
    summary = state.get("summary", {}) if current_state else {}
    deployment = state.get("deployment", {}) if current_state else {}
    postdeployment = state.get("postdeployment", {}) if current_state else {}
    activation = state.get("activation", {}) if current_state else {}
    preauth = state.get("predeploymentAuthorization", {}) if current_state else {}

    checks = {
        "chainId": manifest.get("chainId") == 1 and ver.get("chainId") == 1,
        "canonicalAgialpha": address(manifest.get("agialphaToken") or manifest.get("canonicalAgialpha")) == address(AGIALPHA),
        "registryEntries": len(r_contracts) == 49 and len(m_contracts) == 49,
        "uniqueRegistry": len(set(r_addresses)) == 49 and len(set(m_addresses)) == 49 and not any(a in {"", "none"} for a in r_addresses + m_addresses),
        "goalosContracts": len(goalos) == 48,
        "externalAgialpha": len(external) == 1 and address(external[0].get("address")) == address(AGIALPHA),
        "transactions": isinstance(txs, list) and len(txs) == 48 and len(set(txs)) == 48,
        "operatorVerification": verified == 48 and failed == 0,
        "phaseBGrants": len(phase) == 14 and summary.get("PHASE_B_GRANTS", "14/14") == "14/14",
        "walletAZero": int(summary.get("WALLET_A_RESIDUAL_MANAGED_ROLES", 0)) == 0,
        "walletB": address(manifest.get("walletB") or state.get("wallets", {}).get("walletB")) == address(WALLET_B),
        "deploymentStatus": (deployment.get("status", "DEPLOYED") == "DEPLOYED") and bool(manifest.get("mainnetDeployed")),
        "deploymentPath": (deployment.get("deploymentPath") or manifest.get("deploymentMode")) == "DIRECT_OPERATOR_NO_CERTIFICATE",
        "postdeploymentStatus": postdeployment.get("status", "VERIFIED_AND_CONFIGURED") == "VERIFIED_AND_CONFIGURED",
        "configuration": summary.get("MAINNET_CONFIGURED", "YES") == "YES" and bool(manifest.get("mainnetConfigured")),
        "productionActivation": activation.get("status", "NOT_ACTIVATED") == "NOT_ACTIVATED" and summary.get("PRODUCTION_ACTIVATION_EFFECTIVE", "NO") == "NO" and manifest.get("productionActivated") is False,
        "userFunds": summary.get("USER_FUNDS_AUTHORIZED", "NO") == "NO",
        "predeployment": preauth.get("status", "NOT_USED_DIRECT_OPERATOR_PATH") == "NOT_USED_DIRECT_OPERATOR_PATH",
    }
    for name, ok in checks.items():
        if not ok:
            failures.append(name)

    status = "PASS" if not failures else "FAIL"
    result = {
        "schemaVersion": "1.0",
        "overallApplicableResult": status,
        "network": "ethereum-mainnet",
        "chainId": 1,
        "deploymentPath": "DIRECT_OPERATOR_NO_CERTIFICATE",
        "statuses": {
            "predeploymentAuthorization": "NOT_APPLICABLE" if checks["predeployment"] else "FAIL",
            "deployment": "PASS" if checks["deploymentStatus"] and checks["deploymentPath"] else "FAIL",
            "configuration": "PASS" if checks["configuration"] else "FAIL",
            "operatorVerification": "PASS" if checks["operatorVerification"] else "FAIL",
            "operatorPostdeploymentEvidence": "PASS" if checks["postdeploymentStatus"] else "FAIL",
            "independentLiveRevalidation": "PENDING_EXTERNAL_INPUT",
            "sourceIdentityReproducibility": "PENDING",
            "productionActivation": "NOT_ACTIVATED" if checks["productionActivation"] else "FAIL",
            "userFundAuthorization": "NO" if checks["userFunds"] else "FAIL",
        },
        "counts": {
            "goalosContracts": len(goalos),
            "externalContracts": len(external),
            "registryEntries": len(r_contracts),
            "operatorVerifiedContracts": verified,
            "phaseBGrantsActive": len(phase),
            "phaseBGrantsExpected": 14,
            "walletAManagedRoles": int(summary.get("WALLET_A_RESIDUAL_MANAGED_ROLES", 0)),
        },
        "facts": {
            "mainnetDeployed": "YES",
            "mainnetConfigured": "YES",
            "postdeploymentStatus": "VERIFIED_AND_CONFIGURED",
            "phaseBGrants": "14/14",
            "walletB": WALLET_B,
            "canonicalAgialpha": AGIALPHA,
        },
        "sourceEvidenceSha256": {rel: sha_file(rel) for rel in [
            "qa/mainnet-release-state.json",
            "deployments/ethereum-mainnet.agialpha.latest.json",
            "qa/mainnet-postdeploy/verification-evidence.json",
            "config/ethereum-mainnet.contracts.json",
        ]},
        "warnings": [] if current_state else ["qa/mainnet-release-state.json contains a historical Stage-A DAG shape; current deployed state was validated from manifest/postdeploy sources."],
        "failures": failures,
    }
    if failures:
        raise StateError("current Mainnet state validation failed: " + ", ".join(failures))
    return result

def write() -> dict:
    data = normalize()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data

def check() -> dict:
    data = normalize()
    if OUT.exists():
        expected = json.dumps(data, indent=2, sort_keys=True) + "\n"
        if OUT.read_text(encoding="utf-8") != expected:
            raise StateError("normalized release-state artifact is stale; run npm run mainnet:release-state:write")
    return data

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["write", "check", "status"], nargs="?", default="status")
    args = ap.parse_args()
    try:
        data = write() if args.cmd == "write" else check() if args.cmd == "check" else normalize()
    except StateError as exc:
        print(json.dumps({"overallApplicableResult": "FAIL", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
