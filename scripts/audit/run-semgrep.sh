#!/usr/bin/env bash
set -euo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/semgrep.txt"; JSON="$AUDIT_REPORT_DIR/semgrep.json"
CMD="semgrep scan --config configs/semgrep.yml --json --output $JSON ."
if ! command -v semgrep >/dev/null 2>&1; then
  python -m pip install --user semgrep --quiet >> "$TXT" 2>&1
  export PATH="$HOME/.local/bin:$PATH"
fi
set +e
timeout 180 semgrep scan --config configs/semgrep.yml --exclude audit/reports --json --output "$JSON" . >> "$TXT" 2>&1
STATUS=$?
set -e
if [ ! -s "$JSON" ]; then
  echo "Semgrep failed to produce JSON; status=$STATUS" >> "$TXT"
  cat > "$JSON" <<JSON
{"tool":"semgrep","status":"FAILED","critical_high_unresolved":1,"error":"semgrep did not produce JSON"}
JSON
  exit 1
fi
python - "$JSON" <<'PY'
import json,sys,pathlib
p=pathlib.Path(sys.argv[1]); data=json.loads(p.read_text())
results=data.get('results',[]) if isinstance(data,dict) else []
critical=sum(1 for r in results if str(r.get('extra',{}).get('severity','')).upper() in {'ERROR','CRITICAL','HIGH'})
wrapped={'tool':'semgrep','status':'COMPLETED','rawResults':data,'critical_high_unresolved':critical,'resultCount':len(results)}
p.write_text(json.dumps(wrapped,indent=2)+'\n')

if results:
    with (p.parent / 'semgrep-findings.txt').open('w', encoding='utf-8') as fh:
        for r in results:
            extra = r.get('extra', {})
            start = r.get('start', {})
            fh.write(f"{extra.get('severity','UNKNOWN')} {r.get('check_id')} {r.get('path')}:{start.get('line')} {extra.get('message','')}\n")
print(json.dumps({'status':'COMPLETED','tool':'semgrep','critical_high_unresolved':critical,'resultCount':len(results)},indent=2))
if critical: sys.exit(1)
PY
