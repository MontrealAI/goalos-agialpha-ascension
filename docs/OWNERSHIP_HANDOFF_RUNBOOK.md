# GoalOS Ownership Handoff Runbook

This runbook is for a careful Ubuntu operator. Ownership is the ERC-173 `owner()` address. Roles are the GoalOS operational permissions. GoalOS couples the owner to the seven owner-managed roles so a successful `transferOwnership(finalOwner)` also grants the final owner all managed roles and removes them from the disposable deployer.

Never type a Ledger seed phrase, Ledger private key, MetaMask seed phrase, or wallet private key into this repository. Ledger proof uses MetaMask/Ledger signing only.

## Required environment

```bash
FINAL_OWNER_ADDRESS=0x...
FINAL_OWNER_KIND=LEDGER_EOA # or SAFE
FINAL_OWNER_CONTROL_PROOF_PATH=.private/final-owner-control-proof.json
```

Mainnet also requires permanent founder, treasury, and vault/controller addresses to be non-disposable; single-deployer permanent address mode is blocked.

## Sepolia sequence

```bash
npm run ownership:sepolia:doctor
npm run ownership:sepolia:plan
npm run ownership:sepolia:dry-run
npm run ownership:sepolia:transfer
npm run ownership:sepolia:verify
npm run ownership:sepolia:evidence
```

## Mainnet sequence

1. Verify the full checksummed `FINAL_OWNER_ADDRESS` on the Ledger/MetaMask screen. Compare every character, not only the first and last characters.
2. Create `.private/final-owner-control-proof.json` using a local Ledger/Safe signing ceremony bound to chain ID 1, final owner, git commit, deployment manifest SHA-256, nonce, creation time, and expiry.
3. Run:

```bash
npm run ownership:mainnet:doctor
npm run ownership:mainnet:plan
npm run ownership:mainnet:fork-rehearsal
```

4. Read `.private/ethereum-mainnet.ownership-plan.latest.json`; copy the full `planHash`.
5. Set the exact typed confirmation:

```bash
export OWNERSHIP_MAINNET_CONFIRMATION="ETHEREUM_MAINNET-1-${FINAL_OWNER_ADDRESS}-${PLAN_HASH}"
npm run ownership:mainnet:transfer-local-gated
npm run ownership:mainnet:verify
npm run ownership:mainnet:evidence
```

## Stop conditions

Stop immediately on wrong chain, wrong final owner, no bytecode, insufficient funds, pending/dropped/replaced transaction, RPC outage, failed receipt, reorg, target/proof mismatch, unexpected owner, unexpected role, or any FAIL output.

## Resume

Rerun `npm run ownership:mainnet:transfer-local-gated`. The journal under `.private/` and on-chain `owner()` state make the command idempotent.

## Optional ETH sweep

Only after `npm run ownership:mainnet:verify` and `npm run ownership:mainnet:evidence` produce `PASSED`, run:

```bash
export OWNERSHIP_SWEEP_CONFIRMATION="SWEEP-AFTER-PASSED-HANDOFF-${FINAL_OWNER_ADDRESS}"
npm run ownership:mainnet:sweep-deployer-local-gated
```

This never sweeps tokens automatically. Deleting a MetaMask account does not invalidate its private key; safety comes from zero on-chain authority and zero valuable balance.

## Public vs private artifacts

Public: deployment handoff JSON under `deployments/`, QA evidence under `qa/`, reports under `docs/`. Private: control proof, journals, operator env files, private keys, and raw wallet data under `.private/`.

## Final checklist

The disposable private key may be removed from MetaMask/local files only after verification proves: every managed contract owner is the final owner, the disposable address has none of the seven managed roles anywhere, permanent economic/controller getters do not equal the disposable address, and optional ETH sweep is complete if desired.
