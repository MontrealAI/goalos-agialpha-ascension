# GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨

## Sovereign Citadel release

This additive website feature reimplements the original **AGI Alpha Node v0** as a GoalOS-native, proof-governed public digital twin. It preserves the original project’s central ideas—declared node identity, bounded runtime resources, peer networking, α‑Work Units, independent validators, observability, guardians, and treasury separation—while translating them into a browser-local constitutional workflow that never grants itself external authority.

**Release:** `3.0.0-sovereign-citadel`  
**Tagline:** **One node. Many minds. Zero unearned authority.**  
**Public status:** interactive design reference and deterministic digital twin; not a live node deployment.

## Public surfaces

The generator adds three complementary pages:

| Page | Purpose |
| --- | --- |
| `agi-alpha-node-v0.html` | Sovereign Node Theatre: compose a bounded work unit, choose a posture, route primary and shadow peer councils, rehearse incidents, inspect consensus, and export evidence. |
| `agi-alpha-node-v0-architecture.html` | Constitutional Architecture: ten authority planes, proof gates, source lineage, threat model, and explicit claim boundary. |
| `agi-alpha-node-v0-proof-ledger.html` | Proof Ledger: sixteen chained artifact classes, reviewer checklist, sample docket, and final human authority boundary. |

A marked, idempotent gateway is added to `index.html`; the three routes are also registered in `routes.json`, `sitemap.xml`, and `site-status.json`.

## Constitutional runtime

The public experience is deterministic and entirely browser-local. A successful proof flight advances through ten states:

1. `NODE_IDENTITY_SEALED`
2. `WORK_UNIT_CONTRACTED`
3. `POLICY_COMPILED`
4. `RESOURCE_ENVELOPE_ADMITTED`
5. `PEER_ROUTES_COMMITTED`
6. `SANDBOX_RECEIPT_READY`
7. `MULTI_AXIS_EVALUATION_READY`
8. `VALIDATOR_QUORUM_RECORDED`
9. `GUARDIAN_REVIEW_PACKAGED`
10. `HUMAN_REVIEW_REQUIRED`

The node is represented by ten bounded constitutional roles: Identity Sentinel, Mission Orchestrator, Constitution Compiler, Resource Governor, Mesh Conductor, Execution Core, Quality Tribunal, Verifier Mesh, Guardian Council, and Chronicle Keeper.

For each declared mission, the runtime deterministically:

- admits a resource envelope before simulated execution;
- scores twelve peer institutions across quality, reliability, evidence, route diversity, energy, and latency;
- commits a four-peer primary route and a three-peer shadow route;
- records seven validator opinions, including dissent;
- convenes five guardians;
- creates a sixteen-artifact SHA-256 commitment chain;
- exports a Node Evidence Docket and executive review brief;
- stops at `HUMAN_REVIEW_REQUIRED` or fails closed to `SAFE_HOLD`.

The resilience gauntlet includes peer eclipse, identity drift, resource surge, and validator divergence. Identity drift and other severe constitutional breaches demonstrate a guardian safe hold rather than fabricated success.

## Evidence model

The sixteen artifact classes are:

`NodeIdentity.json`, `WorkUnitContract.json`, `PolicyEnvelope.json`, `ResourceEnvelope.json`, `PeerCandidateLedger.json`, `PeerRouteCommitment.json`, `IncidentDisposition.json`, `AlphaWorkUnitReceipt.json`, `TelemetryDigest.json`, `EvaluationMatrix.json`, `ValidatorConsensus.json`, `GuardianReview.json`, `AuthorizationState.json`, `ProofChronicle.json`, `NodeEvidenceDocket.json`, and `ExecutiveReviewBrief.md`.

Each artifact contains its payload hash, previous commitment, and current commitment. This makes browser-local runs replayable and inspectable. The chain is not published to Ethereum and is not represented as an external attestation.

## Default-deny security boundary

The release contains no external runtime dependencies and its Content Security Policy uses `connect-src 'none'`. It performs no live ENS resolution, peer dialing, model call, API request, WebSocket connection, wallet connection, blockchain transaction, token movement, staking operation, settlement, or external action. It uses no persistent browser storage.

The generated review boundary is explicit:

```text
Factual correctness   NOT_CERTIFIED
Production activation NOT_ACTIVATED
Funds authorization   NO
External actions       0
Final state            HUMAN_REVIEW_REQUIRED or SAFE_HOLD
```

## Source lineage

The release data records fifteen SHA-256 fingerprints derived from the supplied original repository snapshot. The architecture page maps original Node concepts to their GoalOS constitutional equivalents. This is a traceable reimplementation rather than a claim that the original runtime itself is executing in the browser.

## Mainnet record

The build derives its displayed GoalOS Mainnet record from repository evidence at build time. It preserves the repository’s boundaries: 48 GoalOS-created contracts, recorded operator verification of 48/48, 14/14 configured Phase-B grants, production activation `NOT_ACTIVATED`, user-fund authorization `NO`, and source-identity reproduction `PENDING`.

## Additive build contract

Source files added by this feature:

- `content/agi-alpha-node-v0.json`
- `website/features/agi-alpha-node-v0/**`
- `scripts/website/build_agi_alpha_node_v0.py`
- `scripts/website/snapshot_agi_alpha_node_v0_site.py`
- `scripts/website/verify_agi_alpha_node_v0.py`
- `scripts/website/visual_check_agi_alpha_node_v0.py`
- `test/test_agi_alpha_node_v0_website.py`
- this document and `README_UPLOAD_AGI_ALPHA_NODE_V0.md`

Only the two existing GitHub Pages workflows require modification. The generator does not modify `website/v86_actual_site/**`, contracts, deployment records, Proof Missions, package manifests, lockfiles, or prior feature source.

Before the Node is generated, the workflow snapshots the entire already-generated site. Verification then permits changes only to `index.html`, `routes.json`, `sitemap.xml`, `site-status.json`, the new Node outputs, and—when META-Agentic α‑AGI is already installed—its generated companion manifest. The companion manifest is reconciled only for those four shared integration surfaces and is re-verified after Node generation.

## Local commands

```bash
python3 scripts/build_goalos_agialpha_ascension_website_v86.py --out site
python3 scripts/website/snapshot_agi_alpha_node_v0_site.py --site site --output /tmp/agi-alpha-node-v0-prebuild.json
SOURCE_DATE_EPOCH=1782216000 python3 scripts/website/build_agi_alpha_node_v0.py --site site --root .
python3 scripts/website/verify_agi_alpha_node_v0.py --site site --root . --baseline /tmp/agi-alpha-node-v0-prebuild.json --output site/qa/agi-alpha-node-v0-static.json
python3 -m unittest discover -s test -p 'test_agi_alpha_node_v0_website.py' -v
python3 scripts/website/visual_check_agi_alpha_node_v0.py --site site --output site/qa/agi-alpha-node-v0-browser
```

The production and pull-request workflows run the Node only after the preserved website, Proof Missions 001–008, Ethereum Mainnet record, and any complete optional META-Agentic release have been generated and checked.
