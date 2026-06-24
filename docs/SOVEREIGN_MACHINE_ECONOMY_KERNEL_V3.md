# GoalOS Sovereign Machine Economy Kernel v3

## Purpose

Kernel v3 is the executable constitutional foundation beneath the GoalOS Sovereign Machine Economy. It converts the integrated META-Agentic α‑AGI, AGI Alpha Node v0, and AGI Jobs v0 (v2) experience into a browser-local protocol runtime with enforceable state transitions, cryptographic role separation, durable mission history, independent bundle verification, and a signed human review boundary.

The release remains additive. It does not modify `website/v86_actual_site/**`, contracts, Mainnet deployment evidence, Public Proof Missions, package manifests, lockfiles, or prior feature source.

## Public surfaces

- `sovereign-machine-economy-kernel-v3.html` — executable mission theatre.
- `sovereign-machine-economy-kernel-v3-protocol.html` — state, envelope, role, and authority registry.
- `sovereign-machine-economy-kernel-v3-chronicle.html` — durable append-only mission chronicle.
- `sovereign-machine-economy-kernel-v3-verifier.html` — independent portable-bundle verifier.
- `sovereign-machine-economy-kernel-v3-sdk.html` — zero-dependency core and adapter contract.
- `index.html#sme-kernel-v3` — additive homepage gateway.

## Executable architecture

### Constitutional state machine

The kernel advances through 17 strict states:

`DRAFT → MISSION_COMMITTED → INSTITUTION_PROPOSED → INSTITUTION_CHARTERED → NODE_ADMITTED → EXECUTION_BOUNDED → WORK_EXECUTED → EVIDENCE_SEALED → MARKET_CONVENED → VALIDATION_COMMITTED → VALIDATION_REVEALED → CHALLENGE_WINDOW_OPEN → SETTLEMENT_INTENT_PREPARED → AWAITING_HUMAN_REVIEW → HUMAN_REVIEW_RECORDED → MEMORY_DISPOSITION_RECORDED → COMPLETE`

A transition is committed only when its predecessor, issuer, envelope type, payload commitment, envelope identity, signature, and target state all verify.

### Typed protocol envelopes

Kernel v3 defines ten versioned envelopes:

- `MissionCommitment`
- `InstitutionProposal`
- `InstitutionCharter`
- `NodeAdmission`
- `NodeExecutionReceipt`
- `EvidenceDocket`
- `ValidationOpinion`
- `ChallengeRecord`
- `SettlementIntent`
- `HumanReviewCertificate`

Every envelope carries the protocol version, mission identifier, issuer, logical time, predecessor commitment, payload commitment, authority scope, external-action count, envelope identifier, and signature record.

### Cryptographic role separation

Five role identities are generated with WebCrypto Ed25519:

- Meta-Architect
- Node Operator
- Market Steward
- Independent Verifier
- Human Reviewer

Private `CryptoKey` objects remain in the browser-local vault. Portable mission bundles include only public JWKs and fingerprints.

### Isolated runtime and durable chronicle

The state machine executes inside a Web Worker. Mission state is stored as append-only events in IndexedDB. Refreshing the experience can resume an existing mission. Rollback does not rewrite history; it must be represented by a new signed event.

### Replaceable adapters

META-Agentic, Alpha Node, and AGI Jobs adapters implement the same six-method contract:

```text
initialize()
propose()
execute()
evaluate()
produceEvidence()
verifyEvidence()
```

The first release provides deterministic local adapters. Future authenticated model, enterprise, evaluator, or contract adapters can implement the contract without changing the constitutional transition rules.

### Independent verification

A portable mission bundle contains public identities, signed envelopes, committed events, strict replay policy, and a bundle root. The verifier recomputes:

- schema and protocol compatibility;
- public-key fingerprints;
- payload and envelope commitments;
- every Ed25519 signature;
- issuer allowlists;
- legal state order;
- predecessor commitments;
- final chain head;
- portable bundle root.

Edited bundles are quarantined rather than partially trusted.

## Human authority boundary

The machine cycle stops at `AWAITING_HUMAN_REVIEW`. A Human Reviewer may record one of four local dispositions:

- `APPROVED_FOR_DELIBERATION`
- `REVISION_REQUESTED`
- `DISPUTE_OPEN`
- `REJECTED_SAFE_HOLD`

The certificate records scope, unresolved risks, expiration policy, settlement disposition, and revocable memory disposition. It does not invoke external execution.

## Default-deny posture

Kernel v3 performs no live model call, authenticated enterprise action, wallet connection, RPC request, network read or write, token movement, settlement, credential issuance, production activation, or automatic memory promotion. Local signatures prove possession of local role keys, not real-world identity. Evidence integrity is not factual certification.

## Autonomous build

The production GitHub Action builds all existing GoalOS surfaces first, snapshots the generated site, adds Kernel v3 last, verifies its preservation boundary, runs deterministic tests and browser QA, revalidates every companion manifest, checks canonical v86 byte identity, rejects archives and private operator material, uploads the full Pages artifact, and deploys only after the build job succeeds.
