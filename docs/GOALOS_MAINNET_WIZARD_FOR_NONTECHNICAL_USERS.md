Install:
`npm ci`

Start:
`npm run mainnet:initial:setup-and-authorize`

# GoalOS Mainnet Wizard for Nontechnical Ubuntu Users

This guide explains the safe one-command wizard for the scoped initial Mainnet infrastructure deployment. It does **not** activate production and does **not** authorize user funds.

## 1. Start the wizard

```text
$ npm run goalos:mainnet:wizard

GoalOS Initial Mainnet Deployment Wizard

1/9  Clean release workspace
2/9  Historical Sepolia evidence
3/9  Build and automated tests
4/9  Local Wallet-A/Wallet-B rehearsal
5/9  Initial-deployment safety checks
6/9  Ethereum Mainnet deployment plan
7/9  Ledger Wallet-B approval
8/9  Verification and recovery readiness
9/9  Scoped Stage-A certificate
```

Default mode is preparation only. It sends no transaction and spends no gas.

## 2. Hidden private values

If the wizard needs RPC or Etherscan settings, it asks one question at a time and hides the value while typing. Values are stored in `.private/mainnet-operator.env` with private file permissions. The preparation flow does not require Wallet A's private key.

## 3. Dirty working tree

If your repository has unrelated edits, the wizard leaves them untouched and creates a clean sibling release workspace, such as `../goalos-mainnet-release-<sha>/`.

```text
PASS — Your existing edits were left untouched.
A separate clean release workspace was created.
```

## 4. Historical Sepolia evidence

The wizard validates the existing Sepolia evidence and shows:

```text
PASS — Historical Sepolia deployment validated: 49/49 verified.
Note — This historical deployment used Solidity 0.8.35, a test token, and a different authority arrangement.
```

## 5. Ledger approval

When Ledger approval is needed, the wizard pauses:

```text
ACTION NEEDED — Connect your Ledger and approve one message.
No transaction will be sent and no gas will be spent.
```

Never type your Ledger recovery phrase anywhere.

## 6. Plan review

The wizard creates a nonce-bound plan and summarizes contract count, transaction count, starting nonce, estimated cost, maximum cost, expiry, and plan fingerprint. It does not print private constructor data.

## 7. READY status

When all preparation succeeds, the wizard prints a scoped READY message. This means initial infrastructure deployment only. Production is still **NO**.

## 8. Deployment confirmation

Deployment mode requires:

```text
DEPLOY INITIAL GOALOS MAINNET — NO USER FUNDS
```

and a second confirmation. It cannot run in CI.

## 9. Safe resume and verification

If interrupted:

```bash
npm run goalos:mainnet:wizard -- --resume
```

If Etherscan verification is pending:

```bash
npm run goalos:mainnet:wizard -- --verify
```

After Stage B succeeds, the wizard must still show that production is not activated and user funds are not accepted.
