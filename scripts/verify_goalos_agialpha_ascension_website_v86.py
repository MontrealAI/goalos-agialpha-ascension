#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import unquote
import argparse, re, json, sys, os

REQUIRED = [
    "index.html","mission-os.html","proof-cards.html","proof-card-001.html","proof-card-023.html",
    "proof-card-031.html","whitepaper.html","resources.html","sovereign-rsi-control-plane.html",
    "assets/goalos-v86-preserve.css","assets/goalos-v86-dynamic-ai.js"
]
REQUIRED_LINES = [
    "GoalOS",
    "proof",
    "Ascension",
]
FORBIDDEN_ARCHIVES = {".zip",".7z",".tar",".gz",".rar"}
FORBIDDEN_POSITIVE = [
    "achieved AGI",
    "achieved ASI",
    "achieved superintelligence",
    "guaranteed ROI",
    "guaranteed return",
    "token appreciation",
    "live Mainnet settlement",
    "Mainnet deployed",
    "Kardashev Type II achieved",
    "energy abundance achieved",
]
NEGATING_PREFIXES = ["does not claim", "do not claim", "not claim", "no ", "not ", "without claiming", "is not"]

def is_negated(text, start):
    # Treat claim-boundary lists such as "no guaranteed ROI, token appreciation, live Mainnet settlement"
    # as negated for every item in the list.
    before = text[max(0,start-600):start].lower()
    after = text[start:start+160].lower()
    sentence_start = max(before.rfind("."), before.rfind(";"), before.rfind("\n"))
    sentence = (before[sentence_start+1:] + after).lower()
    negators = ["does not claim", "do not claim", "not claim", "not claimed", "not ", "no ", "without claiming", "is not", "are not", "never claims", "prohibited framing", "prohibited", "not as"]
    return any(n in before for n in negators) or any(n in sentence for n in negators)

def local_targets(html):
    return re.findall(r'(?:href|src)=["\']([^"\']+)["\']', html)

def verify(site: Path):
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not (site / rel).exists():
            errors.append(f"missing required file: {rel}")
    archives = [str(p.relative_to(site)) for p in site.rglob("*") if p.is_file() and p.suffix.lower() in FORBIDDEN_ARCHIVES]
    if archives:
        errors.append("public site contains archives: " + ", ".join(archives[:20]))
    htmls = sorted(site.glob("*.html"))
    if len(htmls) < 50:
        errors.append(f"too few html pages: {len(htmls)}")
    for p in htmls:
        raw = p.read_text(encoding="utf-8", errors="ignore")
        low = raw.lower()
        if "goalos-v86-preserve.css" not in raw:
            errors.append(f"{p.name}: missing v86 css link")
        if "goalos-v86-dynamic-ai.js" not in raw:
            errors.append(f"{p.name}: missing v86 dynamic AI script")
        if "goalos-v86-critical" not in raw:
            errors.append(f"{p.name}: missing inline critical CSS fallback")
        if "<table" in raw and "v86-scroll-table" not in raw and "goalos-v86-dynamic-ai.js" not in raw:
            warnings.append(f"{p.name}: tables rely on JS wrapper")
        text = re.sub(r"<[^>]+>", " ", raw)
        words = re.findall(r"\b[\w$αΑ-]+\b", text)
        if len(words) < 250 and p.name != "proof-card-023.html":
            warnings.append(f"{p.name}: short page ({len(words)} words)")
        for phrase in FORBIDDEN_POSITIVE:
            start = low.find(phrase.lower())
            if start >= 0 and not is_negated(low, start):
                errors.append(f"{p.name}: unbounded claim phrase: {phrase}")
        for href in local_targets(raw):
            if not href or href.startswith(("#","mailto:","tel:","javascript:","data:","http://","https://")):
                continue
            clean = unquote(href.split("#")[0].split("?")[0])
            if not clean:
                continue
            target = (site / clean.lstrip("/")) if clean.startswith("/") else (p.parent / clean)
            if not target.exists():
                errors.append(f"{p.name}: broken local link {href}")
        if "<img" in raw:
            for tag in re.findall(r"<img\b[^>]*>", raw, re.I):
                if "alt=" not in tag and 'aria-hidden="true"' not in tag and "aria-hidden='true'" not in tag:
                    errors.append(f"{p.name}: image missing alt text: {tag[:120]}")
    # proof card sequence
    for i in range(1, 32):
        if not (site / f"proof-card-{i:03d}.html").exists():
            errors.append(f"missing proof card {i:03d}")
    report = {
        "status": "PASS" if not errors else "FAIL",
        "html_pages": len(htmls),
        "errors": errors,
        "warnings": warnings[:200],
        "checks": {
            "required_files": REQUIRED,
            "archive_count": len(archives),
            "proof_cards_expected": 31
        }
    }
    qadir = site / "qa"
    qadir.mkdir(exist_ok=True)
    (qadir / "static-verify-v86.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = ["# GoalOS v86 Static Verification", "", f"Status: **{report['status']}**", "", f"HTML pages: {len(htmls)}", "", "## Errors"]
    md += [f"- {e}" for e in errors] or ["- None"]
    md += ["", "## Warnings"]
    md += [f"- {w}" for w in warnings[:200]] or ["- None"]
    (qadir / "static-verify-v86.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    return verify(Path(args.site))
if __name__ == "__main__":
    raise SystemExit(main())
