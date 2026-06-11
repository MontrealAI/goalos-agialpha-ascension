# Final Local Mainnet Deployment Runbook

Final deployment is local-only and requires private operator inputs:

```bash
python scripts/private/run-final-local-mainnet-deployment.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

The script must verify public authorization JSON is YES, private authorization bundle is YES, chainId is 1, AGIALPHA token address is exact, founder approval commitment exists, and the local typed confirmation phrase is supplied. GitHub Actions must never execute this command.
