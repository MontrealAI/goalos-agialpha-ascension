#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/solhint.txt"; JSON="$AUDIT_REPORT_DIR/solhint.json"
if [ ! -f .solhint.json ]; then
  echo ".solhint.json is missing" > "$TXT"
  echo '{"tool":"solhint","status":"FAILED","critical_high_unresolved":1}' > "$JSON"
  exit 1
fi
set +e
npx --yes solhint@latest "contracts/**/*.sol" > "$TXT" 2>&1
STATUS=$?
set -e
python - "$TXT" "$JSON" "$STATUS" <<'PY'
import json, pathlib, sys
text=pathlib.Path(sys.argv[1]).read_text(errors='ignore'); status=int(sys.argv[3])
# Solhint exits nonzero for errors; warnings are accepted and documented.
errors=sum(1 for line in text.splitlines() if ' error ' in line.lower())
out={'tool':'solhint','status':'COMPLETED' if errors==0 else 'FAILED','exitStatus':status,'errors':errors,'warnings':text.lower().count(' warning '),'critical_high_unresolved':errors}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
if errors: sys.exit(1)
PY
