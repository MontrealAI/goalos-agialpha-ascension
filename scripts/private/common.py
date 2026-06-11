from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
PRIVATE = ROOT / ".private"
QA = ROOT / "qa"
AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
SENSITIVE_KEYS = ("PRIVATE_KEY", "RPC_URL", "ETHERSCAN_API_KEY", "SIGNATURE", "MNEMONIC", "SEED")
HEX32_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return "0x" + hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes()) if path.exists() else "0x" + "0" * 64


def sha256_json(data: Any) -> str:
    return sha256_bytes(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def read_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def write_json(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def load_env(path: pathlib.Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", default=".private/mainnet-operator.env")
    p.add_argument("--input", default=".private/mainnet-operator-input.json")
    return p


def public_base() -> dict[str, Any]:
    return {
        "redacted": True,
        "containsSecrets": False,
        "containsPrivateAddresses": False,
        "chain": "ethereum",
        "chainId": 1,
        "agialphaToken": AGIALPHA,
        "commit": git_commit(),
        "generatedAt": now(),
    }


def non_placeholder(value: object) -> bool:
    text = str(value or "").strip()
    return bool(text) and not text.startswith("PRIVATE_LOCAL_ONLY") and text not in {"<REDACTED>", "REDACTED", ""}


def assert_private_path(path: pathlib.Path) -> None:
    resolved = path.resolve()
    if PRIVATE.resolve() not in resolved.parents and resolved != PRIVATE.resolve():
        raise SystemExit("Private operator scripts only read/write under .private/ for private artifacts.")


def refuse_to_print_secret(value: object) -> str:
    text = str(value or "")
    if len(text) <= 8:
        return "***"
    return text[:4] + "…" + text[-4:]


def public_safe(data: dict[str, Any]) -> bool:
    text = json.dumps(data, sort_keys=True).upper()
    return (
        data.get("redacted") is True
        and data.get("containsSecrets") is False
        and data.get("containsPrivateAddresses") is False
        and not any(key in text for key in SENSITIVE_KEYS)
    )


def valid_hash(value: object) -> bool:
    return isinstance(value, str) and bool(HEX32_RE.fullmatch(value)) and value.lower() != "0x" + "0" * 64
