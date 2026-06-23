# Mainnet Activation Nontechnical Runbook

This runbook is for the Wallet-B hardware-wallet operator. It does not ask for, need, or accept a recovery phrase, private key, or seed.

## What to connect

Connect the physical Ledger that controls Wallet B:

`0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99`

## Which Ledger app to open

Open the **Ethereum** app on the Ledger.

## What address must appear

The local wallet software must show exactly:

`0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99`

Stop immediately if any other address appears.

## Exact plan hash to compare

Run `npm run mainnet:activation:prepare-local` first. Compare the printed activation-plan hash with the hash shown by the local ceremony command. Stop if they differ.

## Local command

```bash
./scripts/run-mainnet-activation-ledger.sh --plan qa/mainnet-activation/activation-plan.public.json --expected-plan-hash <PLAN_HASH>
```

## What each Ledger prompt means

- **Address prompt:** confirms the signing account. It must be Wallet B.
- **Typed-data prompt:** confirms the controlled canary activation statement.
- **Transaction prompt, if present:** confirms a real Mainnet transaction target, value, function selector, nonce, and fee ceiling.

## When to stop

Stop if:

- the Ledger asks for a recovery phrase;
- the address is not Wallet B;
- the plan hash differs;
- any target, nonce, value, gas ceiling, or effect differs from the reviewed plan;
- the command reports source, Stage-B, authority, or configuration drift.

## How to resume

Re-run the same command. The local tooling writes append-only ceremony journals and refuses duplicate submission for an already-submitted plan.

## How to export sanitized evidence

After the local ceremony and canary, export only the sanitized bundle at:

`.private/mainnet-activation/sanitized-evidence-bundle.json`

Do not commit raw Ledger transport logs, RPC URLs, API keys, browser profiles, private operator notes, or any `.private/` file.
