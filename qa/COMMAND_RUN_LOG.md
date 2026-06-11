## npm run repo:all
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 repo:all
> python scripts/repository_safety_check.py && python scripts/repository_status_check.py && python scripts/repository_production_readiness_check.py && python scripts/no_paid_products_check.py && python scripts/no_private_operator_data_check.py

Repository safety check passed.
Repository status check passed.
{
  "status": "passed",
  "errors": [],
  "warnings": [],
  "message": "Repository is production-continuation ready as a GitHub starter candidate."
}
Paid/private product check passed.
Private operator data check passed.
EXIT_STATUS=0
## npm run repo:no-private-operator-data
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 repo:no-private-operator-data
> python scripts/no_private_operator_data_check.py

Private operator data check passed.
EXIT_STATUS=0
## npm run repo:no-paid-products
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 repo:no-paid-products
> python scripts/no_paid_products_check.py

Paid/private product check passed.
EXIT_STATUS=0
## npm run assert:public-status
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 assert:public-status
> python scripts/assert_public_status.py

Public status assertion passed: Ethereum Mainnet is not authorized, public claims are bounded, and external-audit closure is not an active required gate.
EXIT_STATUS=0
## npm run compile
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 compile
> hardhat compile

Downloading compiler 0.8.24
Generating typings for: 80 artifacts in dir: typechain-types for target: ethers-v6
Successfully generated 190 typings!
Compiled 78 Solidity files successfully (evm target: paris).
EXIT_STATUS=0
## npm test
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 test
> hardhat test



  AEP-001 / AGIALPHA Ascension proof-of-evolution spine
    ✔ runs Aim -> Act -> Prove -> Evolve on-chain commitments (1378ms)

  GoalOS AGIALPHA Ascension flow
    ✔ creates a Proof Seed using AGIALPHA (222ms)
    ✔ runs post -> claim -> submit -> review -> proof card -> credential -> reputation with AGIALPHA (216ms)
    ✔ anchors a legacy AGIJobManager record as reviewed history (179ms)

  GoalOS AGIALPHA Ascension v4 institutional controls
    ✔ records conformance, claim boundary, replay, chronicle and falsification records (156ms)
    ✔ supports commit-reveal validation (160ms)
    ✔ supports evaluator staking, slashing court, and reward vault (159ms)

  v4.3 Ethereum launch gate consistency
    ✔ uses Ethereum Sepolia and complete institutional gates (64ms)


  8 passing (3s)

EXIT_STATUS=0
## npm run test:all
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 test:all
> hardhat test test/agialphaAscensionFlow.test.ts test/aepAscensionFlow.test.ts test/v4InstitutionalControls.test.ts test/v4_3EthereumGateConsistency.test.ts



  GoalOS AGIALPHA Ascension flow
    ✔ creates a Proof Seed using AGIALPHA (1456ms)
    ✔ runs post -> claim -> submit -> review -> proof card -> credential -> reputation with AGIALPHA (216ms)
    ✔ anchors a legacy AGIJobManager record as reviewed history (160ms)

  AEP-001 / AGIALPHA Ascension proof-of-evolution spine
    ✔ runs Aim -> Act -> Prove -> Evolve on-chain commitments (278ms)

  GoalOS AGIALPHA Ascension v4 institutional controls
    ✔ records conformance, claim boundary, replay, chronicle and falsification records (155ms)
    ✔ supports commit-reveal validation (136ms)
    ✔ supports evaluator staking, slashing court, and reward vault (138ms)

  v4.3 Ethereum launch gate consistency
    ✔ uses Ethereum Sepolia and complete institutional gates (56ms)


  8 passing (3s)

EXIT_STATUS=0
## npm run static-check
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 static-check
> python scripts/static_check.py

Static QA passed.
Files checked: 1059
EXIT_STATUS=0
## npm run readiness:v4.3
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 readiness:v4.3
> python scripts/verify-readiness-v4-3.py

{
  "package": "GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY",
  "generated_at": "2026-06-11T22:25:45.368516+00:00",
  "static_readiness": "passed",
  "files_checked": 1058,
  "errors": [],
  "warnings": [],
  "status": "gate-clean evidence-ready audit candidate; mainnet not authorized",
  "score_current_state": "9.6/10 audit-candidate package; not 10/10 until executed evidence and internal security review exist",
  "next_gate": "real Ethereum Sepolia rehearsal and filled Evidence Docket"
}
EXIT_STATUS=0
## npm run evidence:docket:template
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 evidence:docket:template
> python scripts/generate-evidence-docket-template.py

{
  "status": "EVIDENCE_DOCKET_TEMPLATE_WRITTEN",
  "path": "evidence/SEPOLIA_EVIDENCE_DOCKET_TEMPLATE_v4_2.json",
  "sha256": "ba4c166355fb15a9fe6f145c0b07d237bfb731257d19360123a27fc815274bff"
}
EXIT_STATUS=0
## npm run rehearse:local
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 rehearse:local
> hardhat run scripts/rehearse-local-authorization-chain.ts --network hardhat

{
  "status": "PASSED",
  "scope": "LOCAL_SIMULATION_ONLY",
  "manifest": "deployments/local.agialpha.latest.json",
  "manifestHash": "0x74cd5a7da275e0d754035670d56018d96cf84ff85305198147bac17c3d09e82b",
  "contractsDeployed": 17,
  "proofWorkLoopCompleted": true,
  "negativePathsCompleted": true,
  "generatedAt": "2026-06-11T22:25:59.535Z",
  "mainnetEvidence": false,
  "publicSepoliaEvidence": false,
  "containsSecrets": false,
  "containsPrivateAddresses": false
}
EXIT_STATUS=0
## npm run evidence:local
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 evidence:local
> python scripts/generate-local-evidence-docket.py

{
  "status": "LOCAL_SIMULATION_ONLY",
  "generatedAt": "2026-06-11T22:26:02.722931+00:00",
  "manifest": "deployments/local.agialpha.latest.json",
  "manifestHash": "0x1c2436b82bb2f34a80c3001ab132a5330d10e673e363b125524c7299ecab02c6",
  "mainnetEvidence": false,
  "publicSepoliaEvidence": false
}
EXIT_STATUS=0
## npm run audit:slither
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:slither
> bash scripts/audit/run-slither.sh

EXIT_STATUS=0
## npm run audit:foundry
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:foundry
> bash scripts/audit/run-foundry.sh

EXIT_STATUS=0
## npm run audit:echidna
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:echidna
> bash scripts/audit/run-echidna.sh

EXIT_STATUS=0
## npm run audit:medusa
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:medusa
> bash scripts/audit/run-medusa.sh

EXIT_STATUS=0
## npm run audit:mythril
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:mythril
> bash scripts/audit/run-mythril.sh

EXIT_STATUS=0
## npm run audit:semgrep
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:semgrep
> bash scripts/audit/run-semgrep.sh

EXIT_STATUS=0
## npm run audit:solhint
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:solhint
> bash scripts/audit/run-solhint.sh

EXIT_STATUS=0
## npm run audit:actions
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:actions
> bash scripts/audit/run-actionlint.sh

EXIT_STATUS=0
## npm run audit:shell
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:shell
> bash scripts/audit/run-shellcheck.sh

EXIT_STATUS=0
## npm run audit:secrets
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:secrets
> bash scripts/audit/run-gitleaks.sh

EXIT_STATUS=0
## npm run audit:npm
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:npm
> bash scripts/audit/run-npm-audit.sh

EXIT_STATUS=0
## npm run audit:osv
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:osv
> bash scripts/audit/run-osv-scanner.sh

EXIT_STATUS=0
## npm run audit:all
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:all
> bash scripts/audit/run-all-audits.sh

{
  "generated_at": "2026-06-11T22:27:16.790164+00:00",
  "report_dir": "audit/reports/2026-06-11-2226",
  "decision": "TECHNICALLY_MAINNET_READY_NO",
  "critical_high_unresolved": 0,
  "medium_unaccepted": 0,
  "tools": [
    {
      "tool": "slither",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/slither.json",
      "text": "audit/reports/2026-06-11-2226/slither.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "slither execution pending or environment-blocked"
      ]
    },
    {
      "tool": "echidna",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/echidna.json",
      "text": "audit/reports/2026-06-11-2226/echidna.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "echidna execution pending or environment-blocked"
      ]
    },
    {
      "tool": "mythril",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/mythril.json",
      "text": "audit/reports/2026-06-11-2226/mythril.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "mythril execution pending or environment-blocked"
      ]
    },
    {
      "tool": "medusa",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/medusa.json",
      "text": "audit/reports/2026-06-11-2226/medusa.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "medusa execution pending or environment-blocked"
      ]
    },
    {
      "tool": "foundry",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/foundry.json",
      "text": "audit/reports/2026-06-11-2226/foundry-test.log",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "foundry execution pending or environment-blocked"
      ]
    },
    {
      "tool": "halmos",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/halmos.json",
      "text": "audit/reports/2026-06-11-2226/halmos.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "halmos execution pending or environment-blocked"
      ]
    },
    {
      "tool": "semgrep",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/semgrep.json",
      "text": "audit/reports/2026-06-11-2226/semgrep.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "semgrep execution pending or environment-blocked"
      ]
    },
    {
      "tool": "solhint",
      "status": "COMPLETED_TEXT_ONLY",
      "json": null,
      "text": "audit/reports/2026-06-11-2226/solhint.txt",
      "blocks_technical_mainnet_readiness": false,
      "blockers": []
    },
    {
      "tool": "smtchecker",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/smtchecker.json",
      "text": "audit/reports/2026-06-11-2226/smtchecker.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "smtchecker execution pending or environment-blocked"
      ]
    },
    {
      "tool": "npm-audit",
      "status": "COMPLETED_WITH_FINDINGS_REVIEW_REQUIRED",
      "json": "audit/reports/2026-06-11-2226/npm-audit.json",
      "text": "audit/reports/2026-06-11-2226/npm-audit.txt",
      "blocks_technical_mainnet_readiness": false,
      "blockers": []
    },
    {
      "tool": "osv-scanner",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/osv-scanner.json",
      "text": "audit/reports/2026-06-11-2226/osv-scanner.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "osv-scanner execution pending or environment-blocked"
      ]
    },
    {
      "tool": "actionlint",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/actionlint.json",
      "text": "audit/reports/2026-06-11-2226/actionlint.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "actionlint execution pending or environment-blocked"
      ]
    },
    {
      "tool": "shellcheck",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/shellcheck.json",
      "text": "audit/reports/2026-06-11-2226/shellcheck.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "shellcheck execution pending or environment-blocked"
      ]
    },
    {
      "tool": "gitleaks",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/gitleaks.json",
      "text": "audit/reports/2026-06-11-2226/gitleaks.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "gitleaks execution pending or environment-blocked"
      ]
    }
  ],
  "mainnet_blockers": [
    "toolchain components pending/environment-blocked unless cleared by internal security review",
    "public Sepolia replay evidence is pending unless real Sepolia RPC/deployer evidence is supplied",
    "AGIALPHA mainnet token verification requires mainnet RPC evidence",
    "treasury/admin/founder address ceremony and founder deployment approval are not complete"
  ]
}
{
  "status": "NOT_CLEARED",
  "sha256": "8f31901285c4be3d1e057b54a97ad2074807287cf3807dc7e5d490115d3b81c0",
  "path": "audit/reports/2026-06-11-2226/toolchain-clearance-report.md"
}
{
  "status": "NO_UNRESOLVED_CRITICAL_HIGH",
  "tool": "summary",
  "critical_high_unresolved": 0
}
EXIT_STATUS=0
## npm run audit:summarize
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:summarize
> python scripts/audit/summarize-audit-results.py

{
  "generated_at": "2026-06-11T22:27:20.779659+00:00",
  "report_dir": "audit/reports/2026-06-11-2226",
  "decision": "TECHNICALLY_MAINNET_READY_NO",
  "critical_high_unresolved": 0,
  "medium_unaccepted": 0,
  "tools": [
    {
      "tool": "slither",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/slither.json",
      "text": "audit/reports/2026-06-11-2226/slither.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "slither execution pending or environment-blocked"
      ]
    },
    {
      "tool": "echidna",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/echidna.json",
      "text": "audit/reports/2026-06-11-2226/echidna.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "echidna execution pending or environment-blocked"
      ]
    },
    {
      "tool": "mythril",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/mythril.json",
      "text": "audit/reports/2026-06-11-2226/mythril.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "mythril execution pending or environment-blocked"
      ]
    },
    {
      "tool": "medusa",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/medusa.json",
      "text": "audit/reports/2026-06-11-2226/medusa.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "medusa execution pending or environment-blocked"
      ]
    },
    {
      "tool": "foundry",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/foundry.json",
      "text": "audit/reports/2026-06-11-2226/foundry-test.log",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "foundry execution pending or environment-blocked"
      ]
    },
    {
      "tool": "halmos",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/halmos.json",
      "text": "audit/reports/2026-06-11-2226/halmos.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "halmos execution pending or environment-blocked"
      ]
    },
    {
      "tool": "semgrep",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/semgrep.json",
      "text": "audit/reports/2026-06-11-2226/semgrep.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "semgrep execution pending or environment-blocked"
      ]
    },
    {
      "tool": "solhint",
      "status": "COMPLETED_TEXT_ONLY",
      "json": null,
      "text": "audit/reports/2026-06-11-2226/solhint.txt",
      "blocks_technical_mainnet_readiness": false,
      "blockers": []
    },
    {
      "tool": "smtchecker",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/smtchecker.json",
      "text": "audit/reports/2026-06-11-2226/smtchecker.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "smtchecker execution pending or environment-blocked"
      ]
    },
    {
      "tool": "npm-audit",
      "status": "COMPLETED_WITH_FINDINGS_REVIEW_REQUIRED",
      "json": "audit/reports/2026-06-11-2226/npm-audit.json",
      "text": "audit/reports/2026-06-11-2226/npm-audit.txt",
      "blocks_technical_mainnet_readiness": false,
      "blockers": []
    },
    {
      "tool": "osv-scanner",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/osv-scanner.json",
      "text": "audit/reports/2026-06-11-2226/osv-scanner.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "osv-scanner execution pending or environment-blocked"
      ]
    },
    {
      "tool": "actionlint",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/actionlint.json",
      "text": "audit/reports/2026-06-11-2226/actionlint.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "actionlint execution pending or environment-blocked"
      ]
    },
    {
      "tool": "shellcheck",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/shellcheck.json",
      "text": "audit/reports/2026-06-11-2226/shellcheck.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "shellcheck execution pending or environment-blocked"
      ]
    },
    {
      "tool": "gitleaks",
      "status": "PENDING_ENVIRONMENT_BLOCKED",
      "json": "audit/reports/2026-06-11-2226/gitleaks.json",
      "text": "audit/reports/2026-06-11-2226/gitleaks.txt",
      "blocks_technical_mainnet_readiness": true,
      "blockers": [
        "gitleaks execution pending or environment-blocked"
      ]
    }
  ],
  "mainnet_blockers": [
    "toolchain components pending/environment-blocked unless cleared by internal security review",
    "public Sepolia replay evidence is pending unless real Sepolia RPC/deployer evidence is supplied",
    "AGIALPHA mainnet token verification requires mainnet RPC evidence",
    "treasury/admin/founder address ceremony and founder deployment approval are not complete"
  ]
}
EXIT_STATUS=0
## npm run audit:fail-on-critical
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:fail-on-critical
> python scripts/audit/fail-on-critical-findings.py

{
  "status": "NO_UNRESOLVED_CRITICAL_HIGH",
  "tool": "summary",
  "critical_high_unresolved": 0
}
EXIT_STATUS=0
## npm run audit:clearance-report
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 audit:clearance-report
> python scripts/audit/generate-toolchain-clearance-report.py

{
  "status": "NOT_CLEARED",
  "sha256": "237e6532f3ea76ad41de7a9e7a049b0d019d7c95b21e1d961ec993dec0ea4bd7",
  "path": "audit/reports/2026-06-11-2226/toolchain-clearance-report.md"
}
EXIT_STATUS=0
## npm run mainnet:authorization-check:public
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> goalos-agialpha-ascension@4.3.0 mainnet:authorization-check:public
> python scripts/ethereum-mainnet-authorization-check.py --public-only

{
  "status": "NO",
  "ETHEREUM_MAINNET_AUTHORIZED": "NO",
  "commit": "62c680e40627b832f08a5fca8598c145451183eb",
  "chain": "ethereum",
  "chainId": 1,
  "agialphaToken": "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA",
  "evidence": {
    "technicalReadinessSha256": "0dc43291d5e6195a917d5efbf3d36a5d3b582f14c0528120424ddee793d44c7e",
    "deploymentAuthorizationSha256": "82ba5d31bc11319943a806d2399115ba40795ec60ca406038a8ea7e3a205f974",
    "ethereumAuthorizationEvidence": {
      "path": "qa/public-ethereum-mainnet-authorization-evidence.json",
      "sha256": null,
      "present": false,
      "status": null
    }
  },
  "blockers": [
    "PRIVATE_OPERATOR_EVIDENCE_PENDING",
    "Run --with-redacted-private-evidence to evaluate committed redacted private evidence",
    "TECHNICALLY_MAINNET_READY is not YES",
    "MAINNET_DEPLOYMENT_AUTHORIZED is not YES",
    "PRIVATE_OPERATOR_EVIDENCE_PENDING: missing qa/public-ethereum-mainnet-authorization-evidence.json"
  ],
  "reason": "PRIVATE_OPERATOR_EVIDENCE_PENDING",
  "generatedAt": "2026-06-11T22:27:28.986622+00:00",
  "generatedBy": "scripts/ethereum-mainnet-authorization-check.py",
  "finalManualDeploymentCommand": null,
  "mainnetDeploymentExecuted": false
}
EXIT_STATUS=0
