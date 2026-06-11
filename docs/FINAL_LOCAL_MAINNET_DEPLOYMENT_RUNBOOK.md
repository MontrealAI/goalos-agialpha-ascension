# Final Local Ethereum Mainnet Deployment Runbook

GitHub Actions must never deploy Ethereum Mainnet. The final deployment package is local-only.

Command:

```bash
python scripts/private/run-final-local-mainnet-deployment.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

Equivalent package script:

```bash
npm run deploy:ethereum-mainnet:gated:local
```

Required gates:

- chain id `1`;
- `MAINNET_TARGET=ethereum`;
- `AGIALPHA_TOKEN_ADDRESS=0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA`;
- public Ethereum Mainnet authorization JSON is `YES`;
- private authorization bundle is locally present and `YES`;
- founder approval commitment exists;
- private env is loaded locally;
- local typed confirmation is present in the private env.

No mainnet deployment occurred in this PR.


## v4.4 final gated command

The safest final command remains local-only:

```bash
npm run deploy:ethereum-mainnet:gated:local
```

It loads `.private/mainnet-operator.env` and `.private/mainnet-operator-input.json`, verifies redacted YES decisions, rejects CI, requires `DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET`, then calls the Hardhat gated deployment. The public repository stores only `qa/public-mainnet-deployment-commitment.json`; the private transcript remains `.private/deployment-transcript-private.json`.
