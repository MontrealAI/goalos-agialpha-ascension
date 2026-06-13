# GoalOS AGIALPHA Proof Card 005 Main Website Integration v11.0

This patch adds **Proof Card 005 - Sovereign RSI Value-to-Capability Treasury** to the main website and keeps Proof Cards 001-004 visible.

## Main website

`https://montrealai.github.io/goalos-agialpha-ascension/`

## What Proof Card 005 adds

Proof Card 004 explained that GoalOS AGIALPHA Ascension can accumulate capabilities, evidence, and economic value over time. Proof Card 005 is incrementally stronger: it explains how **verified value can be governed and reinvested into future capability**.

The key loop is:

```text
verified value -> governed capability budget -> better proof missions -> stronger artifacts -> better future workflows -> more verified value
```

## Upload instructions

Upload the **contents** of `UPLOAD_TO_GITHUB` to the repository root.

Important files:

```text
.github/workflows/autonomous-github-pages.yml
.github/workflows/main-website-proof-card-005-smoke-test.yml
scripts/add_goalos_agialpha_main_site_proof_cards_v11.py
scripts/verify_goalos_agialpha_main_site_proof_cards_v11.py
scripts/patch_existing_pages_workflow_for_proof_cards_v11.py
docs/examples/proof-card-005-sovereign-rsi-value-to-capability-treasury.md
data/examples/proof-card-005-sovereign-rsi-value-to-capability-treasury.json
evidence/examples/proof-card-005-evidence-docket-template.json
```

## Run order

1. GitHub -> Actions.
2. Run **Main Website Proof Card 005 Smoke Test**.
3. If it passes, run **Premium Autonomous GitHub Pages Website**.
4. Open the main website.
5. Confirm Proof Cards 001-005 appear on the homepage and in `proof-cards.html`.

## Expected pages

```text
index.html
proof-cards.html
proof-card-001.html
proof-card-002.html
proof-card-003.html
proof-card-004.html
proof-card-005.html
agialpha-ledger-route.html
sovereign-rsi-control-plane.html
evidence-docket.html
season-001.html
share.html
```

## Public line

GoalOS AGIALPHA Ascension accumulates what proved itself. Proof Card 005 shows how verified value can fund stronger future capability.
