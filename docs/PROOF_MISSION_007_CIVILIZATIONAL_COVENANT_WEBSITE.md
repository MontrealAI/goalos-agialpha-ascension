# Public Proof Mission 007 — The Civilizational Covenant

## Public status

```text
PROTOCOL_PUBLISHED_AWAITING_THREE_CONTINUITY_PROVEN_COMMONWEALTHS
```

Mission 007 publishes a bounded, claim-controlled protocol for plural stewardship of shared public goods. It does not claim political authority, legal authority, global consent, civilizational safety, AGI, ASI, superintelligence, or authority over humanity.

## Constitutional law

```text
No stewardship without consent.
No shared future without plural sovereignty.
No covenant without rights, dissent, exit, rollback, and the power to end.
```

## Website outputs

The autonomous GitHub Pages workflow generates:

```text
proof-mission-007.html
proof-missions.html
index.html additive Mission 007 panel
downloads/proof-missions/public-proof-mission-007.json
downloads/proof-missions/mission-007-*.json
downloads/proof-missions/mission-007-proof-route.csv
```

## Preservation rule

The builder changes only generated output. It does not modify `contracts/**`, `website/v86_actual_site/**`, package files, deployment scripts, or Mainnet records. Missions 001–005 remain byte-for-byte unchanged. Mission 006 changes only in its explicitly marked Mission 007 horizon panel.

## Required build order

```bash
python3 scripts/build_goalos_agialpha_ascension_website_v86.py --out site
python3 scripts/website/build_proof_gradient_sovereign.py --site site
python3 scripts/website/build_proof_mission_002.py --site site
python3 scripts/website/build_proof_mission_003.py --site site
python3 scripts/website/build_proof_mission_004.py --site site
python3 scripts/website/build_proof_mission_005.py --site site
python3 scripts/website/build_proof_mission_006.py --site site
python3 scripts/website/build_proof_mission_007.py --site site
```

The workflow must never run a Mission 006 or Mission 007 visual check before the corresponding builder creates the page.
