#!/usr/bin/env python3
"""Fail-closed cross-check for GoalOS public Mainnet website inputs.

Read-only. This command never opens a wallet, contacts an RPC endpoint, or
sends a blockchain transaction.
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
MISSION_ID = "GOALOS-PUBLIC-PROOF-MISSION-001"
FORBIDDEN_MARKERS = (
    "private_mainnet_deployer_private_key",
    "mainnet_deployer_private_key",
    "mainnet_rpc_url=",
    "private_mainnet_rpc_url=",
    "etherscan_api_key=",
    "seed_phrase",
    "mnemonic",
)


def load(path: Path) -> Any:
    if not path.is_file():
        raise ValueError(f"missing required source: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_registry(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise ValueError("canonical registry must be an object")
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    chain_id = data.get("chainId", metadata.get("chainId"))
    if chain_id != 1:
        raise ValueError("canonical registry must describe chainId 1")
    raw_contracts = data.get("contracts")
    if not isinstance(raw_contracts, list) or len(raw_contracts) != 49:
        raise ValueError("canonical registry must contain exactly 49 entries")

    result: list[dict[str, Any]] = []
    names: set[str] = set()
    addresses: set[str] = set()
    for raw in raw_contracts:
        if not isinstance(raw, dict):
            raise ValueError("canonical registry entry must be an object")
        name, address = raw.get("name"), raw.get("address")
        if not isinstance(name, str) or not name:
            raise ValueError("canonical registry entry has no name")
        if not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
            raise ValueError(f"invalid canonical address for {name}")
        if raw.get("chainId", chain_id) != 1:
            raise ValueError(f"wrong chainId for {name}")

        classification = raw.get("classification")
        if classification not in {"deployed", "external"}:
            if raw.get("external") is True and raw.get("deployedByGoalOS") is False:
                classification = "external"
            elif raw.get("external") is False and raw.get("deployedByGoalOS") is True:
                classification = "deployed"
            else:
                raise ValueError(f"cannot classify canonical registry entry {name}")

        key = address.lower()
        if name in names or key in addresses:
            raise ValueError(f"duplicate canonical registry entry: {name} / {address}")
        names.add(name)
        addresses.add(key)
        result.append({"name": name, "address": address, "classification": classification})

    deployed = [item for item in result if item["classification"] == "deployed"]
    external = [item for item in result if item["classification"] == "external"]
    if len(deployed) != 48 or len(external) != 1:
        raise ValueError("canonical registry must contain 48 GoalOS entries and 1 external dependency")
    if external[0]["name"] != "AGIALPHA" or external[0]["address"].lower() != CANONICAL_AGIALPHA.lower():
        raise ValueError("canonical AGIALPHA dependency is incorrect")
    return result


def normalized_pairs(entries: Any) -> set[tuple[str, str]]:
    if not isinstance(entries, list):
        raise ValueError("contract collection must be a list")
    pairs: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("contract collection entry must be an object")
        name, address = entry.get("name"), entry.get("address")
        if not isinstance(name, str) or not isinstance(address, str) or not ADDRESS_RE.fullmatch(address):
            raise ValueError(f"invalid contract collection entry: {name!r}")
        pair = (name, address.lower())
        if pair in pairs:
            raise ValueError(f"duplicate contract collection pair: {name}")
        pairs.add(pair)
    return pairs


def reject_private_material(value: Any, label: str) -> None:
    serialized = json.dumps(value, sort_keys=True).lower()
    for marker in FORBIDDEN_MARKERS:
        if marker in serialized:
            raise ValueError(f"{label} contains forbidden private-operator marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/ethereum-mainnet.contracts.json")
    parser.add_argument("--release-contracts", default="release/mainnet-2026-06-21/CONTRACTS_MAINNET.json")
    parser.add_argument("--proof-snapshot", default="data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    parser.add_argument("--proof-content", default="content/proof-gradient-sovereign.json")
    parser.add_argument("--out", default="site/qa/unified-public-source-validation.json")
    args = parser.parse_args()

    registry_path = Path(args.registry)
    release_contracts_path = Path(args.release_contracts)
    snapshot_path = Path(args.proof_snapshot)
    content_path = Path(args.proof_content)

    registry = normalized_registry(load(registry_path))
    release_contracts = load(release_contracts_path)
    snapshot = load(snapshot_path)
    content = load(content_path)

    expected_pairs = {(item["name"], item["address"].lower()) for item in registry}
    if normalized_pairs(release_contracts) != expected_pairs:
        raise ValueError("release contract registry differs from canonical registry")

    if not isinstance(snapshot, dict):
        raise ValueError("Proof Gradient Mainnet snapshot must be an object")
    reject_private_material(snapshot, "Proof Gradient Mainnet snapshot")
    if normalized_pairs(snapshot.get("contracts")) != expected_pairs:
        raise ValueError("Proof Gradient Mainnet snapshot differs from canonical registry")
    expected_snapshot = {
        "chainId": 1,
        "releaseTag": RELEASE_TAG,
        "deploymentStatus": "CONFIGURED",
        "deploymentMode": "DIRECT_OPERATOR_NO_CERTIFICATE",
        "canonicalAgialpha": CANONICAL_AGIALPHA,
        "goalosCreatedContractCount": 48,
        "manifestEntryCount": 49,
        "creationTransactionCount": 48,
        "phaseBGrantCount": 14,
        "notExternallyAudited": True,
    }
    for key, expected in expected_snapshot.items():
        actual = snapshot.get(key)
        if isinstance(expected, str) and key == "canonicalAgialpha":
            if str(actual).lower() != expected.lower():
                raise ValueError(f"snapshot {key} mismatch")
        elif actual != expected:
            raise ValueError(f"snapshot {key} expected {expected!r}, got {actual!r}")
    verification = snapshot.get("verification")
    if not isinstance(verification, dict) or verification.get("goalosContracts") != 48 or verification.get("verified") != 48 or verification.get("failed") != 0 or verification.get("complete") is not True:
        raise ValueError("Proof Gradient verification summary must be 48/48 complete with zero failures")
    postcheck = snapshot.get("postcheck")
    if not isinstance(postcheck, dict) or postcheck.get("chainId") != 1 or postcheck.get("checkedContracts") != 48 or postcheck.get("status") != "PASSED" or postcheck.get("failures") not in ([], None):
        raise ValueError("Proof Gradient postcheck must record 48 contracts and PASSED")

    if not isinstance(content, dict):
        raise ValueError("Proof Gradient content must be an object")
    reject_private_material(content, "Proof Gradient public content")
    if content.get("pageVersion") != "sovereign-v3" or content.get("missionId") != MISSION_ID:
        raise ValueError("Proof Gradient content is not Sovereign v3 / Mission 001")
    if not str(content.get("releaseUrl", "")).endswith(f"/releases/tag/{RELEASE_TAG}"):
        raise ValueError("Proof Gradient content release URL mismatch")
    proof_route = content.get("proofRoute")
    if not isinstance(proof_route, list) or len(proof_route) != 15:
        raise ValueError("Proof Gradient proofRoute must contain 15 stages")
    deployed_names = {item["name"] for item in registry if item["classification"] == "deployed"}
    route_names = {str(item.get("contractName")) for item in proof_route if isinstance(item, dict)}
    if not route_names or not route_names.issubset(deployed_names):
        raise ValueError("Proof Gradient proofRoute contains unknown Mainnet contracts")
    if not isinstance(content.get("claimBoundary"), list) or len(content["claimBoundary"]) < 4:
        raise ValueError("Proof Gradient claim boundary is incomplete")

    public_blob = json.dumps(content, sort_keys=True).lower()
    for term in ("third-party competitor", "competitor comparison", " versus ", " vs. "):
        if term in public_blob:
            raise ValueError(f"prohibited public competitor framing: {term}")

    result = {
        "schemaVersion": "1.0",
        "status": "PASS",
        "chainId": 1,
        "releaseTag": RELEASE_TAG,
        "proofGradientEdition": "SOVEREIGN_V3",
        "missionId": MISSION_ID,
        "registryEntries": 49,
        "goalosCreatedContracts": 48,
        "externalDependencies": 1,
        "operatorVerification": "48/48",
        "verificationFailures": 0,
        "phaseBGrants": "14/14",
        "postdeploymentCheck": "48/48 PASS",
        "productionActivation": "NO",
        "userFundAuthorization": "NO",
        "publicNetworkTransactionSent": False,
        "hashes": {
            "canonicalRegistry": sha256(registry_path),
            "releaseContracts": sha256(release_contracts_path),
            "proofSnapshot": sha256(snapshot_path),
            "proofContent": sha256(content_path),
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
