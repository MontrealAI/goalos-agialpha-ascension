#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPER_ROOT = ROOT / "docs/papers/sovereign-rsi"
V63 = PAPER_ROOT / "v6.3"
ARCHIVE = PAPER_ROOT / "archive"
BASE = "GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI"
CANONICAL = {
    f"{BASE}.md": "canonical-markdown-source",
    f"{BASE}.pdf": "institutional-reading-edition",
    f"{BASE}.docx": "editable-working-edition",
    f"{BASE}.tex": "typesetting-source",
}
SECRET_PATTERNS = [
    re.compile(r"(?:PRIVATE_KEY|SEED_PHRASE|MNEMONIC|ETHERSCAN_API_KEY|FOUNDER_APPROVAL_SIGNATURE)\s*[:=]\s*[^\s\"']+", re.I),
    re.compile(r"https?://[^\s\"']*(?:alchemy|infura|quicknode|ankr|blast|drpc|chainstack)[^\s\"']*", re.I),
    re.compile(r"\b(?:0x)?[0-9a-fA-F]{64}\b.*(?:private|secret|key|signature)", re.I),
]


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_checksums(path: pathlib.Path) -> dict[str, str]:
    sums: dict[str, str] = {}
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"malformed checksum line: {line}")
        digest, rel = parts
        sums[rel.strip().lstrip("*")] = digest
    return sums


def main() -> int:
    errors: list[str] = []
    required = [V63 / "README.md", V63 / "PAPER_ASSET_MANIFEST.json", V63 / "CHECKSUMS.sha256"]
    required.extend(V63 / name for name in CANONICAL)
    for path in required:
        if not path.exists():
            errors.append(f"missing required paper artifact: {path.relative_to(ROOT)}")

    if errors:
        print(json.dumps({"status": "FAILED", "errors": errors}, indent=2))
        return 1

    manifest = json.loads((V63 / "PAPER_ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("version") != "v6.3" or manifest.get("canonical") is not True:
        errors.append("paper manifest must identify canonical v6.3")
    boundary = manifest.get("claimBoundary", {})
    for key in ["achievedAGI", "achievedASI", "achievedSuperintelligence", "empiricalSOTA", "guaranteedEconomicReturn", "legalApproval", "taxApproval", "securityApproval", "energyAbundance", "kardashevTypeIIAchieved"]:
        if boundary.get(key) is not False:
            errors.append(f"claimBoundary.{key} must be false")

    manifest_files = {entry.get("path"): entry for entry in manifest.get("files", []) if isinstance(entry, dict)}
    checksums = parse_checksums(V63 / "CHECKSUMS.sha256")
    for name, role in CANONICAL.items():
        path = V63 / name
        rel = path.relative_to(ROOT).as_posix()
        digest = sha256(path)
        if checksums.get(rel) != digest:
            errors.append(f"checksum mismatch for {rel}")
        entry = manifest_files.get(rel)
        if not entry:
            errors.append(f"manifest missing {rel}")
        else:
            if entry.get("role") != role:
                errors.append(f"manifest role mismatch for {rel}")
            if entry.get("sha256") != digest:
                errors.append(f"manifest sha256 mismatch for {rel}")

    readme = read_text(V63 / "README.md")
    for name in CANONICAL:
        link = f"./{name}"
        if link not in readme:
            errors.append(f"v6.3 README missing exact link {link}")
        if not (V63 / name).exists():
            errors.append(f"v6.3 README link target missing {name}")
    for phrase in ["Claim boundary", "does not claim achieved AGI", "investment return", "legal approval", "tax approval", "security approval"]:
        if phrase not in readme:
            errors.append(f"v6.3 README missing claim-boundary phrase: {phrase}")

    root_readme = read_text(ROOT / "README.md") if (ROOT / "README.md").exists() else ""
    if "## Research paper" not in root_readme:
        errors.append("root README missing research-paper section")
    if "docs/papers/sovereign-rsi/v6.3/GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.md" not in root_readme:
        errors.append("root README does not point to v6.3 paper markdown")

    stale_in_v63 = [p.relative_to(ROOT).as_posix() for p in V63.iterdir() if p.is_file() and ("_v6.1_" in p.name or "_Paper_v5" in p.name)]
    if stale_in_v63:
        errors.append("historical paper assets remain in v6.3 root: " + ", ".join(stale_in_v63))
    if not any((ARCHIVE / "v5").glob("GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_Sovereign_RSI_Paper_v5.*")):
        errors.append("v5 historical assets are not archived under docs/papers/sovereign-rsi/archive/v5")
    if not any((ARCHIVE / "v6.1").glob("GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.1_Sovereign_RSI.*")):
        errors.append("v6.1 historical assets are not archived under docs/papers/sovereign-rsi/archive/v6.1")

    for path in list(V63.glob("*")) + list((ARCHIVE / "v5").glob("*")) + list((ARCHIVE / "v6.1").glob("*")):
        if not path.is_file() or path.suffix.lower() in {".pdf", ".docx"}:
            continue
        text = read_text(path)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"potential private secret in paper file {path.relative_to(ROOT)}")
                break

    out = {
        "status": "PASSED" if not errors else "FAILED",
        "canonicalPaperFolder": V63.relative_to(ROOT).as_posix(),
        "canonicalAssets": sorted(CANONICAL),
        "archivedVersions": ["v5", "v6.1"],
        "errors": errors,
    }
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
