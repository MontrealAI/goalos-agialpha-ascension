# GoalOS AGIALPHA Ascension First Real Loop ✨

## Purpose

This release reimplements the original **AGI ALPHA First Real Loop** inside the GoalOS AGIALPHA Ascension website as a proof-governed, deterministic, browser-local public experience.

It preserves the original causal sequence:

`Nova-Seed → MARK → Mini Sovereign → five AGI Jobs → Evidence Docket → Capability Compiler → vNext treatment/control`

GoalOS adds explicit mission commitment, constitutional authority limits, artifact hashes, falsification criteria, replay posture, treatment/control comparison, and a terminal human promotion gate.

## Public pages

The autonomous build generates three pages:

- `first-real-loop.html` — flagship experience and interactive proof-cycle command theatre.
- `first-real-loop-architecture.html` — nine-layer constitutional architecture, original-to-GoalOS translation, threat model, and promotion boundary.
- `first-real-loop-docket.html` — searchable twelve-artifact ledger, canonical public manifest, intervention register, downloads, and terminal disposition.

The builder also adds one marked, idempotent gateway to `index.html` and updates only `sitemap.xml` and `site-status.json` among existing generated files.

## What the loop demonstrates

The deterministic reference run contains:

- one committed Nova-Seed: `ColdChain-Energy-Seed-001`;
- one structured MARK review with a 4.67/5 internal score;
- one advisory-only Mini Sovereign;
- five bounded jobs, all recorded as passed;
- twelve curated source records;
- four reviewer-accepted interventions in the top five;
- twelve sealed evidence artifacts;
- one extracted capability compiler: `ColdChain-Energy-Compiler-v0`;
- one lineage-bound successor proposal: `ColdChain-Energy-Seed-002`;
- a treatment/control comparison at equal cost units;
- control yield `0.30`, treatment yield `0.50`, and bounded scaffold reuse lift `66.67%`;
- hallucination delta `0` and safety delta `0`;
- terminal state `HUMAN_REVIEW_REQUIRED`;
- authority `NONE_GRANTED`.

The measured lift is a deterministic reference result from the original loop mechanics. It is not a production, facility, investment, savings, SOTA, AGI, or external-certification claim.

## Eight proof-gated phases

1. **Commit** — seal mission intent, risk envelope, success conditions, and authority ceiling.
2. **Seed** — admit the Nova-Seed foresight genome and five-job graph.
3. **MARK** — adjudicate coherence, evidence, usefulness, safety, reuse, and executability.
4. **Sovereign** — constitute an advisory-only bounded institution.
5. **Work** — execute source discovery, modeling, generation, causal red-team, and ranking.
6. **Proof** — seal provenance, decisions, failures, risks, and accepted artifacts.
7. **Learn** — extract only reusable schemas and rules that survived review.
8. **vNext** — challenge the successor seed against a declared control and stop at human review.

## Twelve-artifact Evidence Docket

The release hashes canonical payloads for:

- Run Manifest
- Nova-Seed 001
- MARK Review
- Mini Sovereign Charter
- Job Graph
- Source Ledger
- Intervention Register
- Capability Compiler v0
- vNext Seed 002
- Treatment / Control
- Falsification Register
- Executive Review Brief

The stable public run commitment is:

`3d1fee22e57444bbca2cdf779b3089a265a9dc2b99539c660d21759a84a13034`

## Browser-local safety boundary

The interactive experience performs no source retrieval, model call, wallet connection, RPC request, peer connection, token movement, settlement, production execution, equipment control, or external action.

The terminal record is intentionally fixed to:

```text
State               HUMAN_REVIEW_REQUIRED
Authority           NONE_GRANTED
External actions    0
Wallet connections  0
Network requests    0
Production          NOT_ACTIVATED
User funds          NO AUTHORIZATION
```

A downloadable browser docket remains a demonstration artifact, not independent factual certification.

## Source files

The feature source is additive:

```text
content/goalos-first-real-loop.json
website/first_real_loop/first-real-loop.css
website/first_real_loop/first-real-loop.js
scripts/website/build_goalos_first_real_loop.py
scripts/website/verify_goalos_first_real_loop.py
scripts/website/browser_check_goalos_first_real_loop.py
schemas/goalos-first-real-loop-evidence-docket.schema.json
test/test_goalos_first_real_loop.py
docs/GOALOS_FIRST_REAL_LOOP_WEBSITE.md
.github/workflows/goalos-first-real-loop-smoke-test.yml
```

Only `.github/workflows/goalos-agialpha-ascension-v86-final.yml` is modified so the existing autonomous Pages deployment generates and verifies the new release after Public Proof Missions 001–008 and the Ethereum Mainnet record.

## Local or CI build order

The feature deliberately depends on the existing public build order:

```bash
python3 scripts/build_goalos_agialpha_ascension_website_v86.py --out site
python3 scripts/website/build_proof_gradient_sovereign.py --site site
python3 scripts/website/build_proof_mission_002.py --site site
python3 scripts/website/build_proof_mission_003.py --site site
python3 scripts/website/build_proof_mission_004.py --site site
python3 scripts/website/build_proof_mission_005.py --site site
python3 scripts/website/build_proof_mission_006.py --site site
python3 scripts/website/build_proof_mission_007.py --site site
python3 scripts/website/build_proof_mission_008.py --site site
python3 scripts/add_goalos_ethereum_mainnet_pages_v87.py \
  --site site \
  --registry config/ethereum-mainnet.contracts.json \
  --release-contracts release/mainnet-2026-06-21/CONTRACTS_MAINNET.json \
  --release-manifest release/mainnet-2026-06-21/RELEASE_MANIFEST.json \
  --deployment-evidence release/mainnet-2026-06-21/DEPLOYMENT_EVIDENCE.json
python3 scripts/website/build_goalos_first_real_loop.py --site site
```

## Verification

```bash
python3 scripts/website/verify_goalos_first_real_loop.py \
  --site site \
  --content content/goalos-first-real-loop.json \
  --schema schemas/goalos-first-real-loop-evidence-docket.schema.json
python3 -m unittest discover -s test -p 'test_goalos_first_real_loop.py' -v
python3 -m playwright install --with-deps chromium
python3 scripts/website/browser_check_goalos_first_real_loop.py --site site
```

The verifier checks identity, page structure, exact build outputs, stable commitment reproduction, artifact hashes, homepage marker uniqueness, sitemap/status integration, source boundaries, zero-authority invariants, and absence of external execution primitives.

The browser suite exercises desktop, tablet, and mobile layouts; the complete eight-phase proof cycle; deterministic result display; downloadable docket content; Evidence Docket search; homepage integration; console cleanliness; failed requests; and external network requests.

## Preservation contract

The builder records the complete generated-site hash map before adding the feature. It refuses to complete if any pre-existing file changes outside:

```text
index.html
sitemap.xml
site-status.json
```

It also refuses any pre-existing file removal. A repeated build is byte-identical for all feature outputs and integration surfaces.

The implementation does not modify:

- `website/v86_actual_site/**`;
- Solidity or deployment configuration;
- Mainnet registry or release evidence;
- Public Proof Mission source;
- package manifests or lockfiles;
- private operator material;
- prior feature source.

## Lineage

- Original repository: `MontrealAI/agialpha-first-real-loop`
- Original snapshot: `bd920a6c52d820a087116bf59f2a4236d0494ac0`
- GoalOS repository snapshot: `a0bf9d3d4c5154a22f50651095b2683e5cafe973`

The release translates the original mechanics rather than representing them as new empirical evidence.
