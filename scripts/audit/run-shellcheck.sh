#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/shellcheck.txt"
JSON="$AUDIT_REPORT_DIR/shellcheck.json"
: > "$TXT"
mapfile -t SHELL_FILES < <(find scripts -type f -name '*.sh' -not -path '*/node_modules/*' | sort)
if [ "${#SHELL_FILES[@]}" -eq 0 ]; then
  cat > "$JSON" <<'JSON'
{
  "tool": "shellcheck",
  "status": "COMPLETED",
  "mode": "no-shell-scripts-found",
  "exitStatus": 0,
  "critical_high_unresolved": 0,
  "filesChecked": []
}
JSON
  cat "$JSON"
  exit 0
fi

if command -v shellcheck >/dev/null 2>&1; then
  RAW_JSON="$AUDIT_REPORT_DIR/shellcheck.raw.json"
  STDERR="$AUDIT_REPORT_DIR/shellcheck.stderr.txt"
  set +e
  shellcheck -f json "${SHELL_FILES[@]}" > "$RAW_JSON" 2> "$STDERR"
  STATUS=$?
  set -e
  MODE="shellcheck"
  python - "$RAW_JSON" "$STDERR" "$TXT" "$JSON" "$STATUS" "$MODE" "${SHELL_FILES[@]}" <<'PY'
import json, pathlib, sys
raw_path, stderr_path, txt_path, json_path = map(pathlib.Path, sys.argv[1:5])
status = int(sys.argv[5])
mode = sys.argv[6]
files = sys.argv[7:]
raw_text = raw_path.read_text(errors="ignore") if raw_path.exists() else ""
stderr_text = stderr_path.read_text(errors="ignore") if stderr_path.exists() else ""
try:
    data = json.loads(raw_text) if raw_text.strip() else []
except Exception as exc:
    data = {"parse_error": str(exc), "raw": raw_text[:4000]}
comments = data if isinstance(data, list) else data.get("comments", []) if isinstance(data, dict) else []
errors = [c for c in comments if isinstance(c, dict) and str(c.get("level", "")).lower() == "error"]
warnings = [c for c in comments if isinstance(c, dict) and str(c.get("level", "")).lower() == "warning"]
infos = [c for c in comments if isinstance(c, dict) and str(c.get("level", "")).lower() in {"info", "style"}]
command_failed = status not in (0, 1)
critical = len(errors) + (1 if command_failed else 0)
out = {
    "tool": "shellcheck",
    "status": "FAILED" if critical else "COMPLETED",
    "mode": mode,
    "exitStatus": status,
    "critical_high_unresolved": critical,
    "filesChecked": files,
    "errorCount": len(errors),
    "warningCount": len(warnings),
    "infoCount": len(infos),
    "rawResults": data,
    "stderr": stderr_text[:4000],
}
pathlib.Path(json_path).write_text(json.dumps(out, indent=2) + "\n")
summary = [
    f"shellcheck status={out['status']} exitStatus={status}",
    f"filesChecked={len(files)} errors={len(errors)} warnings={len(warnings)} infos={len(infos)}",
]
if stderr_text.strip():
    summary += ["", "stderr:", stderr_text]
pathlib.Path(txt_path).write_text("\n".join(summary) + "\n")
print(json.dumps({k: out[k] for k in ["tool", "status", "mode", "exitStatus", "critical_high_unresolved"]}, indent=2))
if critical:
    sys.exit(1)
PY
else
  set +e
  for file in "${SHELL_FILES[@]}"; do
    bash -n "$file" >> "$TXT" 2>&1 || STATUS=$?
  done
  STATUS="${STATUS:-0}"
  set -e
  MODE="bash-syntax-equivalent"
  python - "$TXT" "$JSON" "$STATUS" "$MODE" "${SHELL_FILES[@]}" <<'PY'
import json, pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text(errors="ignore")
status = int(sys.argv[3])
mode = sys.argv[4]
files = sys.argv[5:]
out = {
    "tool": "shellcheck",
    "status": "COMPLETED" if status == 0 else "FAILED",
    "mode": mode,
    "exitStatus": status,
    "critical_high_unresolved": 0 if status == 0 else 1,
    "filesChecked": files,
    "output": text[:4000],
}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: out[k] for k in ["tool", "status", "mode", "exitStatus", "critical_high_unresolved"]}, indent=2))
if status:
    sys.exit(1)
PY
fi
python - "$JSON" "$TXT" <<'PY'
import json, pathlib, sys
from scripts.audit.audit_model import stable_fingerprint, write_normalized
path=pathlib.Path(sys.argv[1]); txt=pathlib.Path(sys.argv[2])
try: legacy=json.loads(path.read_text())
except Exception as exc:
    legacy={'tool':'shellcheck','status':'MALFORMED','critical_high_unresolved':1,'error':str(exc)}
critical=int(legacy.get('critical_high_unresolved',0) or 0)
findings=[]
for i in range(critical):
    findings.append({'fingerprint':stable_fingerprint('shellcheck','SHELLCHECK_FINDING','scripts','',str(txt),str(txt),i),'id':'SHELLCHECK_FINDING','tool':'shellcheck','severity':'high','status':'unresolved','title':'shellcheck/bash syntax finding','packageOrContract':'scripts','installedVersion':'','fixedVersion':'','dependencyPath':'','file':str(txt),'line':None,'description':legacy.get('output') or legacy.get('stderr') or legacy.get('error',''),'evidence':[str(txt)],'triageRef':''})
state='FAILED' if critical else 'COMPLETED'
obj=write_normalized(path,'shellcheck','shellcheck -f json scripts/**/*.sh or bash -n fallback',int(legacy.get('exitStatus',0) or 0),findings,[str(txt)],state)
obj['mode']=legacy.get('mode'); obj['filesChecked']=legacy.get('filesChecked',[])
path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
PY
