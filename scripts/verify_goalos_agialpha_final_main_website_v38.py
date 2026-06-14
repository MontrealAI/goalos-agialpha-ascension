#!/usr/bin/env python3
from pathlib import Path
import argparse
import re
import sys

REQUIRED = [
    "index.html",
    "start-here.html",
    "personal-proof-sprint.html",
    "proof-sprint-builder.html",
    "autopilot-mission-builder.html",
    "use-cases.html",
    "resources.html",
    "proof-cards.html",
    "agialpha-ledger-route.html",
    "sovereign-rsi-control-plane.html",
    "evidence-docket.html",
    "sitemap.xml",
    "robots.txt",
    "manifest.webmanifest",
    "routes.json",
    "site-status.json",
    ".nojekyll",
]
PROOF_CARDS = [f"proof-card-{i:03d}.html" for i in range(1, 18)]
TEXT_EXTS = {".html",".json",".xml",".txt",".webmanifest",".js",".css",".md"}
SECRET_RE = re.compile(r"(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=|SEPOLIA_RPC_URL=)", re.I)
FORBIDDEN = ["recursive.com", "recursive-org/first-steps-toward-automated-ai-research"]

def read(p):
    return p.read_text(encoding="utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    errors = []
    for name in REQUIRED + PROOF_CARDS:
        if not (site / name).exists():
            errors.append(f"missing required page/file: {name}")

    if (site / "index.html").exists():
        idx = read(site / "index.html")
        for name in ["autopilot-mission-builder.html","start-here.html","personal-proof-sprint.html","use-cases.html","resources.html","proof-cards.html"]:
            if name not in idx:
                errors.append(f"homepage does not link {name}")
        for name in PROOF_CARDS:
            if name not in idx:
                errors.append(f"homepage does not link {name}")

    if (site / "proof-cards.html").exists():
        atlas = read(site / "proof-cards.html")
        for name in PROOF_CARDS:
            if name not in atlas:
                errors.append(f"proof card atlas does not link {name}")

    for name in PROOF_CARDS:
        p = site / name
        if p.exists():
            txt = read(p)
            for term in ["AGIALPHA", "Evidence", "RSI", "<style"]:
                if term not in txt:
                    errors.append(f"{name} missing required term/markup: {term}")

    if (site / "autopilot-mission-builder.html").exists():
        txt = read(site / "autopilot-mission-builder.html")
        for term in ["Mission Builder", "Generate mission JSON", "copyMission", "downloadMission", "AGIALPHA"]:
            if term not in txt:
                errors.append(f"autopilot builder missing {term}")

    for p in site.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS:
            txt = read(p)
            if SECRET_RE.search(txt):
                errors.append(f"secret-like string found in {p.relative_to(site)}")
            low = txt.lower()
            for bad in FORBIDDEN:
                if bad in low:
                    errors.append(f"forbidden competitor reference found in {p.relative_to(site)}")

    if errors:
        print("Verification failed:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("GoalOS AGIALPHA final main website v38 verification passed.")
if __name__ == "__main__":
    main()
