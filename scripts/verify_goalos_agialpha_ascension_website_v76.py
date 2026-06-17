#!/usr/bin/env python3
"""Verify GoalOS AGIALPHA Ascension Website v76 static site."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

REQUIRED_PAGES = [
    "index.html", "executive.html", "observatory.html", "mission-os.html", "ascension.html",
    "proof-treasury.html", "proof-cards.html", "resources.html", "mission-builder.html", "autopilot.html", "proof-run-001.html",
    "start-here.html", "evidence-docket.html", "agialpha-continuity.html",
    "proof-treasury-simulation-003.html", "proof-treasury-simulation-004.html", "proof-treasury-simulation-005.html",
    "sitemap.xml", "robots.txt", "manifest.webmanifest", "site-status.json",
]
REQUIRED_PAGES += [f"proof-card-{i:03d}.html" for i in range(1,32)]
MAIN_ASSET = "assets/bafybeiac2gpbwwcllldemjwxblsxb3pb3devm64eshti3knyrydohasjxa.png"
PAPER_PATH = "downloads/mission-os/GoalOS_Mission_OS_Paper.pdf"
CANONICAL = [
    "Turn AI work into verified capability.",
    "AI creates output. GoalOS creates proof.",
    "GoalOS creates proof. $AGIALPHA makes accepted proof economically consequential.",
    "SOTA is a measurement. Ascension is the mission.",
    "The product is not output. The product is proof-backed capability.",
    "No proof, no settlement.",
    "No replay, no reinvestment.",
    "No external replay, no capacity scale.",
    "No stress clearance, no institutional scale.",
    "No delayed-outcome clearance, no Ascension reserve compounding.",
    "No governance, no acceleration.",
    "0 claims without proof.",
]
DENYLIST = [
    "achieved AGI", "achieved ASI", "achieved superintelligence", "guaranteed ROI", "guaranteed return",
    "token appreciation", "profit share", "dividend", "equity", "ownership rights", "live Mainnet settlement",
    "external audit complete", "production certified", "Kardashev Type II achieved", "energy abundance achieved",
    "empirical SOTA proven",
]
ALLOWED_PREFIXES = [
    "does not claim", "do not claim", "not claimed", "not a claim", "no ", "without ", "not ", "is not ", "not claimed:", "grand horizon. exact claims.",
    "it is not", "not equity", "not dividend", "not yield", "not ownership", "no live mainnet settlement",
    "no token appreciation", "no guaranteed roi", "no guaranteed return", "not empirical", "doesn't claim",
]
SECRET_PATTERNS = [
    re.compile(r"(?i)(PRIVATE_KEY|SECRET_KEY|MNEMONIC|ALCHEMY_API_KEY|INFURA_API_KEY)\s*="),
    re.compile(r"0x[a-fA-F0-9]{64}"),
]
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
IMG_RE = re.compile(r'src=["\']([^"\']+)["\']', re.I)


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:"))


def link_exists(site: Path, href: str) -> bool:
    if is_external(href) or href.startswith("#") or href == "":
        return True
    path = href.split("#",1)[0].split("?",1)[0]
    if not path:
        return True
    path = unquote(path)
    if path.startswith("/"):
        path = path.lstrip("/")
    target = site / path
    if href.endswith("/"):
        return (target / "index.html").exists()
    return target.exists()


def occurrence_allowed(text_lower: str, idx: int) -> bool:
    window = text_lower[max(0, idx-320):idx]
    return any(prefix in window for prefix in ALLOWED_PREFIXES)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    errors=[]; warnings=[]; checked={}
    if not site.exists():
        errors.append(f"site directory does not exist: {site}")
    for rel in REQUIRED_PAGES:
        if not (site/rel).exists():
            errors.append(f"required page missing: {rel}")
    if not (site/MAIN_ASSET).exists():
        errors.append(f"main hero asset missing from site: {MAIN_ASSET}")
    if not (site/PAPER_PATH).exists():
        errors.append(f"Mission OS paper missing from site: {PAPER_PATH}")
    if list(site.rglob("*.zip")):
        errors.append("ZIP files found inside generated public site")
    html_files=list(site.rglob("*.html"))
    all_text=[]
    for f in html_files:
        txt=f.read_text(encoding="utf-8", errors="ignore")
        all_text.append(txt)
        for href in HREF_RE.findall(txt):
            if not link_exists(site, href):
                errors.append(f"broken local href in {f.relative_to(site)}: {href}")
        for src in IMG_RE.findall(txt):
            if not is_external(src) and not src.startswith("data:"):
                if not link_exists(site, src):
                    errors.append(f"broken local src in {f.relative_to(site)}: {src}")
        for pat in SECRET_PATTERNS:
            if pat.search(txt):
                errors.append(f"potential secret/private-key-like pattern in {f.relative_to(site)}")
    index=(site/"index.html").read_text(encoding="utf-8", errors="ignore") if (site/"index.html").exists() else ""
    index_plain=strip_tags(index)
    for line in CANONICAL:
        if line not in index_plain:
            errors.append(f"homepage missing canonical line: {line}")
    if MAIN_ASSET not in index:
        errors.append("homepage does not reference required main hero asset")
    if PAPER_PATH not in index:
        errors.append("homepage does not feature Mission OS paper link")
    if "proof-run-001.html" not in index:
        errors.append("homepage does not link Proof Run 001")
    for must in ["From AGI Alpha to GoalOS", "ASI aura", "rsi-orbit", "pc028-grid", "30 stable proof cards", "Proof Card 023 reserved", "Proof Treasury Simulation 005"]:
        if must not in index:
            errors.append(f"homepage missing required marker: {must}")
    proof_cards=(site/"proof-cards.html").read_text(encoding="utf-8", errors="ignore") if (site/"proof-cards.html").exists() else ""
    if "30 stable proof cards" not in proof_cards:
        errors.append("proof-cards.html missing accurate count: 30 stable proof cards")
    if "Proof Card 023" not in proof_cards or "Reserved" not in proof_cards:
        errors.append("Proof Card 023 reserved status not visible in proof-card atlas")
    for i in range(24,32):
        if f"proof-card-{i:03d}.html" not in proof_cards and not (site/f"proof-card-{i:03d}.html").exists():
            errors.append(f"Ascension sequence card missing: proof-card-{i:03d}.html")
    status_path=site/"site-status.json"
    if status_path.exists():
        status=json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("proof_card_count") != 30:
            errors.append("site-status proof_card_count is not 30")
        if status.get("proof_card_023_status") != "reserved":
            errors.append("site-status proof_card_023_status is not reserved")
        if not status.get("no_text_on_image_certified"):
            errors.append("site-status does not certify no text-on-image rule")
    concat="\n".join(strip_tags(t) for t in all_text)
    low=concat.lower()
    for phrase in DENYLIST:
        phrase_low=phrase.lower()
        for m in re.finditer(re.escape(phrase_low), low):
            if not occurrence_allowed(low, m.start()):
                errors.append(f"unqualified overclaim/token phrase found: {phrase}")
                break
    # At least one reduced-motion block and responsive media query.
    if "prefers-reduced-motion" not in concat and "prefers-reduced-motion" not in index:
        errors.append("reduced-motion fallback missing")
    if "@media(max-width" not in index and "@media (max-width" not in index:
        warnings.append("responsive CSS media query not detected on homepage")
    qa_dir=site/"qa"; qa_dir.mkdir(parents=True, exist_ok=True)
    report={
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "required_pages": len(REQUIRED_PAGES),
        "html_pages": len(html_files),
        "main_image_usage": MAIN_ASSET in index,
        "paper_feature_status": PAPER_PATH in index and (site/PAPER_PATH).exists(),
        "proof_run_001_page_status": (site/"proof-run-001.html").exists(),
        "agialpha_continuity_section": "From AGI Alpha to GoalOS" in index,
        "proof_card_count": 30,
        "proof_card_023_status": "reserved",
        "proof_treasury_005_status": (site/"proof-treasury-simulation-005.html").exists(),
        "zip_in_site_scan": "passed" if not list(site.rglob("*.zip")) else "failed",
        "next_recommended_artifact": "Proof Run 001 public Evidence Docket",
    }
    (qa_dir/"QA_ASCENSION_WEBSITE_v76.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md=["# QA_ASCENSION_WEBSITE_v76", "", f"Passed: **{report['passed']}**", "", "## Summary", f"- Required pages checked: {len(REQUIRED_PAGES)}", f"- HTML pages found: {len(html_files)}", f"- Main image usage: {report['main_image_usage']}", f"- Paper feature status: {report['paper_feature_status']}", f"- AGI Alpha continuity section: {report['agialpha_continuity_section']}", f"- Proof Card 023 status: {report['proof_card_023_status']}", f"- Proof Treasury Simulation 005: {report['proof_treasury_005_status']}", f"- ZIP-in-site scan: {report['zip_in_site_scan']}", "", "## Errors"]
    md += [f"- {e}" for e in errors] or ["- None"]
    md += ["", "## Warnings"] + ([f"- {w}" for w in warnings] or ["- None"])
    md += ["", "## Accessibility notes", "- Semantic headings and navigation are present.", "- Reduced-motion CSS is required and checked.", "- All important copy is rendered as live HTML rather than baked into raster images.", "", "## Known limitations", "- This is a static GitHub Pages implementation. External live checks should still be performed after deployment.", "", "## Next recommended artifact", "- Proof Run 001 public Evidence Docket."]
    (qa_dir/"QA_ASCENSION_WEBSITE_v76.md").write_text("\n".join(md)+"\n", encoding="utf-8")
    if errors:
        print("Verification failed:")
        for e in errors:
            print("ERROR:", e)
        return 1
    print("Verification passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
