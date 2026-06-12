# Public Mainnet Authorization Runbook

GoalOS AGIALPHA Ascension v4.4.0 mainnet authorization candidate.

Run `npm run mainnet:public-authorize`, then `npm run docs:status`, `npm run assert:public-status`, `npm run qa:manifest`, and `npm run qa:manifest:verify`. This creates the certificate, validates it, computes technical readiness, deployment authorization, and Ethereum Mainnet authorization, refreshes generated public status docs, and verifies QA manifest freshness.

The private operator package is optional and is not a public YES gate. Public YES means manual, local, gated Ethereum Mainnet deployment is authorized by the certificate; it does not mean deployment occurred.

Final manual deployment command after optional branch-protection hardening and local runtime RPC/key preparation:

```bash
npm run deploy:ethereum-mainnet:gated
```

CI must not run the manual deployment command.
