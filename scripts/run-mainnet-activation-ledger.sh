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
ACTUAL=$(python - <<PY
import json
print(json.load(open('$PLAN')).get('planHash',''))
PY
)
if [[ -z "$EXPECTED" || "$ACTUAL" != "$EXPECTED" ]]; then
  echo "REFUSED: activation plan hash mismatch." >&2
  exit 2
fi
printf '%s\n' "Wallet B Ledger ceremony is local-only. Review $PLAN, connect the Ledger for 0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99, then run npm run mainnet:activation:ledger-sign when ready. Never enter a recovery phrase."
