#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/shellcheck.txt"; JSON="$AUDIT_REPORT_DIR/shellcheck.json"
if command -v shellcheck >/dev/null 2>&1; then
  set +e
  find scripts -name '*.sh' -print0 | xargs -0 shellcheck > "$TXT" 2>&1
  STATUS=$?
  set -e
  MODE="shellcheck"
else
  set +e
  find scripts -name '*.sh' -print0 | xargs -0 -I{} bash -n {} > "$TXT" 2>&1
  STATUS=$?
  set -e
  MODE="bash-syntax-equivalent"
fi
python - "$TXT" "$JSON" "$STATUS" "$MODE" <<'PY'
import json,pathlib,sys
text=pathlib.Path(sys.argv[1]).read_text(errors='ignore'); status=int(sys.argv[3]); mode=sys.argv[4]
out={'tool':'shellcheck','status':'COMPLETED' if status==0 else 'FAILED','mode':mode,'exitStatus':status,'critical_high_unresolved':0 if status==0 else 1,'output':text[:4000]}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['tool','status','mode','exitStatus','critical_high_unresolved']},indent=2))
if status: sys.exit(1)
PY
