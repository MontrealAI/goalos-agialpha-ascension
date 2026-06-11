# Final Local Operator Runbook

1. Generate private templates.
2. Fill `.private/mainnet-operator-input.json` and `.private/mainnet-operator.env` locally.
3. Run private Sepolia rehearsal, mainnet preflight, founder approval verification, address ceremony commitment, and redacted evidence generation.
4. Commit only the redacted `qa/public-*.json` evidence files.
5. Re-run public authorization checks with `--with-redacted-private-evidence`.
6. If all three statuses are YES, the founder/deployer may run the local final deployment command.

Final local command:

```bash
python scripts/private/run-final-local-mainnet-deployment.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json
```

CI must never run this command.
