#!/usr/bin/env python3
from __future__ import annotations
import datetime
import hashlib
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
CACHE_PATH = ROOT / "qa/public-agialpha-token-code-evidence.json"
OUT_PATH = ROOT / "qa/public-agialpha-token-verification.json"
REPORT_PATH = ROOT / "docs/AGIALPHA_TOKEN_VERIFICATION_REPORT.md"
RPC_ENDPOINTS = [
    "https://ethereum-rpc.publicnode.com",
    "https://rpc.flashbots.net",
    "https://cloudflare-eth.com",
]


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha_text(value: str) -> str:
    return "0x" + hashlib.sha256(value.encode()).hexdigest()


def read_json(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def valid_hash(value: object) -> bool:
    return isinstance(value, str) and value.startswith("0x") and len(value) == 66 and value.lower() != "0x" + "0" * 64 and value.lower() != "0x" + "1" * 64


def fetch_code(endpoint: str) -> tuple[str | None, dict]:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [AGIALPHA, "latest"]}).encode()
    req = urllib.request.Request(endpoint, data=payload, headers={"content-type": "application/json", "user-agent": "goalos-public-token-verifier/1.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())
    if data.get("error"):
        return None, {"method": f"{endpoint} eth_getCode", "status": "ERROR", "error": data["error"]}
    code = data.get("result")
    if isinstance(code, str) and code != "0x":
        return code, {"method": f"{endpoint} eth_getCode", "status": "PASSED", "codeSha256": sha_text(code)}
    return None, {"method": f"{endpoint} eth_getCode", "status": "NO_CODE"}


def cache_is_valid(cache: dict) -> bool:
    return (
        cache.get("redacted") is True
        and cache.get("containsSecrets") is False
        and cache.get("containsPrivateAddresses") is False
        and cache.get("chain") == "ethereum"
        and cache.get("chainId") == 1
        and str(cache.get("agialphaToken", "")).lower() == AGIALPHA.lower()
        and cache.get("addressHasCode") is True
        and valid_hash(cache.get("codeSha256"))
        and cache.get("evidenceSource") in {"live-public-read-only-rpc", "public-explorer-manual"}
    )


def write_report(report: dict) -> None:
    (ROOT / "qa").mkdir(exist_ok=True)
    (ROOT / "docs").mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    REPORT_PATH.write_text(
        "# AGIALPHA Token Verification Report\n\n"
        f"Status: **{report['status']}**\n\n"
        f"Verification mode: **{report['verificationMode']}**\n\n"
        f"Canonical Ethereum Mainnet AGIALPHA token: `{AGIALPHA}`.\n\n"
        "This checker only passes with live public read-only code evidence or a committed cached public code evidence artifact. "
        "A transient public RPC failure alone is not accepted as proof.\n"
    )


def main() -> None:
    methods: list[dict] = []
    code_hash: str | None = None
    mode = "none"
    for endpoint in RPC_ENDPOINTS:
        try:
            code, method = fetch_code(endpoint)
            methods.append(method)
            if code:
                code_hash = sha_text(code)
                mode = "live-public-read-only-rpc"
                cache = {
                    "redacted": True,
                    "containsSecrets": False,
                    "containsPrivateAddresses": False,
                    "chain": "ethereum",
                    "chainId": 1,
                    "agialphaToken": AGIALPHA,
                    "addressHasCode": True,
                    "codeSha256": code_hash,
                    "evidenceSource": mode,
                    "observedAt": now(),
                    "sourceMethod": method["method"],
                }
                CACHE_PATH.write_text(json.dumps(cache, indent=2) + "\n")
                break
        except Exception as exc:
            methods.append({"method": f"{endpoint} eth_getCode", "status": "UNAVAILABLE", "error": str(exc)[:160]})

    if not code_hash:
        cache = read_json(CACHE_PATH)
        if cache_is_valid(cache):
            code_hash = cache["codeSha256"]
            mode = "cached-public-code-evidence"
            methods.append({"method": str(CACHE_PATH.relative_to(ROOT)), "status": "PASSED_CACHED_PUBLIC_CODE_EVIDENCE", "codeSha256": code_hash})

    status = "PASSED" if code_hash else "FAILED"
    report = {
        "redacted": True,
        "containsSecrets": False,
        "containsPrivateAddresses": False,
        "status": status,
        "verificationMode": mode,
        "chain": "ethereum",
        "chainId": 1,
        "agialphaToken": AGIALPHA,
        "addressHasCode": bool(code_hash),
        "codeSha256": code_hash,
        "contractTreatedAsExistingAgialphaToken": bool(code_hash),
        "newAgialphaTokenDeployed": False,
        "mockAgialphaUsedOnMainnet": False,
        "methods": methods,
        "generatedAt": now(),
        "blockers": [] if code_hash else ["No live public RPC code evidence and no valid cached public token-code evidence artifact."],
    }
    write_report(report)
    print(json.dumps(report, indent=2))
    if status != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
