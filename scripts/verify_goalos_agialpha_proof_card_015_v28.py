#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    if not site.exists():
        fail(f"Missing site directory: {site}")
    required = ["index.html","proof-cards.html","agialpha-ledger-route.html","sovereign-rsi-control-plane.html","evidence-docket.html"] + [f"proof-card-{i:03d}.html" for i in range(1,16)]
    for name in required:
        if not (site/name).exists():
            fail(f"Missing required page: {name}")
    index = (site/"index.html").read_text(encoding="utf-8", errors="replace")
    gallery = (site/"proof-cards.html").read_text(encoding="utf-8", errors="replace")
    for i in range(1,16):
        target = f"proof-card-{i:03d}.html"
        if target not in index:
            fail(f"Homepage does not link {target}")
        if target not in gallery:
            fail(f"Gallery does not link {target}")
        txt = (site/target).read_text(encoding="utf-8", errors="replace")
        for marker in ["<style", "AGIALPHA", "Evidence Docket", "RSI", "Claim boundary", "<table", "<svg"]:
            if marker not in txt:
                fail(f"{target} missing marker: {marker}")
    all_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in site.glob("*.html"))
    if re.search(r"PRIVATE_KEY|SEED_PHRASE|MNEMONIC|DEPLOYER_PRIVATE_KEY|MAINNET_RPC_URL=", all_text, re.I):
        fail("Potential secret-like text found")
    if re.search(r"recursive\.com|recursive-org", all_text, re.I):
        fail("Named competitor URL/repo reference found")
    print("Main website Proof Cards 001-015 verification passed.")
if __name__ == "__main__":
    main()
