#!/usr/bin/env python3
"""Cross-check the public Mainnet and Proof Gradient source snapshots.

Read-only. This script never contacts an RPC endpoint or sends a transaction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
CANONICAL_AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
RELEASE_TAG = "v4.4.0-mainnet-2026-06-21"


def load(path: Path) -> Any:
    if not path.is_file():
        raise ValueError(f"missing required source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_registry(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise ValueError("canonical registry must be an object")
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    if data.get("chainId", metadata.get("chainId")) != 1:
        raise ValueError("canonical registry must describe chainId 1")
    contracts = data.get("contracts")
    if not isinstance(contracts, list) or len(contracts) != 49:
        raise ValueError("canonical registry must contain 49 entries")
    normalized: list[dict[str, Any]] = []
    for raw in contracts:
        if not isinstance(raw, dict):
            raise ValueError("canonical registry entry must be an object")
        name, address = raw.get("name"), raw.get("address")
        if not isinstance(name, str) or not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
            raise ValueError(f"invalid canonical registry entry: {name!r}")
        classification = raw.get("classification")
        if classification not in {"deployed", "external"}:
            if raw.get("external") is True and raw.get("deployedByGoalOS") is False:
                classification = "external"
            elif raw.get("external") is False and raw.get("deployedByGoalOS") is True:
                classification = "deployed"
            else:
                raise ValueError(f"cannot classify canonical registry entry: {name}")
        normalized.append({"name": name, "address": address, "classification": classification})
    return normalized


def normalize_contracts(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        return [{"name": str(name), "address": str(address)} for name, address in raw.items()]
    if isinstance(raw, list):
        result = []
        for item in raw:
            if not isinstance(item, dict) or not item.get("name") or not item.get("address"):
                raise ValueError("snapshot contract entry is invalid")
            result.append(dict(item))
        return result
    raise ValueError("snapshot contracts must be a list or object")


def pair_set(entries: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {(str(item["name"]), str(item["address"]).lower()) for item in entries}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/ethereum-mainnet.contracts.json")
    parser.add_argument("--release-contracts", default="release/mainnet-2026-06-21/CONTRACTS_MAINNET.json")
    parser.add_argument("--proof-snapshot", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    parser.add_argument("--proof-content", default="content/proof-gradient-apex.json")
    parser.add_argument("--out", default="site/qa/unified-public-source-validation.json")
    args = parser.parse_args()

    registry_path = Path(args.registry)
    release_contracts_path = Path(args.release_contracts)
    proof_snapshot_path = Path(args.proof_snapshot)
    proof_content_path = Path(args.proof_content)

    registry = normalize_registry(load(registry_path))
    release_contracts_raw = load(release_contracts_path)
    snapshot = load(proof_snapshot_path)
    content = load(proof_content_path)

    if not isinstance(release_contracts_raw, list) or len(release_contracts_raw) != 49:
        raise ValueError("release contract registry must contain 49 entries")
    snapshot_contracts = normalize_contracts(snapshot.get("contracts") if isinstance(snapshot, dict) else None)
    if len(snapshot_contracts) != 49:
        raise ValueError("Proof Gradient Mainnet snapshot must contain 49 entries")

    # Public website snapshots must not carry disposable signer or secret-bearing fields.
    authority = snapshot.get("authority", {}) if isinstance(snapshot, dict) else {}
    if isinstance(authority, dict) and "deployer" in authority:
        raise ValueError("Proof Gradient public snapshot must omit the disposable deployer address")
    serialized_snapshot = json.dumps(snapshot, sort_keys=True).lower()
    for forbidden_marker in (
        "private_mainnet_deployer_private_key",
        "mainnet_rpc_url=",
        "etherscan_api_key=",
        "seed_phrase",
        "mnemonic",
    ):
        if forbidden_marker in serialized_snapshot:
            raise ValueError(f"Proof Gradient public snapshot contains forbidden operator material: {forbidden_marker}")

    expected = pair_set(registry)
    if pair_set(release_contracts_raw) != expected:
        raise ValueError("release contract registry differs from canonical registry")
    if pair_set(snapshot_contracts) != expected:
        raise ValueError("Proof Gradient Mainnet snapshot differs from canonical registry")

    deployed = [item for item in registry if item["classification"] == "deployed"]
    external = [item for item in registry if item["classification"] == "external"]
    if len(deployed) != 48 or len(external) != 1:
        raise ValueError("canonical registry must contain 48 GoalOS entries and one external dependency")
    if external[0]["name"] != "AGIALPHA" or external[0]["address"].lower() != CANONICAL_AGIALPHA.lower():
        raise ValueError("canonical AGIALPHA entry is incorrect")

    if not isinstance(snapshot, dict) or snapshot.get("chainId") != 1:
        raise ValueError("Proof Gradient snapshot must describe chainId 1")
    if snapshot.get("releaseTag") != RELEASE_TAG:
        raise ValueError("Proof Gradient snapshot release tag mismatch")
    if snapshot.get("deploymentStatus") != "CONFIGURED":
        raise ValueError("Proof Gradient snapshot deployment status must be CONFIGURED")
    if len(snapshot.get("transactions", [])) != 48:
        raise ValueError("Proof Gradient snapshot must contain 48 deployment transactions")
    if len(snapshot.get("phaseBGrants", [])) != 14:
        raise ValueError("Proof Gradient snapshot must contain 14 Phase-B grants")
    if snapshot.get("mockAgialphaUsed") is not False or snapshot.get("newAgialphaTokenDeployed") is not False:
        raise ValueError("Proof Gradient snapshot violates the canonical AGIALPHA boundary")

    if not isinstance(content, dict) or content.get("releaseTag") != RELEASE_TAG:
        raise ValueError("Proof Gradient content release tag mismatch")
    evidence = content.get("evidence", {}).get("verificationSummary", {})
    if evidence.get("manifestEntries") != 49 or evidence.get("goalosCreatedContracts") != 48 or evidence.get("verifiedGoalosContracts") != 48:
        raise ValueError("Proof Gradient content evidence summary is inconsistent")
    if evidence.get("failed") != 0:
        raise ValueError("Proof Gradient content must record zero operator verification failures")

    result = {
        "schemaVersion": "1.0",
        "status": "PASS",
        "chainId": 1,
        "releaseTag": RELEASE_TAG,
        "registryEntries": 49,
        "goalosCreatedContracts": 48,
        "externalDependencies": 1,
        "deploymentTransactions": 48,
        "phaseBGrants": 14,
        "productionActivation": "NO",
        "userFundAuthorization": "NO",
        "publicNetworkTransactionSent": False,
        "hashes": {
            "canonicalRegistry": sha256(registry_path),
            "releaseContracts": sha256(release_contracts_path),
            "proofSnapshot": sha256(proof_snapshot_path),
            "proofContent": sha256(proof_content_path),
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
