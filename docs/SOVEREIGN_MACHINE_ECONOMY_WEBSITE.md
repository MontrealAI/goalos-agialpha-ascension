# GoalOS AGIALPHA Ascension — Sovereign Machine Economy

## Release identity

**Constellation:** META-AGENTIC α‑AGI 👁️✨ × AGI Alpha Node v0 ⚡️✨ × AGI Jobs v0 (v2) ✨  
**Release:** `GOALOS-SOVEREIGN-MACHINE-ECONOMY-001`  
**Version:** `1.0.0-civilization`

> A mind that builds minds. A node that turns intelligence into proof. A market that turns proof into accountable value.

This release integrates the three installed GoalOS flagships into one deterministic, browser-local constitutional machine-economy experience. It does not replace or rewrite any of them. It builds after them, verifies their manifests, adds four new public surfaces, extends only declared shared website surfaces, and reconciles the companion manifest hashes.

## Public surfaces

| Page | Purpose |
|---|---|
| `sovereign-machine-economy.html` | Commission and inspect the complete institution → node → market proof cycle |
| `sovereign-machine-economy-architecture.html` | Constitutional architecture, handoff protocol, separation of powers, guardians and lineage |
| `sovereign-machine-economy-chronicle.html` | Searchable 36-artifact cryptographic Proof Chronicle |
| `sovereign-machine-economy-atlas.html` | Civilization Atlas linking all three flagship institutions and their deeper surfaces |
| `index.html#sovereign-machine-economy` | Additive flagship gateway on the main GoalOS website |

The homepage also receives one additive `Machine Economy` navigation entry.

## Constitutional cycle

The interactive cycle traverses eighteen gates:

1. Mission Charter
2. Institution Population
3. Pareto Selection
4. Constitution Seal
5. Foundry Handoff
6. Node Identity
7. Peer Route
8. Resource Envelope
9. Alpha Work Unit
10. Node Validation
11. Node Evidence Seal
12. Market Handoff
13. Market Charter
14. Guild Competition
15. Coalition Formation
16. Proof Parliament
17. Challenge Window
18. Human Settlement Review

The Evidence Docket contains 36 chained artifacts: 12 META, 12 NODE and 12 JOBS. Three explicit commitments bind META → NODE → JOBS → HUMAN.

## Terminal constitution

| Condition | Terminal state |
|---|---|
| Normal evidence-complete run | `HUMAN_SETTLEMENT_REVIEW` |
| Budget breach | `HUMAN_REVIEW_REQUIRED` |
| Evidence gap | `DISPUTE_OPEN` |
| Institution divergence or node identity drift | `SAFE_HOLD` |

Every path retains `NONE_GRANTED` external authority. The browser experience performs zero wallet connections, zero runtime network requests, zero live token movement and zero external actions.

## Source files

- `content/sovereign-machine-economy.json`
- `website/features/sovereign-machine-economy/templates/*.html`
- `website/features/sovereign-machine-economy/assets/sovereign-machine-economy.css`
- `website/features/sovereign-machine-economy/assets/sovereign-machine-economy.js`
- `schemas/sovereign-machine-economy-docket.schema.json`
- `scripts/website/build_sovereign_machine_economy.py`
- `scripts/website/snapshot_sovereign_machine_economy_site.py`
- `scripts/website/verify_sovereign_machine_economy.py`
- `scripts/website/visual_check_sovereign_machine_economy.py`
- `test/test_sovereign_machine_economy_website.py`

## Deterministic build order

The feature must be built after the preserved v86 website, Proof Missions 001–008, Mainnet record, META-Agentic α‑AGI, AGI Alpha Node v0, First Real Loop and AGI Jobs v0 (v2).

```bash
python3 scripts/website/snapshot_sovereign_machine_economy_site.py \
  --site site \
  --output /tmp/sovereign-machine-economy-prebuild.json

SOURCE_DATE_EPOCH=1782320400 python3 scripts/website/build_sovereign_machine_economy.py \
  --site site \
  --root .

python3 scripts/website/verify_sovereign_machine_economy.py \
  --site site \
  --root . \
  --baseline /tmp/sovereign-machine-economy-prebuild.json \
  --schema schemas/sovereign-machine-economy-docket.schema.json \
  --output site/qa/sovereign-machine-economy-static.json

python3 -m unittest discover -s test \
  -p 'test_sovereign_machine_economy_website.py' -v

python3 scripts/website/visual_check_sovereign_machine_economy.py \
  --site site \
  --output site/qa/sovereign-machine-economy
```

## Additive preservation boundary

New generated outputs are limited to the four public pages, two assets, one public data file, one sample docket, one manifest and the feature QA reports.

Existing generated outputs permitted to change are limited to:

- `index.html`
- `routes.json`
- `sitemap.xml`
- `site-status.json`
- `meta-agentic-alpha-agi-manifest.json`
- `agi-alpha-node-v0-manifest.json`
- `agi-jobs-v0-v2-manifest.json`

The canonical `website/v86_actual_site/**` source is not modified. Contracts, Mainnet evidence, Proof Missions, prior flagship source, package manifests and lockfiles are outside the feature write boundary.

## Human-review boundary

The interface is a deterministic constitutional digital twin and evidence workflow. It does not certify factual correctness, activate production, authorize user funds, issue credentials, execute external work, settle value or promote capability memory.
