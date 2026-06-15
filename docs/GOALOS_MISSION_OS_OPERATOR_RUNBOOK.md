# GoalOS Mission OS — Operator Runbook

## Local operation

1. Pick a mission file in `examples/mission-os/`.
2. Run the generator:

```bash
python scripts/mission-os/mission_os_until_done.py \
  --mission examples/mission-os/ai-product-intelligence.json \
  --out evidence/mission-os/ai-product-intelligence-001 \
  --max-cycles 8
```

3. Check completion:

```bash
python scripts/mission-os/done_check.py evidence/mission-os/ai-product-intelligence-001
```

4. Review the Evidence Docket and generated index page.
5. Publish only after human review.

## GitHub Actions operation

Run the workflow:

```text
GoalOS Mission OS — Autonomous Until Done
```

Inputs:

- `mission_file`: path to a JSON mission file.
- `output_dir`: where generated artifacts should be written.
- `max_cycles`: maximum repair cycles.

The workflow opens a pull request. It never auto-merges.

## Operator safety rules

- No Mainnet broadcast.
- No token movement.
- No unsupported AGI / ASI / ROI / audit / production claims.
- No public promotion without human review.
- No secrets in mission files or generated artifacts.
