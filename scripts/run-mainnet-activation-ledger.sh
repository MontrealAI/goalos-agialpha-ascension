#!/usr/bin/env bash
set -euo pipefail
if [[ "${CI:-}" != "" ]]; then
  echo "REFUSED: CI/cloud cannot run the Wallet-B Ledger activation ceremony." >&2
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
python scripts/mainnet_activation.py prepare-local
ACTUAL=$(python - <<PY
import json
print(json.load(open('$PLAN')).get('planHash',''))
PY
)
if [[ -n "$EXPECTED" && "$ACTUAL" != "$EXPECTED" ]]; then
  echo "REFUSED: activation plan hash mismatch." >&2
  echo "Expected: $EXPECTED" >&2
  echo "Actual:   $ACTUAL" >&2
  exit 2
fi
cat <<EOF
Wallet-B Ledger ceremony checklist
- Open the Ethereum app on the physical Ledger.
- Confirm the address shown by the local wallet is 0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99.
- Compare activation plan hash: $ACTUAL
- Type ACTIVATE_CONTROLLED_PRODUCTION_CANARY_V1 only if every prompt matches the reviewed plan.
EOF
read -r -p "Type confirmation: " CONFIRM
if [[ "$CONFIRM" != "ACTIVATE_CONTROLLED_PRODUCTION_CANARY_V1" ]]; then
  echo "REFUSED: typed confirmation mismatch." >&2
  exit 2
fi
python scripts/mainnet_activation.py ledger-sign
