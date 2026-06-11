# AGIALPHA Vault Funding Runbook v2.0

## Key point

The contracts can be deployed without funding the vaults.

Because AGIALPHA already exists, this package cannot mint AGIALPHA and should not pretend to allocate supply.

Vault funding must be performed separately by an authorized AGIALPHA holder / treasury wallet.

## Step 1 - deploy contracts

```bash
npm run deploy:ethereum-mainnet:gated
```

This creates vault addresses.

## Step 2 - generate funding instructions

```bash
npm run generate:vault-funding-instructions
```

## Step 3 - approve treasury funding decision

Complete:

- funding amount
- source wallet
- recipient vault
- purpose
- approval hash
- accounting treatment
- transaction record

## Step 4 - fund vaults

Only if approved:

```bash
ALLOW_VAULT_FUNDING=YES_FUNDER_APPROVED
VAULT_FUNDING_APPROVAL_HASH=0x...
FUND_PROOF_REWARDS_VAULT=...
npm run fund:vaults:gated
```

## Recommended initial approach

Do not fund every vault immediately.

Start small:

- proof rewards vault
- security vault
- community vault

Only fund commercialization performance vault after the commercialization SOW and tranche criteria are approved.
