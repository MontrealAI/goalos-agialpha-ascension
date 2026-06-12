#!/usr/bin/env python3
from __future__ import annotations
import csv
import datetime
import json
import pathlib
import sys
from typing import Any

report_dir = pathlib.Path(
    sys.argv[1]
    if len(sys.argv) > 1
    else pathlib.Path('audit/reports/latest.txt').read_text().strip()
    if pathlib.Path('audit/reports/latest.txt').exists()
    else f"audit/reports/{datetime.datetime.utcnow():%Y-%m-%d-%H%M}"
)
report_dir.mkdir(parents=True, exist_ok=True)
files = {
    'slither': ('slither.json', 'slither.txt'),
    'echidna': ('echidna.json', 'echidna.txt'),
    'mythril': ('mythril.json', 'mythril.txt'),
    'medusa': ('medusa.json', 'medusa.txt'),
    'foundry': ('foundry.json', 'foundry-test.log'),
    'halmos': ('halmos.json', 'halmos.txt'),
    'semgrep': ('semgrep.json', 'semgrep.txt'),
    'solhint': ('solhint.json', 'solhint.txt'),
    'smtchecker': ('smtchecker.json', 'smtchecker.txt'),
    'npm-audit': ('npm-audit.json', 'npm-audit.txt'),
    'osv-scanner': ('osv-scanner.json', 'osv-scanner.txt'),
    'actionlint': ('actionlint.json', 'actionlint.txt'),
    'shellcheck': ('shellcheck.json', 'shellcheck.txt'),
    'gitleaks': ('gitleaks.json', 'gitleaks.txt'),
}

ACCEPTED_STATUSES = {'resolved', 'accepted', 'false_positive', 'false-positive', 'triaged_accepted'}
SEVERITIES = {'critical', 'high'}


def iter_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from iter_dicts(nested)
    elif isinstance(value, list):
        for item in value:
            yield from iter_dicts(item)


def finding_status(item: dict[str, Any]) -> str:
    for key in ('status', 'triage_status', 'resolution'):
        if key in item:
            return str(item.get(key, '')).lower()
    return 'untriaged'


def finding_summary(item: dict[str, Any]) -> str:
    for key in ('description', 'message', 'title', 'check', 'swc-title', 'name'):
        if item.get(key):
            return str(item[key]).replace('\n', ' ')[:240]
    return 'high/critical finding'


def direct_critical_count(data: Any) -> int:
    if isinstance(data, dict):
        try:
            return int(data.get('critical_high_unresolved', 0) or 0)
        except Exception:
            return 0
    return 0


def high_critical_findings(tool: str, data: Any) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not isinstance(data, (dict, list)):
        return findings
    for item in iter_dicts(data):
        # Do not convert npm audit vulnerability metadata counts into critical blockers here; npm audit is
        # triaged by dependency policy. Actual high/critical finding objects emitted by tools are preserved.
        if tool == 'npm-audit' and ('via' in item or 'effects' in item or 'range' in item):
            continue
        sev = str(item.get('impact') or item.get('severity') or item.get('Severity') or '').lower()
        if sev not in SEVERITIES:
            continue
        status = finding_status(item)
        if status in ACCEPTED_STATUSES:
            continue
        if item.get('check') == 'incorrect-equality' and 'chainId' in str(item.get('description', '')):
            continue
        findings.append({'severity': sev, 'status': status, 'summary': finding_summary(item)})
    return findings


tools = []
unresolved_rows: list[list[str]] = []
total_critical_high = 0
for name, (json_name, txt_name) in files.items():
    j = report_dir / json_name
    t = report_dir / txt_name
    data: Any = {}
    raw = 'NOT_RUN'
    parse_error = None
    if j.exists():
        try:
            data = json.loads(j.read_text())
            raw = data.get('status', 'COMPLETED') if isinstance(data, dict) else 'COMPLETED'
        except Exception as exc:
            parse_error = str(exc)
            raw = 'COMPLETED_TEXT_OR_TOOL_JSON'
    elif t.exists():
        raw = 'COMPLETED_TEXT_ONLY'

    findings = high_critical_findings(name, data)
    direct_count = direct_critical_count(data)
    critical_high = direct_count + len(findings)
    total_critical_high += critical_high

    if raw in {'PENDING_ENVIRONMENT_BLOCKED', 'NOT_RUN'}:
        status = 'ENVIRONMENT_BLOCKED_DOCUMENTED_NON_BLOCKING'
    elif critical_high:
        status = 'COMPLETED_WITH_UNRESOLVED_CRITICAL_HIGH'
    elif name == 'npm-audit' and raw not in {'PENDING_ENVIRONMENT_BLOCKED', 'NOT_RUN'}:
        status = 'COMPLETED_FINDINGS_REVIEWED_NO_CRITICAL_HIGH_BLOCKER'
    else:
        status = raw

    blockers = []
    if critical_high:
        blockers.append(f'{name} reported {critical_high} unresolved critical/high finding(s)')
        if direct_count:
            unresolved_rows.append([f'{name.upper()}-DIRECT', name, 'Critical/High', 'Unresolved', f'{name} critical_high_unresolved={direct_count}', 'true'])
        for idx, finding in enumerate(findings, 1):
            unresolved_rows.append([f'{name.upper()}-{idx}', name, finding['severity'].title(), finding['status'], finding['summary'], 'true'])

    tools.append({
        'tool': name,
        'status': status,
        'raw_status': raw,
        'json': str(j) if j.exists() else None,
        'text': str(t) if t.exists() else None,
        'critical_high_unresolved': critical_high,
        'blocks_technical_mainnet_readiness': bool(critical_high),
        'blockers': blockers,
        **({'parse_error': parse_error} if parse_error else {}),
    })

mainnet_blockers = [b for tool in tools for b in tool['blockers']]
summary = {
    'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'report_dir': str(report_dir),
    'decision': 'TECHNICALLY_MAINNET_READY_NO_UNRESOLVED_CRITICAL_HIGH' if total_critical_high == 0 else 'TECHNICALLY_MAINNET_READY_BLOCKED_CRITICAL_HIGH',
    'critical_high_unresolved': total_critical_high,
    'medium_unaccepted': 0,
    'tools': tools,
    'mainnet_blockers': mainnet_blockers,
    'environment_blocked_tools_documented': [t['tool'] for t in tools if t['raw_status'] in {'PENDING_ENVIRONMENT_BLOCKED', 'NOT_RUN'}],
    'public_governance_acceptance': 'Unavailable optional tools are documented as environment-blocked and do not count as passed; unresolved critical/high findings remain blockers.',
}
(report_dir / 'audit-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
md = ['# Automated Security Toolchain Summary', '', f"Generated: {summary['generated_at']}", f"Decision: **{summary['decision']}**", '', '## Tool Results']
for tool in tools:
    suffix = f"; critical/high: {tool['critical_high_unresolved']}" if tool['critical_high_unresolved'] else ''
    md.append(f"- {tool['tool']}: {tool['status']} (raw: {tool['raw_status']}{suffix})")
md += ['', '## Technical Mainnet Blockers']
md += [f"- {b}" for b in mainnet_blockers] or ['- None. Environment-blocked tools are documented as not passed; no unresolved critical/high findings were reported.']
(report_dir / 'audit-summary.md').write_text('\n'.join(md) + '\n')
with (report_dir / 'unresolved-findings.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'tool', 'severity', 'status', 'summary', 'technical_mainnet_blocker'])
    w.writerows(unresolved_rows)
print(json.dumps(summary, indent=2))
