#!/usr/bin/env python3
"""Verify the GoalOS AGIALPHA Ascension Website v75 Apex Pages artifact."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REQUIRED_PAGES = [
    "index.html",
    "whitepaper.html",
    "roadmap.html",
    "biography.html",
    "developers.html",
    "jobs.html",
    "mission-os.html",
    "proof-cards.html",
    "evidence-docket.html",
    "agialpha-ledger-route.html",
    "sovereign-rsi-control-plane.html",
    "ascension.html",
    "proof-treasury.html",
    "resources.html",
    "start-here.html",
    "autopilot-mission-builder.html",
    "mission-os-paper.html",
    "proof-treasury-simulation-003.html",
    "proof-treasury-simulation-004.html",
    "proof-treasury-simulation-005.html",
    "sitemap.xml",
    "robots.txt",
    "manifest.webmanifest",
    "site-status.json",
]
REQUIRED_PAGES += [f"proof-card-{i:03d}.html" for i in range(1, 32)]
REQUIRED_ASSETS = [
    "assets/v75-apex.css",
    "assets/v75-apex.js",
]
REQUIRED_HOME_TEXT = [
    "AI creates output. GoalOS creates proof.",
    "SOTA is a measurement. Ascension is the mission.",
    "proof-governed operating regime",
]
DENYLIST = [
    "achieved AGI",
    "achieved ASI",
    "achieved superintelligence",
    "guaranteed ROI",
    "guaranteed return",
    "investment return",
    "token appreciation",
    "price target",
    "profit share",
    "passive income",
    "revenue share",
    "dividend",
    "equity ownership",
    "live Mainnet settlement",
    "Mainnet deployed: YES",
    "external audit complete",
    "production certified",
    "guaranteed secure",
    "legal approval complete",
    "tax approval complete",
]
SAFE_PREFIXES = [
    "no claim of",
    "no claim",
    "does not claim",
    "do not claim",
    "not claim",
    "not claimed",
    "without claiming",
    "not a claim",
    "no ",
    "not ",
    "never ",
    "forbidden claims",
    "prohibited framing",
    "prohibited",
    "disallowed",
    "claim boundary",
    "doesn’t claim",
    "doesn't claim",
]
SECRET_PATTERNS = [
    re.compile(r"(?i)(PRIVATE_KEY|SECRET_KEY|MNEMONIC|ALCHEMY_API_KEY|INFURA_API_KEY|ETHERSCAN_API_KEY)\s*="),
    re.compile(r"(?i)-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"0x[a-fA-F0-9]{64}"),
]
REF_RE = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']", re.I)
TEXT_SUFFIXES = {".html", ".js", ".css", ".json", ".xml", ".txt", ".md", ".csv", ".webmanifest", ".svg"}


def is_external(ref: str) -> bool:
    return ref.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:"))


def link_exists(site: Path, ref: str) -> bool:
    if not ref or ref.startswith("#") or is_external(ref):
        return True
    path = ref.split("#", 1)[0].split("?", 1)[0]
    if not path:
        return True
    path = unquote(path).lstrip("/")
    target = site / path
    if ref.endswith("/"):
        return (target / "index.html").exists()
    return target.exists()


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def occurrence_is_safe(lower: str, idx: int) -> bool:
    window = lower[max(0, idx - 720):idx]
    return any(prefix in window for prefix in SAFE_PREFIXES)


def scan_denylist(rel: str, text: str, errors: list[str]) -> None:
    lower = strip_tags(text).lower()
    for phrase in DENYLIST:
        start = 0
        needle = phrase.lower()
        while True:
            idx = lower.find(needle, start)
            if idx == -1:
                break
            if not occurrence_is_safe(lower, idx):
                errors.append(f"unsafe public claim phrase in {rel}: {phrase}")
            start = idx + len(needle)


def scan_secrets(rel: str, text: str, errors: list[str]) -> None:
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            errors.append(f"potential secret/private-key-like pattern in {rel}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    args = parser.parse_args()
    site = Path(args.site)
    errors: list[str] = []
    warnings: list[str] = []

    if not site.exists():
        errors.append(f"site directory does not exist: {site}")
    else:
        for rel in REQUIRED_PAGES:
            if not (site / rel).exists():
                errors.append(f"required public page/file missing: {rel}")
        for rel in REQUIRED_ASSETS:
            if not (site / rel).exists():
                errors.append(f"required public asset missing: {rel}")
        if list(site.rglob("*.zip")):
            errors.append("ZIP files found in public site artifact")

        for f in site.rglob("*"):
            if not f.is_file() or f.suffix.lower() not in TEXT_SUFFIXES:
                continue
            rel = str(f.relative_to(site)).replace("\\", "/")
            text = f.read_text(encoding="utf-8", errors="ignore")
            scan_secrets(rel, text, errors)
            scan_denylist(rel, text, errors)
            if f.suffix.lower() == ".html":
                for ref in REF_RE.findall(text):
                    if not link_exists(site, ref):
                        errors.append(f"broken local href/src in {rel}: {ref}")

        index = (site / "index.html").read_text(encoding="utf-8", errors="ignore") if (site / "index.html").exists() else ""
        plain = strip_tags(index)
        for line in REQUIRED_HOME_TEXT:
            if line not in plain:
                errors.append(f"homepage missing required thesis text: {line}")

        qa_json = site / "qa" / "QA_ASCENSION_WEBSITE_v75_APEX.json"
        if not qa_json.exists():
            errors.append("QA manifest missing: qa/QA_ASCENSION_WEBSITE_v75_APEX.json")
        else:
            try:
                manifest = json.loads(qa_json.read_text(encoding="utf-8"))
                if manifest.get("page_count", 0) < 50:
                    warnings.append("QA manifest reports fewer than 50 HTML pages")
            except json.JSONDecodeError as exc:
                errors.append(f"QA manifest is invalid JSON: {exc}")

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("Verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Verification passed for GoalOS AGIALPHA Ascension Website v75 Apex.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
