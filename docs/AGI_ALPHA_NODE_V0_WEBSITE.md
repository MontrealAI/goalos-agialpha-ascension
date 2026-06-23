# GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨

## Release identity

| Field | Value |
|---|---|
| Public title | **GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨** |
| Release ID | `goalos-agialpha-ascension-agi-alpha-node-v0-001` |
| Version | `1.0.0-ascension-alpha` |
| Status | `interactive-sovereign-node-simulation` |
| Flagship route | `/agi-alpha-node-v0.html` |
| Architecture route | `/agi-alpha-node-v0-architecture.html` |
| Homepage gateway | `/index.html#agi-alpha-node-v0` |
| Terminal state | `HUMAN_REVIEW_REQUIRED` |
| External authority | `NONE_GRANTED` |

## Product thesis

**Intelligence at the edge. Proof at the center. Authority at the human boundary.**

AGI Alpha Node v0 is reconstituted as a GoalOS-native **sovereign proof node**: a browser-local experience for composing one bounded Alpha Work Unit, admitting a deterministic resource envelope, routing a reviewable peer mesh, generating a reproducible sandbox receipt, evaluating quality and service objectives, recording validator quorum with dissent, and exporting a fourteen-artifact Node Evidence Docket.

The experience does not pretend to operate infrastructure that is not present. It resolves no ENS identity, contacts no libp2p peer, calls no model, allocates no compute, connects no wallet, moves no token, submits no transaction, executes no treasury intent, and performs no external action. A complete proof package earns **human review**, not permission.

## What a visitor can do

1. Select an enterprise, scientific, engineering, or public-interest mission preset—or write a custom mission.
2. Choose a work class: Reason, Build, Verify, or Orchestrate.
3. Select an Institutional, Ascension, or Frontier operating posture.
4. Compose a bounded mission contract with a decision, success criteria, constraints, reviewer, and stop rules.
5. Run the deterministic eight-state node cycle.
6. Inspect the admitted and rejected peers, resource envelope, latency, energy, reliability, and fallback policy.
7. Inspect the normalized Alpha Work Unit receipt and quality/SLO evaluation.
8. Review seven independent validator seats, quorum, rationales, uncertainty, and preserved dissent.
9. Inspect five guardian domains while treasury and external authority remain separately withheld.
10. Download the complete Node Evidence Docket as JSON and the Executive Review Brief as Markdown.
11. Place the node in Safe Hold without deleting evidence.

## Eight proof-gated states

| # | State | Bounded authority | Sealed artifact |
|---:|---|---|---|
| 1 | `NODE_IDENTITY_COMMITTED` | Identity Sentinel | `NodeIdentity.json` |
| 2 | `WORK_UNIT_CONTRACTED` | Mission Orchestrator | `WorkUnitContract.json` |
| 3 | `RESOURCE_ENVELOPE_ADMITTED` | Resource Governor | `ResourceEnvelope.json` |
| 4 | `PEER_ROUTE_COMMITTED` | Mesh Conductor | `PeerRoute.json` |
| 5 | `SANDBOX_RECEIPT_READY` | Execution Core | `WorkUnitReceipt.json` |
| 6 | `QUALITY_EVALUATION_READY` | Quality Tribunal | `QualityEvaluation.json` |
| 7 | `VALIDATOR_QUORUM_RECORDED` | Verifier Mesh | `ValidatorConsensus.json` |
| 8 | `HUMAN_REVIEW_REQUIRED` | Guardian Council | `AuthorizationState.json` |

The complete chain contains fourteen artifacts, including sandbox planning, energy, contradictions, health attestation, the Node Evidence Docket, and a Chronicle entry.

## Original AGI Alpha Node v0 → GoalOS translation

The reimplementation preserves the original project’s conceptual lineage while changing its public execution model from live owner-operated infrastructure to an inspectable, proof-gated, default-deny GoalOS experience.

| Original concept | GoalOS Ascension construct | Why the translation matters |
|---|---|---|
| ENS node identity | Node Identity Commitment | A displayed name becomes an explicit claim with provenance requirements—not assumed ownership. |
| libp2p host, dial policy, and resource manager | Peer Route + Resource Envelope | Connectivity, capacity, latency, energy, and fallbacks become reviewable admission decisions. |
| Alpha Work Unit | Proof-carrying Work Unit Contract | Machine work is bound to mission, success criteria, resources, telemetry, quality, evidence, and review state. |
| Runtime orchestrator | Mission Orchestrator + proof-gated state machine | Sequencing is mission-scoped and cannot silently expand the user mandate. |
| Validator loop and quorum engine | Independent Verifier Mesh | Votes, thresholds, rationales, uncertainty, and dissent remain inspectable and cannot self-authorize action. |
| Prometheus, Grafana, and runtime telemetry | Evidence Telemetry Ledger | Operational signals become sealed review artifacts rather than ephemeral dashboard decoration. |
| Owner governance controls | Guardian Council + Authorization State | Pause, veto, least privilege, separation of duties, and human review become explicit gates. |
| Treasury executor and economic settlement | Settlement Intent under default deny | Successful work-unit review never implies authority to move funds or settle value. |
| Global Synthetic Labor metrics | Normalized Alpha Work Unit receipt | Work, quality, timeliness, energy, and evidence are displayed as deterministic simulation values, not live economic claims. |
| Offline snapshots and operator records | Node Evidence Docket + Chronicle | The complete review package is portable and locally downloadable without hidden persistence. |

## Deterministic runtime contract

The runtime uses the mission contract as a seed for reproducible, browser-local simulation. The same mission, work class, posture, and constraints produce the same peer route, Alpha Work Unit receipt, validator record, artifact hashes, and docket ID.

The runtime deliberately separates:

- **capability** from **authority**;
- **simulated quorum** from **factual certification**;
- **proof-package completeness** from **production readiness**;
- **guardian review** from **treasury authorization**;
- **local generation** from **external execution**.

The public JavaScript exposes a read-only QA surface at `window.__AAN_QA__` so automated browser tests can verify state, determinism, downloads, authority boundaries, and artifact integrity without introducing an API.

## Security and claim boundary

The experience is built under a strict default-deny contract:

| Capability | Public release state |
|---|---|
| External JavaScript/CSS dependencies | None |
| Network reads or writes | None |
| Model or tool calls | None |
| Live ENS resolution | None |
| Wallet or provider connection | None |
| Token movement or transaction broadcast | None |
| Treasury execution or settlement | None |
| Browser persistence | None |
| External actions | `0` |
| Factual correctness certification | `NOT_CERTIFIED` |
| Production activation | `NOT_ACTIVATED` |
| Funds authorization | `NO` |
| Terminal state | `HUMAN_REVIEW_REQUIRED` |

A strict Content Security Policy permits only same-origin assets. The verifier rejects network primitives, wallet/provider primitives, storage primitives, external script or stylesheet URLs, misleading production claims, missing boundaries, state-machine drift, manifest drift, and accidental authority escalation.

## Source layout

```text
content/agi-alpha-node-v0.json
website/features/agi-alpha-node-v0/templates/agi-alpha-node-v0.html
website/features/agi-alpha-node-v0/templates/agi-alpha-node-v0-architecture.html
website/features/agi-alpha-node-v0/assets/agi-alpha-node-v0.css
website/features/agi-alpha-node-v0/assets/agi-alpha-node-v0.js
scripts/website/build_agi_alpha_node_v0.py
scripts/website/verify_agi_alpha_node_v0.py
scripts/website/visual_check_agi_alpha_node_v0.py
test/test_agi_alpha_node_v0_website.py
docs/AGI_ALPHA_NODE_V0_WEBSITE.md
README_UPLOAD_AGI_ALPHA_NODE_V0.md
```

The only existing repository files updated by the release are the two autonomous website workflow definitions:

```text
.github/workflows/goalos-agialpha-ascension-v86-final.yml
.github/workflows/goalos-agialpha-ascension-v86-smoke-test.yml
```

## Generated public outputs

The additive builder writes:

```text
site/agi-alpha-node-v0.html
site/agi-alpha-node-v0-architecture.html
site/assets/agi-alpha-node-v0.css
site/assets/agi-alpha-node-v0.js
site/data/agi-alpha-node-v0.json
site/agi-alpha-node-v0-manifest.json
site/qa/agi-alpha-node-v0-build.json
```

It also idempotently adds one navigation link, one homepage gateway, the two routes, sitemap entries, and a release record in `site-status.json`. Repeated builds replace only their own marked integration blocks and do not duplicate them.

## Autonomous workflow order

The production and pull-request workflows retain the complete existing site generation pipeline and add AGI Alpha Node v0 only after the preserved v86 site and existing feature builders have completed:

```text
Preserve/copy canonical website
→ build existing generated experiences
→ build META-AGENTIC Institution Foundry
→ build AGI Alpha Node v0 additively
→ assert generated outputs
→ static verification
→ focused regression tests
→ Chromium interaction/visual QA
→ reject private/archive material
→ package complete Pages artifact
→ deploy (production workflow only)
```

## Developer validation

From the repository root:

```bash
python3 scripts/website/build_agi_alpha_node_v0.py --site site
python3 scripts/website/verify_agi_alpha_node_v0.py --site site
python3 -m unittest test.test_agi_alpha_node_v0_website -v
python3 scripts/website/visual_check_agi_alpha_node_v0.py --site site --output site/qa/agi-alpha-node-v0
```

The browser check uses Chromium through Playwright, captures desktop/tablet/mobile evidence, downloads the two review records, verifies deterministic reruns, confirms all authority boundaries, and fails on console errors, page errors, network activity, or horizontal overflow.

## Preservation contract

This release is additive by design:

- no file under `website/v86_actual_site/**` is modified;
- no contract, deployment record, Mainnet evidence, Proof Mission, package manifest, dependency lockfile, or existing feature source is rewritten;
- existing generated pages remain byte-identical except for the intentionally marked homepage/navigation/route/status/sitemap integration surfaces;
- repeated builds are idempotent;
- rollback is performed by reverting the release pull request, not by deleting generated Pages files manually.

## Acceptance standard

A release is acceptable only when:

- the original website and all prior routes still load;
- the META-AGENTIC flagship still coexists with the new node;
- exactly one AGI Alpha Node navigation item and homepage gateway exist;
- both new routes render without horizontal overflow on desktop, tablet, and mobile;
- the same mission produces the same peer route, receipt, quorum, and docket;
- dissent remains visible;
- fourteen artifacts are sealed;
- both review records download;
- terminal state is `HUMAN_REVIEW_REQUIRED`;
- authority remains `NONE_GRANTED` and external actions remain `0`;
- the smoke and production workflows remain green.
