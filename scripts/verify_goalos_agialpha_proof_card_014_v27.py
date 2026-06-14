#!/usr/bin/env python3
from pathlib import Path
import argparse
import re

PAGES = [f"proof-card-{i:03d}.html" for i in range(1, 15)] + [
    "index.html",
    "proof-cards.html",
    "agialpha-ledger-route.html",
    "sovereign-rsi-control-plane.html",
    "evidence-docket.html",
]
FORBIDDEN = ["recursive.com", "recursive-org", "@Recursive_SI", "Launching Recursive", "First Steps Toward Automated AI Research"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    missing = [p for p in PAGES if not (site / p).exists()]
    if missing:
        raise SystemExit("Missing pages: " + ", ".join(missing))
    index = (site / "index.html").read_text(encoding="utf-8", errors="replace")
    gallery = (site / "proof-cards.html").read_text(encoding="utf-8", errors="replace")
    for i in range(1, 15):
        href = f"proof-card-{i:03d}.html"
        if href not in index and href not in gallery:
            raise SystemExit(f"{href} not linked from index or gallery")
        txt = (site / href).read_text(encoding="utf-8", errors="replace")
        for marker in ["AGIALPHA", "Evidence Docket", "RSI", "Claim boundary"]:
            if marker not in txt:
                raise SystemExit(f"{href} missing marker {marker}")
        if "<style>" not in txt:
            raise SystemExit(f"{href} missing inline CSS fallback")
        if txt.count("<table") < 3:
            raise SystemExit(f"{href} needs multiple substantial tables")
        if "<svg" not in txt:
            raise SystemExit(f"{href} needs visual SVG/flowchart")
    pc14 = (site / "proof-card-014.html").read_text(encoding="utf-8", errors="replace")
    for marker in [
        "AI-Startup Category Dominance Engine",
        "Sovereign Category Board",
        "AEPCategoryDominanceRegistry",
        "AEPRevenueProofRegistry",
        "AEPDistributionChannelRegistry",
        "Kardashev Type II",
    ]:
        if marker not in pc14:
            raise SystemExit(f"Proof Card 014 missing marker: {marker}")
    all_txt = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in site.glob("*.html"))
    for bad in FORBIDDEN:
        if bad.lower() in all_txt.lower():
            raise SystemExit(f"Forbidden named-competitor reference found: {bad}")
    if re.search(r"PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=", all_txt, re.I):
        raise SystemExit("Secret-like string found")
    print("Proof Card 014 v27 verification passed: Proof Cards 001-014 are linked, styled, illustrated, and substantial.")

if __name__ == "__main__":
    main()
