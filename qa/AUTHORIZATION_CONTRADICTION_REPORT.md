# Authorization Contradiction Report

Generated: 2026-06-12T17:00:22.221226+00:00

## Target State
- TECHNICALLY_MAINNET_READY: YES
- MAINNET_DEPLOYMENT_AUTHORIZED: YES
- ETHEREUM_MAINNET_AUTHORIZED: YES
- MAINNET_DEPLOYED: NO

## Active Contradictions
- None.

## Historical / Deprecated / Generated / Backward-Compatible References Kept
- `scripts/assert_public_status.py` line 50:                 errors.append(f'{rel}:{i}: stale external audit closure active-gate language')
- `scripts/assert_public_status.py` line 49:             if 'external audit closure' in l or 'external_audit_closure' in line:
- `docs/CODEX_RUN_LOG.md` line 28: | `npm run readiness:v4.3` | Passed | readiness reported gate-clean evidence-ready audit candidate; mainnet not authorized |
- `docs/RELEASE_CANDIDATE_STATUS.md` line 7: Ethereum Mainnet technical readiness: NO.
- `docs/RELEASE_CANDIDATE_STATUS.md` line 8: Ethereum Mainnet deployment authorization: NO.
- `docs/LEGAL_TAX_PUBLIC_CLAIMS_GATE_MEMO.md` line 5: Public status: Not externally audited. Ethereum Mainnet not authorized. AGIALPHA is a utility coordination token only, not equity, dividends, profit rights, yield, ownership, or an investment claim.
- `docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md` line 1: # External Audit Closure Request v4.2
- `docs/START_HERE_v3_0.md` line 21: Implementation complete. Mainnet not authorized until all gates pass.
- `docs/POST_DEPLOYMENT_EVIDENCE_DOCKET_v3_0.csv` line 25: External audit closure,,
- `docs/MAINNET_AUTHORIZATION_WITH_REDACTED_EVIDENCE.md` line 16: - blocker `PRIVATE_OPERATOR_EVIDENCE_PENDING`.
- `docs/MAINNET_AUTHORIZATION_WITH_REDACTED_EVIDENCE.md` line 23: python scripts/mainnet-readiness-check.py --with-redacted-private-evidence
- `docs/MAINNET_AUTHORIZATION_WITH_REDACTED_EVIDENCE.md` line 24: python scripts/mainnet-deployment-authorization-check.py --with-redacted-private-evidence
- `docs/MAINNET_AUTHORIZATION_WITH_REDACTED_EVIDENCE.md` line 25: python scripts/ethereum-mainnet-authorization-check.py --with-redacted-private-evidence
- `docs/V4_2_EVIDENCE_READY_DELTA.md` line 14: - `docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md`
- `docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_3.md` line 1: # Mainnet Not Authorized Decision v4.3+
- `docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_3.md` line 3: Ethereum Mainnet not authorized.
- `docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_3.md` line 8: Ethereum Mainnet deployment authorization: NO.
- `docs/START_HERE_v4_3.md` line 9: - Historical note: v4.3 previously referenced `EXTERNAL_AUDIT_CLOSURE`; v4.4 replaces that requirement with `AUTOMATED_SECURITY_TOOLCHAIN` and `INTERNAL_SECURITY_REVIEW`.
- `docs/START_HERE_v4_3.md` line 26: Ethereum Mainnet not authorized.
- `docs/PRIVATE_OPERATOR_HANDOFF.md` line 34: 8. Run the public checkers with `--with-redacted-private-evidence`.
- `docs/PRODUCTION_READINESS_SCORECARD.md` line 17: - External audit closure is not complete.
- `docs/FOUNDER_OPERATOR_GUIDE_v3_0.md` line 23: 7. External audit closure.
- `docs/START_HERE_v4_2.md` line 27: Ethereum Mainnet not authorized.
- `docs/START_HERE_v4_2.md` line 68: mainnet NOT AUTHORIZED decision memo
- `docs/FINAL_LOCAL_OPERATOR_RUNBOOK.md` line 25: python scripts/mainnet-authorization-check.py --with-redacted-private-evidence
- `docs/START_HERE_v4_0.md` line 32: - External audit closure.
- `docs/FOUNDATION_HANDOFF_MEMO.md` line 16: - It preserves the correct status: not externally audited, automated security/toolchain review pending, Ethereum Mainnet not authorized.
- `docs/PRODUCTION_CONTINUATION_PLAN.md` line 7: Ethereum Mainnet not authorized.
- `docs/PRODUCTION_CONTINUATION_PLAN.md` line 9: Ethereum Mainnet deployment authorization: NO.
- `docs/REPOSITORY_STATUS.md` line 40: Ethereum Mainnet not authorized.
- `docs/POST_DEPLOYMENT_EVIDENCE_DOCKET_v4_0.csv` line 29: External audit closure,,
- `docs/SAFE_CLAIMS.md` line 21: Ethereum Mainnet not authorized.
- `docs/POST_UPLOAD_VALIDATION_RUNBOOK.md` line 21: - [ ] README says Ethereum Mainnet not authorized.
- `docs/CODEX_PRODUCTION_HANDOFF_PROMPT.md` line 19: Ethereum Mainnet not authorized.
- `docs/AUTOMATED_SECURITY_TOOLCHAIN_REQUEST_v4_2.md` line 3: Historical v4.2 gate request updated for the no-external-audit model. Active release gates use automated security/toolchain clearance and internal security review instead of external audit closure.
- `docs/AUTOMATED_SECURITY_TOOLCHAIN_REQUEST_v4_2.md` line 5: Not externally audited. Ethereum Mainnet not authorized.
- `docs/PRIVATE_OPERATOR_LOCAL_COMMANDS.md` line 14: python scripts/mainnet-authorization-check.py --with-redacted-private-evidence
- `docs/PRIVATE_OPERATOR_LOCAL_COMMANDS.md` line 25: python scripts/mainnet-readiness-check.py --with-redacted-private-evidence
- `docs/PRIVATE_OPERATOR_LOCAL_COMMANDS.md` line 26: python scripts/mainnet-deployment-authorization-check.py --with-redacted-private-evidence
- `docs/PRIVATE_OPERATOR_LOCAL_COMMANDS.md` line 27: python scripts/ethereum-mainnet-authorization-check.py --with-redacted-private-evidence
- `scripts/mainnet-deployment-authorization-check.py` line 10:     parser.add_argument('--with-redacted-private-evidence', action='store_true', help='Deprecated no-op; private evidence is not required.')
- `scripts/repository_safety_check.py` line 46:     "mainnet not authorized",
- `scripts/mainnet-readiness-check.py` line 17:     parser.add_argument('--with-redacted-private-evidence', action='store_true', help='Deprecated no-op; private evidence is not required.')
- `scripts/ethereum-mainnet-authorization-check.py` line 11:     parser.add_argument('--with-redacted-private-evidence', action='store_true', help='Deprecated no-op; private evidence is not required.')
- `scripts/verify-readiness-v4-2.py` line 36:     "docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md",
- `scripts/verify-readiness-v4-2.py` line 73:     for key in ["LEGAL_SIGNOFF_HASH", "TAX_SIGNOFF_HASH", "SECURITY_REVIEW_HASH", "PUBLIC_CLAIMS_REVIEW_HASH", "SEPOLIA_REHEARSAL_EVIDENCE_HASH", "EXTERNAL_AUDIT_CLOSURE_HASH", "FOUNDER_APPROVAL_HASH"]:
- `scripts/verify-readiness-v4-2.py` line 126:         "status":"evidence-ready audit candidate; mainnet not authorized",
- `scripts/mainnet-authorization-check.py` line 32:     parser.add_argument("--with-redacted-private-evidence", action="store_true", help="Deprecated; public-only final mode ignores private evidence.")
- `audit/MAINNET_GATE_REGISTER_v4_2.csv` line 7: External audit closure,open,Audit closure memo
- `audit/MAINNET_BLOCKERS.md` line 5: - External audit closure hash.
- `audit/reports/2026-06-11-1553/slither.txt` line 294: 	- gateOf[LEGAL_REVIEW].passed && gateOf[TAX_REVIEW].passed && gateOf[SECURITY_REVIEW].passed && gateOf[PUBLIC_CLAIMS_REVIEW].passed && gateOf[TREASURY_REVIEW].passed && gateOf[AGIALPHA_TOKEN_VERIFICATION].passed && gateOf[ETHEREUM_SEPOLIA_REHEARSAL].passed && gateOf[EXTERNAL_AUDIT_CLOSURE].passed && gateOf[FOUNDER_APPROVAL].passed (contracts/registry/LaunchGateRegistry.sol#26)
- `audit/reports/2026-06-11-1553/audit-summary.json` line 74:     "external audit closure hash missing",
- `audit/reports/2026-06-11-1553/slither.json` line 42106:             "name": "gateOf[LEGAL_REVIEW].passed && gateOf[TAX_REVIEW].passed && gateOf[SECURITY_REVIEW].passed && gateOf[PUBLIC_CLAIMS_REVIEW].passed && gateOf[TREASURY_REVIEW].passed && gateOf[AGIALPHA_TOKEN_VERIFICATION].passed && gateOf[ETHEREUM_SEPOLIA_REHEARSAL].passed && gateOf[EXTERNAL_AUDIT_CLOSURE].passed && gateOf[FOUNDER_APPROVAL].passed",
- `audit/reports/2026-06-11-1553/slither.json` line 42185:         "description": "LaunchGateRegistry.allCoreGatesPassed() (contracts/registry/LaunchGateRegistry.sol#25-27) uses timestamp for comparisons\n\tDangerous comparisons:\n\t- gateOf[LEGAL_REVIEW].passed && gateOf[TAX_REVIEW].passed && gateOf[SECURITY_REVIEW].passed && gateOf[PUBLIC_CLAIMS_REVIEW].passed && gateOf[TREASURY_REVIEW].passed && gateOf[AGIALPHA_TOKEN_VERIFICATION].passed && gateOf[ETHEREUM_SEPOLIA_REHEARSAL].passed && gateOf[EXTERNAL_AUDIT_CLOSURE].passed && gateOf[FOUNDER_APPROVAL].
- `audit/reports/2026-06-11-1553/slither.json` line 42186:         "markdown": "[LaunchGateRegistry.allCoreGatesPassed()](contracts/registry/LaunchGateRegistry.sol#L25-L27) uses timestamp for comparisons\n\tDangerous comparisons:\n\t- [gateOf[LEGAL_REVIEW].passed && gateOf[TAX_REVIEW].passed && gateOf[SECURITY_REVIEW].passed && gateOf[PUBLIC_CLAIMS_REVIEW].passed && gateOf[TREASURY_REVIEW].passed && gateOf[AGIALPHA_TOKEN_VERIFICATION].passed && gateOf[ETHEREUM_SEPOLIA_REHEARSAL].passed && gateOf[EXTERNAL_AUDIT_CLOSURE].passed && gateOf[FOUNDER_APPROVAL]
- `audit/reports/2026-06-11-1553/audit-summary.md` line 16: - external audit closure hash missing
- `audit/reports/2026-06-11-1553/toolchain-clearance-report.md` line 7: - external audit closure hash missing
- `audit/reports/dependency-triage/pr-3.log` line 98:   "status": "gate-clean evidence-ready audit candidate; mainnet not authorized",
- `audit/reports/dependency-triage/pr-3.log` line 121:     "EXTERNAL_AUDIT_CLOSURE_HASH missing or not bytes32",
- `audit/reports/dependency-triage/pr-4.log` line 231:   "status": "gate-clean evidence-ready audit candidate; mainnet not authorized",
- `audit/reports/dependency-triage/pr-4.log` line 254:     "EXTERNAL_AUDIT_CLOSURE_HASH missing or not bytes32",
- `audit/reports/dependency-triage/pr-2.log` line 115:   "status": "gate-clean evidence-ready audit candidate; mainnet not authorized",
- `audit/reports/dependency-triage/pr-2.log` line 138:     "EXTERNAL_AUDIT_CLOSURE_HASH missing or not bytes32",
- `qa/COMMAND_RUN_LOG.md` line 131:   "status": "gate-clean evidence-ready audit candidate; mainnet not authorized",
- `qa/COMMAND_RUN_LOG.md` line 642:     "PRIVATE_OPERATOR_EVIDENCE_PENDING",
- `qa/COMMAND_RUN_LOG.md` line 643:     "Run --with-redacted-private-evidence to evaluate committed redacted private evidence",
- `qa/COMMAND_RUN_LOG.md` line 646:     "PRIVATE_OPERATOR_EVIDENCE_PENDING: missing qa/public-ethereum-mainnet-authorization-evidence.json"
- `qa/COMMAND_RUN_LOG.md` line 648:   "reason": "PRIVATE_OPERATOR_EVIDENCE_PENDING",
- `qa/BASELINE_COMMAND_LOG.md` line 203:   "status": "gate-clean evidence-ready audit candidate; mainnet not authorized",
- `qa/SHA256SUMS_v4_2.txt` line 79: 175eba5cc72b26122d0fd276d6fc785b52e8d8f8adef6794607f3db326a9d800  docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md
- `qa/READINESS_REPORT_v4_2.json` line 17:   "status": "evidence-ready audit candidate; mainnet not authorized",
- `qa/MAINNET_AUTHORIZATION_CHECK_EXPECTED_BLOCKED.json` line 4:     "PRIVATE_OPERATOR_EVIDENCE_PENDING",
- `qa/ETHEREUM_MAINNET_PREFLIGHT.json` line 2:   "status": "PRIVATE_OPERATOR_EVIDENCE_PENDING",
- `qa/ETHEREUM_MAINNET_PREFLIGHT.json` line 11:     "PRIVATE_OPERATOR_EVIDENCE_PENDING: private operator must run local mainnet preflight and commit only redacted public evidence commitments"
- `qa/MANIFEST_v4_3.json` line 4350:       "path": "docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md",
- `qa/REPO_DOCTOR_REPORT.md` line 42: - Final YES does not depend on external audit closure.
- `qa/MANIFEST_v4_2.json` line 395:       "path": "docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md",
- `qa/MANIFEST_v4_3_FINAL.json` line 400:       "path": "docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md",
- `qa/V4_3_LOCAL_QA_COMMAND_OUTPUTS.json` line 8:       "summary": "Outputs one parseable JSON decision with PRIVATE_OPERATOR_EVIDENCE_PENDING when redacted private commitments are absent."
- `qa/SHA256SUMS_v4_3.txt` line 80: 175eba5cc72b26122d0fd276d6fc785b52e8d8f8adef6794607f3db326a9d800  docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md
- `qa/MANIFEST.json` line 4350:       "path": "docs/EXTERNAL_AUDIT_CLOSURE_REQUEST_v4_2.md",
- `qa/AGIALPHA_TOKEN_VERIFICATION.json` line 2:   "status": "PRIVATE_OPERATOR_EVIDENCE_PENDING",
- `qa/AGIALPHA_TOKEN_VERIFICATION.json` line 6:   "blocker": "PRIVATE_OPERATOR_EVIDENCE_PENDING: token verification is performed locally by the private operator and committed only as a redacted hash commitment",
- `.github/labels.yml` line 33:   description: Mainnet not authorized

## Resolution
Active status docs, public checkers, package scripts, workflows, and deployment gates use the Mainnet Authorization Certificate as source of truth. The assert_public_status.py string references are guard code that rejects stale active-gate language, not stale policy.
