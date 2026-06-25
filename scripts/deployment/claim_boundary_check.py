#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
BLOCKED = [
    "production ready", "externally audited", "guaranteed secure", "guaranteed ROI",
    "achieved AGI", "achieved ASI", "superintelligence achieved", "Kardashev achieved",
    "legal approval complete", "tax approval complete"
]
MAINNET_YES = re.compile(r"Mainnet deployed:\s*YES|MAINNET_DEPLOYED\W+YES|mainnetDeployed\W+YES", re.I)
candidate_names = {"DEPLOYMENT_START_HERE.md", "SEPOLIA_DEPLOYMENT_GUIDE.md", "MAINNET_OPERATOR_RUNBOOK.md", "DEPLOYMENT_TROUBLESHOOTING.md", "DEPLOYMENT_FAQ.md", "DEPLOYMENT_CLAIM_BOUNDARY.md", "SEPOLIA_DEPLOYMENT_REPORT.md", "ETHEREUM_MAINNET_DEPLOYMENT_REPORT.md", "sepolia-deployment-evidence.json", "mainnet-deployment-evidence.json", "ethereum-mainnet.agialpha.latest.json", "ethereum-sepolia.agialpha.latest.json"}
public_copy_bases = ["app", "content", "LOCAL_QA_SITE", "site", "site-assets", "templates"]
public_copy_suffixes = {".html", ".htm", ".md", ".txt", ".json", ".xml", ".webmanifest"}
paths = [p for base in ["docs", "qa", "deployments"] for p in (ROOT/base).rglob("*") if p.is_file() and p.name in candidate_names]
paths += [
    p
    for base in public_copy_bases
    if (ROOT / base).exists()
    for p in (ROOT / base).rglob("*")
    if p.is_file() and p.suffix.lower() in public_copy_suffixes
]
paths += [
    p
    for p in ROOT.iterdir()
    if p.is_file() and p.suffix.lower() in {".html", ".htm"}
]
errors=[]
manifest_path = ROOT / "deployments/ethereum-mainnet.agialpha.latest.json"
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
real_mainnet = manifest.get("chainId") == 1 and manifest.get("status") != "TEMPLATE_NO_DEPLOYMENT" and manifest.get("contracts") and manifest.get("transactions")
CLAIM_BOUNDARY = "This evidence reports Ethereum Mainnet deployment, verification, and configuration mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, user-fund authorization, or production activation."

def safe_negated_line(line: str, phrase: str) -> bool:
    lower = line.lower()
    escaped_phrase = re.escape(phrase.lower())
    scoped_denials = [
        rf"\bdoes\s+not\s+claim\b.*\b{escaped_phrase}\b",
        rf"\bdoes\s+not\s+establish\b.*\b{escaped_phrase}\b",
        rf"\bnot\s+(?:a\s+)?claim\s+of\b.*\b{escaped_phrase}\b",
        rf"\bnot\s+claim\b.*\b{escaped_phrase}\b",
        rf"\bnot\b.{{0,160}}\bproof\s+of\s+{escaped_phrase}\b",
        rf"\bno\s+{escaped_phrase}\b",
        rf"\bnot\s+{escaped_phrase}\b",
        rf"\bwithout\s+{escaped_phrase}\b",
    ]
    return any(re.search(pattern, lower) for pattern in scoped_denials)


def iter_json_strings(value, key_path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_json_strings(child, key_path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_json_strings(child, key_path + (str(index),))
    elif isinstance(value, str):
        yield key_path, value


def is_explicit_not_claimed_context(key_path) -> bool:
    normalized = {
        re.sub(r"[^a-z0-9]+", "_", part.lower()).strip("_")
        for part in key_path
        if not part.isdigit()
    }
    return bool(normalized & {"not_claimed", "claims_not_made", "not_claims", "non_claims"})

for path in paths:
    text = path.read_text(encoding="utf-8", errors="ignore").replace(CLAIM_BOUNDARY, "")
    rel = path.relative_to(ROOT).as_posix()
    parsed_json = None
    if path.suffix.lower() == ".json":
        try:
            parsed_json = json.loads(text)
        except json.JSONDecodeError:
            parsed_json = None
    if parsed_json is not None:
        for key_path, value in iter_json_strings(parsed_json):
            lower = value.lower()
            for phrase in BLOCKED:
                if phrase.lower() not in lower:
                    continue
                if is_explicit_not_claimed_context(key_path) or safe_negated_line(value, phrase):
                    continue
                errors.append(f"Unsafe deployment claim '{phrase}' in {rel}")
    else:
        for phrase in BLOCKED:
            for line in text.splitlines():
                lower = line.lower()
                if safe_negated_line(line, phrase):
                    continue
                if phrase.lower() in lower:
                    errors.append(f"Unsafe deployment claim '{phrase}' in {rel}")
                    break
    if MAINNET_YES.search(text) and not real_mainnet:
        errors.append(f"Unsupported Mainnet deployed YES claim in {rel}")
if errors:
    print("Deployment claim-boundary check failed:")
    for e in sorted(set(errors)): print(f"- {e}")
    sys.exit(1)
print("Deployment claim-boundary check passed.")
