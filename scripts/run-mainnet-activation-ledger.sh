#!/usr/bin/env bash
set -euo pipefail
if [[ "${CI:-}" != "" ]]; then
  echo "REFUSED: CI/cloud runners may not sign or broadcast Mainnet activation." >&2
  exit 2
fi
PLAN="qa/mainnet-activation/activation-plan.public.json"
EXPECTED=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan) PLAN="$2"; shift 2 ;;
    --expected-plan-hash) EXPECTED="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
ACTUAL=$(PLAN_PATH="$PLAN" python - <<'PY'
import json, os
with open(os.environ['PLAN_PATH'], encoding='utf-8') as fh:
    print(json.load(fh).get('planHash', ''))
PY
)
if [[ -z "$EXPECTED" || "$ACTUAL" != "$EXPECTED" ]]; then
  echo "REFUSED: activation plan hash mismatch." >&2
  exit 2
fi
WALLET_B_REDACTED=$(PLAN_PATH="$PLAN" python - <<'PY'
import json, os
with open(os.environ['PLAN_PATH'], encoding='utf-8') as fh:
    w = json.load(fh).get('walletB', '')
print(w[:6] + '…' + w[-4:] if len(w) >= 10 else 'Wallet B from plan')
PY
)
printf '%s\n' "Wallet B Ledger ceremony is local-only. Review $PLAN, connect the Ledger account matching ${WALLET_B_REDACTED}, then run npm run mainnet:activation:ledger-sign when ready. Never enter a recovery phrase."
