#!/usr/bin/env python3
"""Fail-closed validation for the controlled production canary profile.

This validator intentionally avoids external JSON-schema dependencies so it can run
inside the repository's normal npm command surface. It checks the profile/schema
contract and the release-scope manifest invariants that prevent an unclassified
surface from being treated as production-authorized.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "config/authorization-profiles/controlled-production-canary-v1.json"
SCHEMA_PATH = ROOT / "schemas/authorization-profile.schema.json"
SCOPE_PATH = ROOT / "qa/mainnet-readiness/release-scope-manifest.json"
PROFILE = "CONTROLLED_PRODUCTION_CANARY_V1"
VERSION = "1.0"
CHAIN_ID = 1
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
WALLET_A = "0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E"
WALLET_B = "0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99"


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise AssertionError(f"missing {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    profile = load(PROFILE_PATH)
    schema = load(SCHEMA_PATH)
    scope = load(SCOPE_PATH)

    for key in schema.get("required", []):
        require(key in profile, errors, f"profile missing schema-required key: {key}")

    require(profile.get("authorizationProfile") == PROFILE, errors, "profile authorizationProfile mismatch")
    require(profile.get("profileVersion") == VERSION, errors, "profileVersion must be 1.0")
    require(profile.get("chainId") == CHAIN_ID, errors, "profile chainId must be Ethereum Mainnet (1)")
    require(profile.get("canonicalAgialpha") == AGIALPHA, errors, "profile canonical AGIALPHA mismatch")
    wallets = profile.get("wallets", {})
    require(wallets.get("walletA") == WALLET_A, errors, "Wallet A mismatch")
    require(wallets.get("walletB") == WALLET_B, errors, "Wallet B mismatch")
    profile_text = json.dumps(profile)
    require("0x" + "0" * 64 not in profile_text, errors, "profile must not contain private-key/secret material")

    authorized_actions = profile.get("authorizedActions")
    prohibited_actions = profile.get("prohibitedActions")
    require(isinstance(authorized_actions, list) and authorized_actions, errors, "authorizedActions must be populated")
    require(isinstance(prohibited_actions, list) and prohibited_actions, errors, "prohibitedActions must be populated")
    require("Mainnet broadcast by Codex or CI" in (prohibited_actions or []), errors, "profile must explicitly prohibit Codex/CI Mainnet broadcast")

    limits = profile.get("canaryLimits", {})
    require(limits.get("zeroMeansUnlimited") is False, errors, "zeroMeansUnlimited must be false")
    for name, value in limits.items():
        if name == "zeroMeansUnlimited":
            continue
        try:
            require(int(value) > 0, errors, f"canary limit {name} must be finite and greater than zero")
        except Exception:
            errors.append(f"canary limit {name} must be integer-like")

    require(scope.get("authorizationProfile") == PROFILE, errors, "scope authorizationProfile mismatch")
    require(scope.get("profileVersion") == VERSION, errors, "scope profileVersion must be 1.0")
    require(scope.get("chainId") == CHAIN_ID, errors, "scope chainId must be 1")
    require(scope.get("canonicalAgialpha") == AGIALPHA, errors, "scope canonical AGIALPHA mismatch")
    require(scope.get("unknownOrUnclassifiedSurfaceEnabled") is False, errors, "unclassified surface must not be enabled")
    require(scope.get("economicCaps") == limits, errors, "scope economicCaps must match profile canaryLimits exactly")
    require(AGIALPHA in scope.get("supportedTokens", []), errors, "scope must include canonical AGIALPHA as supported token")

    if errors:
        print(json.dumps({"status": "FAILED", "errors": errors}, indent=2))
        return 1
    print(json.dumps({"status": "PASSED", "profile": PROFILE, "profileVersion": VERSION}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
