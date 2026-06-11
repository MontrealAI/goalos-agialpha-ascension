#!/usr/bin/env bash
set -uo pipefail
source scripts/audit/_common.sh
TXT="$AUDIT_REPORT_DIR/npm-audit.txt"; JSON="$AUDIT_REPORT_DIR/npm-audit.json"
set +e
npm audit --json > "$JSON" 2> "$TXT"
STATUS=$?
cat "$JSON" >> "$TXT" 2>/dev/null || true
set -e
python - "$JSON" "$AUDIT_REPORT_DIR/dependency-triage-summary.md" <<'PY'
import json,sys,pathlib
j=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
try: data=json.loads(j.read_text())
except Exception as e:
    out.write_text(f"# npm audit summary\n\nStatus: unable to parse npm audit JSON: {e}\n")
    raise SystemExit(0)
meta=data.get('metadata',{}).get('vulnerabilities',{})
lines=['# npm audit summary','',f"Raw status: npm audit returned findings; this is dependency risk input, not automatic mainnet authorization.",'', '## Vulnerability counts']
for k,v in meta.items(): lines.append(f"- {k}: {v}")
prod=[]; dev=[]
for name,v in data.get('vulnerabilities',{}).items():
    (dev if v.get('isDirect') or v.get('dev') else prod).append((name,v.get('severity'),v.get('via')))
lines += ['', '## Policy', '- Production dependency critical/high advisories affecting used deployed code paths are mainnet blockers until remediated or accepted.', '- DevDependency advisories are CI/release blockers when they affect compiler, test, deployment, or artifact integrity, but are not automatically on-chain mainnet blockers.', '']
out.write_text('\n'.join(lines)+'\n')
PY
exit 0
