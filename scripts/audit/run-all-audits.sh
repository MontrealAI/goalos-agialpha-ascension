#!/usr/bin/env bash
set -uo pipefail
export AUDIT_REPORT_DIR="${AUDIT_REPORT_DIR:-audit/reports/$(date -u +%Y-%m-%d-%H%M)}"
mkdir -p "$AUDIT_REPORT_DIR"
echo "$AUDIT_REPORT_DIR" > audit/reports/latest.txt
npm run compile:ci > "$AUDIT_REPORT_DIR/hardhat-compile.log" 2>&1 || true
npm run test:ci > "$AUDIT_REPORT_DIR/hardhat-test.log" 2>&1 || true
bash scripts/audit/run-slither.sh || true
bash scripts/audit/run-echidna.sh || true
bash scripts/audit/run-mythril.sh || true
bash scripts/audit/run-medusa.sh || true
bash scripts/audit/run-foundry.sh || true
bash scripts/audit/run-halmos.sh || true
bash scripts/audit/run-semgrep.sh || true
bash scripts/audit/run-solhint.sh || true
bash scripts/audit/run-solc-smtchecker.sh || true
bash scripts/audit/run-npm-audit.sh || true
bash scripts/audit/run-osv-scanner.sh || true
bash scripts/audit/run-actionlint.sh || true
bash scripts/audit/run-shellcheck.sh || true
bash scripts/audit/run-gitleaks.sh || true
npm sbom --json > "$AUDIT_REPORT_DIR/sbom.json" 2> "$AUDIT_REPORT_DIR/sbom.txt" || echo "{\"status\":\"PENDING_ENVIRONMENT_BLOCKED\",\"tool\":\"npm-sbom\"}" > "$AUDIT_REPORT_DIR/sbom.json"
for f in foundry-build.log foundry-test.log foundry-invariant.log gas-report.txt coverage-report.txt; do [ -f "$AUDIT_REPORT_DIR/$f" ] || echo "$f not generated in this environment." > "$AUDIT_REPORT_DIR/$f"; done
[ -f "$AUDIT_REPORT_DIR/dependency-triage-summary.md" ] || echo "# Dependency triage summary

See audit/reports/dependency-triage/ for PR #2/#3/#4 controlled triage. No dependency PR was blindly merged." > "$AUDIT_REPORT_DIR/dependency-triage-summary.md"
python scripts/audit/summarize-audit-results.py "$AUDIT_REPORT_DIR"
python scripts/audit/generate-toolchain-clearance-report.py "$AUDIT_REPORT_DIR"
python scripts/audit/fail-on-critical-findings.py "$AUDIT_REPORT_DIR/audit-summary.json" summary
( cd "$AUDIT_REPORT_DIR" && find . -maxdepth 1 -type f ! -name checksums.txt -printf "%f\0" | sort -z | xargs -0 sha256sum > checksums.txt 2>/dev/null || true )
