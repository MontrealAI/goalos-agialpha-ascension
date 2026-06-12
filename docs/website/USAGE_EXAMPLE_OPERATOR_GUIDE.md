# Website Usage Example Operator Guide

## Purpose

This add-on adds a clear, public usage example to the GoalOS AGIALPHA Ascension website without replacing the existing site.

The example is **Proof Card 001 — The Support-to-Trust Workflow**.

## Why this example

Everyone understands customer support. That makes it the best first public explanation of GoalOS + AGIALPHA:

- GoalOS improves a workflow.
- AGIALPHA coordinates proof work.
- A reviewer validates the evidence.
- A Proof Card makes the improvement understandable.
- A credential and reputation update make the contributor legible.
- Private buyer data stays off-chain.

## What to upload

Upload the contents of `UPLOAD_TO_GITHUB/` into the root of the repository.

This includes:

- `.github/workflows/autonomous-github-pages.yml` — patched existing website workflow.
- `.github/workflows/usage-example-website-smoke-test.yml` — build-only smoke test.
- `scripts/add_goalos_agialpha_usage_example_to_site.py` — additive page generator.
- `scripts/build_goalos_agialpha_usage_example_preview.py` — local/smoke-test builder.
- `scripts/verify_goalos_agialpha_usage_example_site.py` — verifier.
- `docs/examples/proof-card-001-support-to-trust-workflow.md` — source story.
- `data/examples/proof-card-001-support-to-trust-workflow.json` — source data.

## What the action produces

- `usage-example.html`
- `proof-card-001.html`
- `proof-mission-001.html`
- `share.html`
- `data/usage-example-proof-card-001.json`
- a homepage feature panel
- sitemap entries

## Safe operating rule

The example is public and illustrative until replaced by a live Evidence Docket.

Do not claim:

- achieved AGI
- investment return
- mainnet deployment
- legal approval
- tax approval
- security approval
- live customer result

## Recommended run order

1. Run `Proof Card 001 Usage Example Smoke Test`.
2. Review the uploaded artifact.
3. Run `Premium Autonomous GitHub Pages Website`.
4. Open the public site.
5. Confirm the homepage, usage example, Proof Card 001, and share page appear.

## Best public copy

GoalOS turns AI work into proof: one support workflow improves, proof validates it, reputation compounds it.
