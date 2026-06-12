#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys

REQUIRED = [
    "index.html",
    "usage-example.html",
    "proof-card-001.html",
    "proof-mission-001.html",
    "share.html",
    "data/usage-example-proof-card-001.json",
    "data/usage-example-site-manifest.json",
]
MUST_CONTAIN = {
    "usage-example.html": ["Proof Card 001", "GoalOS", "AGIALPHA", "The intelligence stays private", "proof becomes verifiable"],
    "proof-card-001.html": ["Support-to-Trust Workflow", "review", "credential", "reputation"],
    "proof-mission-001.html": ["Sponsor", "Builder", "Reviewer"],
    "share.html": ["Share", "GoalOS turns AI work into proof"],
    "index.html": ["Proof Card 001", "Support-to-Trust Workflow"],
}
# We allow safe claim-boundary language such as "does not claim achieved AGI".
# These patterns only catch affirmative prohibited claims in generated example pages.
FORBIDDEN_AFFIRMATIVE = [
    "we achieved agi",
    "guaranteed return",
    "guaranteed roi",
    "mainnet is deployed",
    "legally approved",
    "tax approved",
    "security approved",
]
EXAMPLE_PAGES = ["usage-example.html", "proof-card-001.html", "proof-mission-001.html", "share.html"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    errors = []
    for rel in REQUIRED:
        if not (site / rel).exists():
            errors.append(f"Missing required file: {rel}")
    for rel, needles in MUST_CONTAIN.items():
        p = site / rel
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            for needle in needles:
                if needle not in text:
                    errors.append(f"{rel} missing text: {needle}")
            if rel in EXAMPLE_PAGES:
                low = text.lower()
                for bad in FORBIDDEN_AFFIRMATIVE:
                    if bad in low:
                        errors.append(f"{rel} contains affirmative prohibited claim: {bad}")
    data_path = site / "data/usage-example-proof-card-001.json"
    if data_path.exists():
        data = json.loads(data_path.read_text(encoding="utf-8"))
        boundary = data.get("claimBoundary", {})
        if any(boundary.get(k) is True for k in boundary):
            errors.append("Claim boundary contains a true prohibited claim flag")
    if errors:
        print("Usage example website verification failed:")
        for e in errors:
            print("-", e)
        sys.exit(1)
    print("Usage example website verification passed.")

if __name__ == "__main__":
    main()
