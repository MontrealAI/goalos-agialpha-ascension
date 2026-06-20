# GoalOS deployment: 10 SECURITY AND SECRETS

Install:
npm ci

Start:
npm run deploy

GoalOS uses a guided command center for Sepolia and Ethereum Mainnet. Sepolia is Ethereum's public test network. Mainnet is real Ethereum where gas costs real ETH. The deployer wallet sends deployment transactions. The final Owner controls the finished system; for Mainnet, use a Safe when possible. A Safe is a shared-control wallet with multiple approvers.

## Claim boundary

This page is an operator guide. It does not claim that Mainnet is deployed, verified, handed off, or operational. Those claims require real chain evidence, verification evidence, Owner acceptance, deployer-role cleanup, and canary evidence.

## Standard next steps

1. Run `npm ci`.
   Expected result: dependencies install from the lockfile.
2. Run `npm run deploy`.
   Expected result: the GoalOS Deployment Command Center opens.
3. Choose Sepolia first unless a release-bound Mainnet waiver is approved.
   Expected result: the wizard prints PASS, WARNING, BLOCKED, and NEXT STEP messages.

## What stays private

Never share private keys, mnemonic phrases, RPC URLs, API tokens, Safe signer lists, signatures, or files from `.private/`.

## You are done only when

- Runtime bytecode and configuration are read back from the expected chain.
- Source verification is complete or already verified with evidence.
- The final Owner has accepted ownership.
- Disposable deployer roles are removed.
- Canary limits remain finite and evidence is generated.
