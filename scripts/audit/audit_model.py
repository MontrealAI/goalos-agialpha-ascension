#!/usr/bin/env python3
from __future__ import annotations
import csv, datetime as dt, hashlib, json, os, pathlib, subprocess, sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORTS = ROOT / "audit" / "reports"
TRIAGE_PATH = ROOT / "audit" / "TRIAGE.json"
SEVERITIES = {"critical", "high"}
MANDATORY = {"slither", "semgrep", "solhint", "npm-audit", "osv-scanner", "actionlint", "shellcheck", "gitleaks"}


def sh(cmd:list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()

def maybe_sh(cmd:list[str]) -> str:
    try: return sh(cmd)
    except Exception as exc: return f"UNAVAILABLE: {exc}"

def sha_file(path:pathlib.Path) -> str|None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def current_report_dir() -> pathlib.Path:
    latest = REPORTS / "latest.txt"
    if latest.exists() and latest.read_text().strip():
        return ROOT / latest.read_text().strip()
    return REPORTS / "missing"

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def stable_fingerprint(tool:str, advisory_id:str, package:str, version:str, path:str, file:str="", line:Any=None) -> str:
    key = "|".join([advisory_id or "UNKNOWN", package or "", version or "", path or "", file or "", str(line or "")])
    return hashlib.sha256(key.encode()).hexdigest()[:24]

def load_json(path:pathlib.Path) -> Any:
    return json.loads(path.read_text())

def source_sha() -> str:
    return maybe_sh(["git", "rev-parse", "HEAD"])

def lock_hash() -> str|None:
    return sha_file(ROOT / "package-lock.json")

def load_triage(now:dt.date|None=None) -> tuple[dict[tuple[str,str,str],dict], list[str]]:
    errors=[]; out={}
    if not TRIAGE_PATH.exists():
        return out, ["audit/TRIAGE.json is missing"]
    try: data=load_json(TRIAGE_PATH)
    except Exception as exc: return out, [f"audit/TRIAGE.json is malformed: {exc}"]
    now = now or dt.datetime.now(dt.timezone.utc).date()
    for entry in data.get("entries", []):
        key=(str(entry.get("advisoryId","")), str(entry.get("package","")), str(entry.get("installedVersion","")))
        status=entry.get("status")
        if status not in {"resolved","false_positive","temporarily_accepted"}:
            errors.append(f"Invalid triage status for {key}: {status}")
            continue
        try: expires=dt.date.fromisoformat(str(entry.get("expiresAt")))
        except Exception:
            errors.append(f"Invalid triage expiry for {key}"); continue
        if status=="temporarily_accepted" and expires < now:
            errors.append(f"Expired triage for {key}")
        if not entry.get("rationale") or not entry.get("approvedBy"):
            errors.append(f"Incomplete triage evidence for {key}")
        out[key]=entry
    return out, errors

def apply_triage(finding:dict, triage:dict[tuple[str,str,str],dict]) -> dict:
    key=(finding.get("id",""), finding.get("packageOrContract",""), finding.get("installedVersion",""))
    entry=triage.get(key)
    if entry:
        finding=dict(finding)
        finding["status"] = entry["status"]
        finding["triageRef"] = f"audit/TRIAGE.json#{entry['advisoryId']}:{entry['package']}:{entry['installedVersion']}"
        finding.setdefault("evidence", []).extend(entry.get("evidencePaths", []))
    return finding

def npm_findings(audit_json:dict, triage:dict[tuple[str,str,str],dict]) -> list[dict]:
    findings=[]
    lock_versions={}
    try:
        lock=json.loads((ROOT / "package-lock.json").read_text())
        for node, meta in lock.get("packages", {}).items():
            if node.startswith("node_modules/") and isinstance(meta, dict):
                lock_versions[node.split("/", 1)[1]] = str(meta.get("version", ""))
    except Exception:
        pass
    for package, vuln in audit_json.get("vulnerabilities", {}).items():
        version = lock_versions.get(package, "")
        for via in vuln.get("via", []):
            if not isinstance(via, dict): continue
            sev=str(via.get("severity", vuln.get("severity", ""))).lower()
            if sev not in SEVERITIES: continue
            dep_path=" > ".join(vuln.get("nodes", [])) or package
            advisory_id=str(via.get("url", "")).rstrip("/").split("/")[-1] or str(via.get("source", "UNKNOWN"))
            f={
                "fingerprint": stable_fingerprint("npm-audit", advisory_id, package, version, dep_path),
                "id": advisory_id,
                "tool": "npm-audit",
                "severity": sev,
                "status": "unresolved",
                "title": str(via.get("title") or package),
                "packageOrContract": package,
                "installedVersion": version,
                "fixedVersion": str(via.get("range", "")),
                "dependencyPath": dep_path,
                "file": "package-lock.json",
                "line": None,
                "description": str(via.get("title") or ""),
                "evidence": [str(via.get("url", ""))],
                "triageRef": ""
            }
            findings.append(apply_triage(f, triage))
    return findings

def write_normalized(path:pathlib.Path, tool:str, command:str, exit_status:int, findings:list[dict], raw_paths:list[str], status:str="COMPLETED", tool_version:str="") -> dict:
    unresolved=[f for f in findings if f.get("severity") in SEVERITIES and f.get("status") == "unresolved"]
    obj={"schemaVersion":"2.0","tool":tool,"toolVersion":tool_version,"command":command,"sourceSha":source_sha(),"status":status,"exitStatus":exit_status,"findings":findings,"criticalHighUnresolved":len(unresolved),"rawOutputPaths":raw_paths,"generatedAt":utc()}
    path.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n")
    return obj

def write_summary(report_dir:pathlib.Path, normalized:list[dict], triage_errors:list[str]) -> dict:
    by_fp={}; tool_failures=[]; unavailable=[]
    current_source_sha = source_sha()
    for result in normalized:
        tool=result.get("tool")
        status=result.get("status")
        result_source_sha = result.get('sourceSha')
        if tool in MANDATORY and status not in {"COMPLETED", "COMPLETED_WITH_FINDINGS"}:
            tool_failures.append({"tool":tool,"status":status})
        if result.get('schemaVersion') == '2.0' and tool and result_source_sha != current_source_sha:
            tool_failures.append({"tool":tool,"status":"STALE_SOURCE_SHA","sourceSha":result_source_sha,"currentSourceSha":current_source_sha})
        for f in result.get("findings", []):
            fp=f.get("fingerprint") or stable_fingerprint(tool, f.get("id",""), f.get("packageOrContract",""), f.get("installedVersion",""), f.get("dependencyPath",""), f.get("file",""), f.get("line"))
            if fp in by_fp:
                by_fp[fp].setdefault("sourceScanners", sorted({by_fp[fp].get("tool"), tool}))
            else:
                by_fp[fp]=dict(f)
    unresolved=[f for f in by_fp.values() if f.get("severity") in SEVERITIES and f.get("status") == "unresolved"]
    evidence={p.name: sha_file(p) for p in sorted(report_dir.glob("*.json")) if p.name != "audit-summary.json"}
    decision="PASS" if not unresolved and not tool_failures and not triage_errors else "BLOCKED"
    summary={"schemaVersion":"2.0","sourceSha":current_source_sha,"lockfileHash":lock_hash(),"decision":decision,"criticalHighUnresolved":len(unresolved),"unresolvedFindings":unresolved,"toolFailures":tool_failures,"unavailableMandatoryTools":unavailable,"triageErrors":triage_errors,"evidenceHashes":evidence,"runDirectory":str(report_dir),"generatedAt":utc()}
    (report_dir/"audit-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    md=["# Audit Summary", "", f"Decision: **{decision}**", f"Critical/high unresolved: **{len(unresolved)}**", "", "## Unresolved findings"]
    md += [f"- {f['id']} | {f['packageOrContract']} | {f['severity']} | {f.get('dependencyPath','')}" for f in unresolved] or ["- None"]
    md += ["", "## Tool failures"] + ([f"- {x['tool']}: {x['status']}" for x in tool_failures] or ["- None"])
    if triage_errors: md += ["", "## Triage errors"] + [f"- {e}" for e in triage_errors]
    (report_dir/"audit-summary.md").write_text("\n".join(md)+"\n")
    with (report_dir/"unresolved-findings.csv").open("w", newline="") as f:
        w=csv.writer(f); w.writerow(["id","tool","severity","status","packageOrContract","installedVersion","dependencyPath","title"])
        for item in unresolved: w.writerow([item.get(k,"") for k in ["id","tool","severity","status","packageOrContract","installedVersion","dependencyPath","title"]])
    return summary
