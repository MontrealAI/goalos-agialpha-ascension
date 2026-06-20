#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, re
from pathlib import Path

ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

class OwnerConfigError(ValueError):
    pass

def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def commitment(obj: object) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()

def load_b64(encoded: str) -> dict:
    try:
        raw = base64.b64decode(encoded, validate=True)
        data = json.loads(raw.decode())
    except Exception as exc:
        raise OwnerConfigError(f"invalid base64 JSON owner config: {exc}") from exc
    if not isinstance(data, dict):
        raise OwnerConfigError("owner config must decode to a JSON object")
    return data

def validate_config(data: dict, expected_kind: str | None = None, expected_address: str | None = None) -> dict:
    errors: list[str] = []
    kind = data.get("kind")
    if kind not in {"SAFE", "EOA"}:
        errors.append("kind must be SAFE or EOA")
    if expected_kind and kind != expected_kind:
        errors.append("GOALOS_PRODUCTION_OWNER_KIND does not match private config kind")
    if data.get("chainId") != 1:
        errors.append("chainId must be 1 for Ethereum Mainnet readiness")
    public_address = None
    redacted: dict[str, object] = {"kind": kind, "chainId": data.get("chainId")}
    if kind == "SAFE":
        public_address = data.get("safeAddress")
        if not isinstance(public_address, str) or not ADDRESS_RE.match(public_address):
            errors.append("safeAddress must be an Ethereum address")
        threshold = data.get("expectedThreshold")
        owners = data.get("expectedOwners")
        if not isinstance(threshold, int) or threshold < 1:
            errors.append("expectedThreshold must be a positive integer")
        if not isinstance(owners, list) or not owners:
            errors.append("expectedOwners must be a non-empty array")
        elif any(not isinstance(o, str) or not ADDRESS_RE.match(o) for o in owners):
            errors.append("expectedOwners entries must be Ethereum addresses")
        elif len({o.lower() for o in owners}) != len(owners):
            errors.append("expectedOwners must be unique case-insensitively")
        elif isinstance(threshold, int) and threshold > len(owners):
            errors.append("expectedThreshold cannot exceed expectedOwners length")
        if not isinstance(data.get("safeVersion"), str) or not data.get("safeVersion"):
            errors.append("safeVersion must be pinned")
        if data.get("publishSafeThresholdAndOwnerCount") is True and isinstance(threshold, int) and isinstance(owners, list):
            redacted["safeThreshold"] = threshold
            redacted["safeOwnerCount"] = len(owners)
    elif kind == "EOA":
        public_address = data.get("ownerAddress")
        if not isinstance(public_address, str) or not ADDRESS_RE.match(public_address):
            errors.append("ownerAddress must be an Ethereum address")
        if data.get("hardwareWalletAcknowledgement") is not True:
            errors.append("hardwareWalletAcknowledgement must be true")
    if expected_address and public_address and public_address.lower() != expected_address.lower():
        errors.append("GOALOS_PRODUCTION_OWNER_ADDRESS does not match private config public owner address")
    if expected_address and not ADDRESS_RE.match(expected_address):
        errors.append("GOALOS_PRODUCTION_OWNER_ADDRESS must be an Ethereum address")
    redacted["publicOwnerAddress"] = public_address
    redacted["privateConfigCommitmentSha256"] = commitment(data)
    redacted["validationResult"] = "PASS" if not errors else "FAIL"
    return {"valid": not errors, "errors": errors, "redacted": redacted}
