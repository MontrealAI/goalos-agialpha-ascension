#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Unable to parse {path}: {exc}")


def run_commands(text: str) -> list[str]:
    commands: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)-?\s*run:\s*(.*?)\s*$", line)
        if not m:
            i += 1
            continue
        base_indent = len(m.group(1))
        raw = m.group(2).strip().strip('\"').strip("'")
        if raw in {"|", ">", "|-", ">-", "|+", ">+"}:
            block: list[str] = []
            i += 1
            while i < len(lines):
                child = lines[i]
                if child.strip() and len(child) - len(child.lstrip()) <= base_indent:
                    break
                block.append(child.strip())
                i += 1
            commands.append("\n".join(block).strip())
            continue
        commands.append(raw)
        i += 1
    return commands


def has_command(commands: list[str], required: str) -> bool:
    return any(cmd == required or required in cmd.split("&&") or required in cmd for cmd in commands)


def hidden_by_true(commands: list[str], required: str) -> bool:
    return any(required in cmd and "|| true" in cmd for cmd in commands)


def validate(policy_path: Path, root: Path = ROOT) -> list[str]:
    policy = load_json(policy_path)
    errors: list[str] = []
    for key in ["schemaVersion", "commands", "workflows"]:
        if key not in policy:
            errors.append(f"workflow policy missing {key}")
    if errors:
        return errors
    positive = set(policy["commands"].get("positiveEnforcement", [])) | {"npm run mainnet:authorization-check"}
    forbidden_secret_names = policy["commands"].get("forbiddenMainnetSecrets", [])
    for entry in policy.get("workflows", []):
        rel = entry.get("path")
        role = entry.get("role")
        if not rel or not role:
            errors.append("workflow policy entry missing path or role")
            continue
        path = root / rel
        if not path.exists():
            errors.append(f"{rel}: missing workflow")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        commands = run_commands(text)
        for required in entry.get("requiredCommands", []):
            if not has_command(commands, required):
                errors.append(f"{rel}: {role} missing required command: {required}")
            if hidden_by_true(commands, required):
                errors.append(f"{rel}: mandatory command hidden by || true: {required}")
        forbidden = set(entry.get("forbiddenCommands", []))
        if role != "PROTECTED_RELEASE":
            forbidden |= positive
        for bad in forbidden:
            if has_command(commands, bad):
                errors.append(f"{rel}: {role} must not run positive authorization command: {bad}")
        if role == "PROTECTED_RELEASE":
            if "workflow_dispatch" not in text:
                errors.append(f"{rel}: PROTECTED_RELEASE must use workflow_dispatch")
            required_env = entry.get("requiredEnvironment")
            if required_env and f"environment: {required_env}" not in text:
                errors.append(f"{rel}: PROTECTED_RELEASE missing environment: {required_env}")
            if entry.get("mustNotBroadcastMainnet"):
                lowered = text.lower()
                live_markers = ["deploy:ethereum-mainnet:gated", "deploy:mainnet:live", "--network ethereummainnet"]
                if any(marker in lowered for marker in live_markers):
                    errors.append(f"{rel}: protected readiness workflow must not contain live mainnet broadcast command")
        for secret in forbidden_secret_names:
            if f"secrets.{secret}" in text:
                errors.append(f"{rel}: workflow references forbidden Mainnet broadcaster secret {secret}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default="qa/workflow-policy.json")
    args = ap.parse_args()
    errors = validate(ROOT / args.policy)
    out = {"status": "passed" if not errors else "failed", "errors": errors}
    print(json.dumps(out, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
