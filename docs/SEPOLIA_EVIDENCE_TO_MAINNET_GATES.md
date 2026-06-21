# Sepolia Evidence to Mainnet Gates

Sepolia evidence is an explicit evidence source, but no Mainnet gate receives `PASS` from file presence or from Sepolia verification alone.

## Gate 1 — authority continuity

Contribution: `PARTIAL` only after read-only authority readback agrees with the manifest topology. The historical deployment shows the same operator address acting as deployer, Owner, operations, founder, and treasury, so it does not prove disposable-deployer separation, Ledger handoff, former-Owner removal, or production authority continuity.

Remaining evidence for PASS: current-release Safe/EOA/Ledger handoff evidence, role readback, deployer decommissioning, and former-owner removal.

## Gate 2 — typed Owner overrides

Contribution: `NOT_SUPPORTED`. Verification proves bytecode/source publication; it does not execute typed override paths.

Remaining evidence for PASS: contract-level scenario evidence for every reachable nonterminal state, replay rejection, before/after hashes, exact events, one-time financial resolution, and ordinary-versus-exceptional distinction.

## Gate 3 — accounting and canary limits

Contribution: `NOT_SUPPORTED`. The files do not prove accounting reconciliation or canary enforcement, and Sepolia `MockAGIALPHA` cannot substitute for canonical Mainnet AGIALPHA validation.

Remaining evidence for PASS: executable accounting/cap tests, exact reconciliation, solvency readback, configured limits, and canonical token validation where Mainnet-specific.

## Gate 4 — lifecycle, migration, shutdown

Contribution: `NOT_SUPPORTED`. The files do not prove pause/resume, WindDown, migration, rollback, liability-aware shutdown, or terminal shutdown.

Remaining evidence for PASS: executable rehearsal evidence and readback for lifecycle controller/mode and selector policy.

## Gate 5 — assurance and deployment reproducibility

Contribution: `PARTIAL`. Sepolia can support public-chain deployment, complete topology observation, 63 successful transaction records if independently confirmed, 49 non-empty deployed addresses if independently confirmed, 49/49 Etherscan V2 verification, independent 49/49 verification confirmation, and FQN/alias verification behavior.

Remaining evidence for PASS: current-release binding, recent Mainnet fork evidence, canonical Mainnet AGIALPHA evidence, >=1,000,000 invariant actions, >=32 seeds, secondary stateful engine, real deterministic mutation campaign, independent build equality, and a full security docket.

## Production status

Production Gate 1–5 statuses remain `BLOCKED` until all existing exact PASS predicates are genuinely met. Historical Sepolia evidence cannot satisfy current-release or mandatory Mainnet-fork predicates.
