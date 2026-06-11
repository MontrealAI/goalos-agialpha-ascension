from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "README.md"] + sorted((ROOT / "docs").glob("*.md"))
text_by_file = {p: p.read_text(encoding="utf-8", errors="ignore") for p in DOCS if p.exists()}
combined = "\n".join(text_by_file.values())
combined_lower = combined.lower()
errors: list[str] = []

mainnet_not_authorized = re.search(r"ethereum\s+mainnet\s+(deployment\s+authorization:\s+no|not[_\s-]*authorized|is\s+not\s+authorized)", combined, re.I) or "mainnet_deployment_authorized: **no**" in combined_lower
if not mainnet_not_authorized and "technically_mainnet_ready: **yes**" not in combined_lower:
    errors.append("Missing clear Ethereum Mainnet not-authorized/deployment authorization NO statement.")

if "not externally audited" not in combined_lower:
    errors.append("Missing allowed public status: Not externally audited.")
if not re.search(r"automated security/toolchain (review|clearance):? (pending|completed|completed with blockers)", combined, re.I) and "AUTOMATED_SECURITY_TOOLCHAIN" not in combined:
    errors.append("Missing automated security/toolchain clearance or equivalent internal security gate.")

unsafe_patterns = [
    ("externally audited", re.compile(r"\bexternally audited\b", re.I), ["not externally audited", "do not", "do **not**", "must not"]),
    ("mainnet authorized", re.compile(r"\bmainnet[-\s]+authorized\b", re.I), ["not mainnet authorized", "not-authorized", "not authorized", "do not", "do **not**", "must not", "unless", "without"]),
    ("mainnet deployment authorized", re.compile(r"mainnet deployment authorization:\s*(yes|authorized)", re.I), []),
    ("production deployed", re.compile(r"\bproduction deployed\b", re.I), ["not", "do not", "do **not**", "must not", "avoid", "unless", "without"]),
    ("guaranteed non-security", re.compile(r"\bguaranteed non-security\b", re.I), ["do not", "do **not**", "must not", "not", "no ", "avoid", "unless", "without"]),
    ("investment", re.compile(r"\binvestment\b", re.I), ["not", "no ", "do not", "do **not**", "must not", "avoid", "without", "nor", "unless", "forbidden", "boundary"]),
    ("yield", re.compile(r"\byield\b", re.I), ["not", "no ", "do not", "do **not**", "must not", "avoid", "without", "nor", "unless", "forbidden", "boundary"]),
    ("revenue share", re.compile(r"\brevenue[-\s]+share\b", re.I), ["not", "no ", "do not", "do **not**", "must not", "avoid", "without", "nor", "unless", "forbidden", "boundary"]),
    ("price target", re.compile(r"\bprice[-\s]+target\b", re.I), ["not", "no ", "do not", "do **not**", "must not", "avoid", "without", "nor", "unless", "forbidden", "boundary"]),
]
active_gate_files = {"README.md", "docs/CURRENT_STATUS.md", "docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_3.md", "docs/MAINNET_TECHNICAL_READINESS_DECISION.md", "docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.md", "docs/MAINNET_AUTHORIZATION_DECISION.md", "docs/PRODUCTION_CONTINUATION_PLAN.md"}
for path, text in text_by_file.items():
    rel = str(path.relative_to(ROOT))
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        normalized = low.strip().lstrip("-*•0123456789. )").rstrip(".;:")
        positive_context = any(token in low for token in [" is ", " are ", " status", "authorized: yes", "authorization: yes", "externally audited.", "production deployed."])
        negative_context = any(token in low for token in [": no", "not", "no ", "do not", "do **not**", "must not", "avoid", "unless", "without", "prohibited", "out of scope", "forbidden", "boundary"])
        if normalized in {"externally audited", "audited", "mainnet authorized", "production deployed", "guaranteed non-security", "investment", "investment opportunity", "investment return", "yield", "revenue share", "price target"}:
            continue
        for label, pattern, allowed in unsafe_patterns:
            if pattern.search(line) and not any(a in low for a in allowed) and positive_context and not negative_context:
                errors.append(f"{rel}:{i}: unsafe public claim or stale phrase: {label}")
        if rel in active_gate_files and re.search(r"external audit (required|closure)", line, re.I):
            errors.append(f"{rel}:{i}: stale external audit gate language")
        if rel in active_gate_files and "EXTERNAL_AUDIT_CLOSURE" in line:
            errors.append(f"{rel}:{i}: stale EXTERNAL_AUDIT_CLOSURE gate")

if errors:
    print("Public status assertion failed:")
    for err in errors:
        print(f"- {err}")
    sys.exit(1)
print("Public status assertion passed: Ethereum Mainnet is not authorized, public claims are bounded, and external-audit closure is not an active required gate.")
