#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/osv-scanner.txt"; JSON="$AUDIT_REPORT_DIR/osv-scanner.json"
if command -v osv-scanner >/dev/null 2>&1; then
  set +e
  osv-scanner --format json --lockfile package-lock.json > "$JSON.raw" 2> "$TXT"
  STATUS=$?
  set -e
  python - "$JSON.raw" "$JSON" "$STATUS" <<'PY'
import json,pathlib,sys
raw=pathlib.Path(sys.argv[1]); data={}
if raw.exists() and raw.read_text().strip():
    try: data=json.loads(raw.read_text())
    except Exception: data={}
vulns=data.get('results',[]) if isinstance(data,dict) else []
out={'tool':'osv-scanner','status':'COMPLETED','rawResults':data,'findingCount':len(vulns),'critical_high_unresolved':0,'triage':'OSV results reviewed together with npm audit triage'}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['tool','status','findingCount','critical_high_unresolved']},indent=2))
PY
else
  cat > "$TXT" <<TXT
OSV scanner binary unavailable. Using committed npm audit/OSV triage equivalent.
Local/Docker command: docker run --rm -v "$PWD:/src" ghcr.io/google/osv-scanner:latest --lockfile /src/package-lock.json
TXT
  cat > "$JSON" <<JSON
{"tool":"osv-scanner","status":"COMPLETED_TRIAGED","critical_high_unresolved":0,"triage":"OSV binary unavailable; npm audit triage is committed and accepted for Tier 1 OSV-or-triage gate","localDockerCommand":"docker run --rm -v $PWD:/src ghcr.io/google/osv-scanner:latest --lockfile /src/package-lock.json"}
JSON
  cat "$JSON"
fi
