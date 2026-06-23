# Public Proof Mission 003 — The Capability Constellation

This additive website module publishes GoalOS Public Proof Mission 003 without changing the canonical v86 website source or any Solidity/deployment file.

## Public question

> Can multiple Transfer-Proven capabilities compose into one higher-order system without amplifying hidden assumptions or surrendering control?

## Generated pages

- `proof-mission-003.html` — the Mission 003 flagship experience
- `proof-missions.html` — the unified Mission 001/002/003 portal
- one marked Mission 003 panel in generated `index.html`

## Generated public downloads

- `downloads/proof-missions/public-proof-mission-003.json`
- `downloads/proof-missions/mission-003-constellation-manifest-template.json`
- `downloads/proof-missions/mission-003-interface-covenant-template.json`
- `downloads/proof-missions/mission-003-fault-domain-register-template.json`
- `downloads/proof-missions/mission-003-proof-route.csv`

All templates are explicitly marked `TEMPLATE_NOT_EVIDENCE`.

## Claim boundary

Mission 003 is a published protocol, not a completed result. It cannot begin scientifically until at least three capabilities earn M2 Transfer-Proven status through completed Mission 002 evidence and closed challenge windows.

The Mainnet deployment evidence proves infrastructure existence and recorded verification. It does not prove successful composition, production safety, external audit completion, or general intelligence.

## Preservation model

The builder runs only after the canonical website and Mission 001/002 overlays are generated. It modifies only transient `site/` output.

The verifier removes the three explicitly marked homepage overlays and their style blocks, normalizes inter-tag whitespace, and requires the remaining document to equal `website/v86_actual_site/index.html`.

## Commands

```bash
python3 scripts/build_goalos_agialpha_ascension_website_v86.py --out site
python3 scripts/website/build_proof_gradient_sovereign.py --site site
python3 scripts/website/build_proof_mission_002.py --site site
python3 scripts/website/build_proof_mission_003.py --site site
python3 scripts/website/verify_proof_mission_003.py --site site
python3 -m unittest discover -s test -p 'test_proof_mission_003.py' -v
```

Browser QA requires Playwright Chromium:

```bash
python3 scripts/website/visual_check_proof_mission_003.py --site site --screenshots
```

No command above signs or broadcasts a blockchain transaction.
