# Public Proof Mission 004 — The Sovereign Institution

## Purpose

Mission 004 publishes a claim-bounded protocol for testing whether one M3 Composition-Proven constellation can operate as a time-bounded institution across repeated mission epochs without escaping evidence, capital limits, human authority, challenge, or rollback.

Public status:

```text
PROTOCOL_PUBLISHED_AWAITING_ONE_COMPOSITION_PROVEN_CONSTELLATION
```

No institutional outcome is predeclared.

## Public pages

```text
/proof-mission-004.html
/proof-missions.html
/index.html                  additive Mission 004 panel only
```

The Mission 004 builder also promotes the former Mission 004 horizon on the generated Mission 003 page into a link to the newly published protocol. It does not edit the Mission 003 source content.

## Constitutional rules

```text
No mandate, no mission.
No capital without proof.
No evolution beyond review and rollback.
```

## Acceptance scope

Mission 004 requires four operating mission epochs, exact treasury reconciliation, injected institutional shocks, one operator succession, independent replay, five-validator approval, a fourteen-day challenge window, and explicit human renewal, narrowing, or termination.

An accepted result may earn:

```text
M4 — INSTITUTION-PROVEN
```

This does not imply achieved AGI, ASI, general institutional autonomy, universal safety, external audit completion, legal approval, or permanent machine sovereignty.

## Generated downloads

```text
downloads/proof-missions/public-proof-mission-004.json
downloads/proof-missions/mission-004-institution-charter-template.json
downloads/proof-missions/mission-004-epoch-ledger-template.json
downloads/proof-missions/mission-004-treasury-policy-template.json
downloads/proof-missions/mission-004-incident-recovery-template.json
downloads/proof-missions/mission-004-proof-route.csv
```

Every template is marked `TEMPLATE_NOT_EVIDENCE`.

## Autonomous build order

```bash
python3 scripts/build_goalos_agialpha_ascension_website_v86.py --out site
python3 scripts/website/build_proof_gradient_sovereign.py --site site
python3 scripts/website/build_proof_mission_002.py --site site
python3 scripts/website/build_proof_mission_003.py --site site
python3 scripts/website/build_proof_mission_004.py --site site
python3 scripts/website/verify_proof_mission_004.py --site site
```

## Preservation

The integration operates only on generated `site/` output. It does not modify:

```text
contracts/**
website/v86_actual_site/**
package.json
package-lock.json
hardhat.config.ts
deployment scripts
Mainnet deployment records
```

The verifier removes all explicitly marked mission overlays and compares the remaining generated homepage with the canonical source.

## Mainnet claim boundary

Mission 004 maps 34 proof stages to the configured Ethereum Mainnet deployment. The deployment evidence records 48 GoalOS-created contracts, 48 recorded source verifications, zero recorded verification failures, 14 configured grants, and a passing 48-contract postcheck.

Infrastructure existence is public. Mission outcomes remain evidence-gated.

## No public-network action

Website generation, verification, regression tests, browser checks, and GitHub Pages deployment do not submit a blockchain transaction and require no wallet, RPC URL, private key, or Etherscan key.
