# Baseline Command Log

Generated: 2026-06-11T17:45:25Z

## npm run repo:all
```text

> goalos-agialpha-ascension@4.3.0 repo:all
> python scripts/repository_safety_check.py && python scripts/repository_status_check.py && python scripts/repository_production_readiness_check.py && python scripts/no_paid_products_check.py

Repository safety check passed.
Repository status check passed.
{
  "status": "passed",
  "errors": [],
  "warnings": [],
  "message": "Repository is production-continuation ready as a GitHub starter candidate."
}
Paid/private product check passed.
RESULT: PASS
```

## npm run repo:no-paid-products
```text

> goalos-agialpha-ascension@4.3.0 repo:no-paid-products
> python scripts/no_paid_products_check.py

Paid/private product check passed.
RESULT: PASS
```

## npm run compile
```text

> goalos-agialpha-ascension@4.3.0 compile
> hardhat compile

Nothing to compile
No need to generate any newer typings.
RESULT: PASS
```

## npm test
```text

> goalos-agialpha-ascension@4.3.0 test
> hardhat test



  AEP-001 / AGIALPHA Ascension proof-of-evolution spine
    ✔ runs Aim -> Act -> Prove -> Evolve on-chain commitments (1418ms)

  GoalOS AGIALPHA Ascension flow
    ✔ creates a Proof Seed using AGIALPHA (253ms)
    ✔ runs post -> claim -> submit -> review -> proof card -> credential -> reputation with AGIALPHA (229ms)
    ✔ anchors a legacy AGIJobManager record as reviewed history (173ms)

  GoalOS AGIALPHA Ascension v4 institutional controls
    ✔ records conformance, claim boundary, replay, chronicle and falsification records (142ms)
    ✔ supports commit-reveal validation (142ms)
    ✔ supports evaluator staking, slashing court, and reward vault (157ms)

  v4.3 Ethereum launch gate consistency
    ✔ uses Ethereum Sepolia and complete institutional gates (67ms)


  8 passing (3s)

RESULT: PASS
```

## npm run test:all
```text

> goalos-agialpha-ascension@4.3.0 test:all
> hardhat test test/agialphaAscensionFlow.test.ts test/aepAscensionFlow.test.ts test/v4InstitutionalControls.test.ts test/v4_3EthereumGateConsistency.test.ts



  GoalOS AGIALPHA Ascension flow
    ✔ creates a Proof Seed using AGIALPHA (1502ms)
    ✔ runs post -> claim -> submit -> review -> proof card -> credential -> reputation with AGIALPHA (249ms)
    ✔ anchors a legacy AGIJobManager record as reviewed history (210ms)

  AEP-001 / AGIALPHA Ascension proof-of-evolution spine
    ✔ runs Aim -> Act -> Prove -> Evolve on-chain commitments (322ms)

  GoalOS AGIALPHA Ascension v4 institutional controls
    ✔ records conformance, claim boundary, replay, chronicle and falsification records (160ms)
    ✔ supports commit-reveal validation (153ms)
    ✔ supports evaluator staking, slashing court, and reward vault (181ms)

  v4.3 Ethereum launch gate consistency
    ✔ uses Ethereum Sepolia and complete institutional gates (81ms)


  8 passing (3s)

RESULT: PASS
```

## npm run static-check
```text

> goalos-agialpha-ascension@4.3.0 static-check
> python scripts/static_check.py

Static QA passed.
Files checked: 829
RESULT: PASS
```

## npm run readiness:v4.3
```text

> goalos-agialpha-ascension@4.3.0 readiness:v4.3
> python scripts/verify-readiness-v4-3.py

{
  "package": "GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY",
  "generated_at": "2026-06-11T17:46:07.737976+00:00",
  "static_readiness": "passed",
  "files_checked": 829,
  "errors": [],
  "warnings": [],
  "status": "gate-clean evidence-ready audit candidate; mainnet not authorized",
  "score_current_state": "9.6/10 audit-candidate package; not 10/10 until executed evidence and internal security review exist",
  "next_gate": "real Ethereum Sepolia rehearsal and filled Evidence Docket"
}
RESULT: PASS
```

## npm run evidence:docket:template
```text

> goalos-agialpha-ascension@4.3.0 evidence:docket:template
> python scripts/generate-evidence-docket-template.py

{
  "status": "EVIDENCE_DOCKET_TEMPLATE_WRITTEN",
  "path": "evidence/SEPOLIA_EVIDENCE_DOCKET_TEMPLATE_v4_2.json",
  "sha256": "e9c687179b03069190845e456fa206fbe843ff5e0b90e2faaa837e1caaa25f65"
}
RESULT: PASS
```

## npm run assert:public-status
```text

> goalos-agialpha-ascension@4.3.0 assert:public-status
> python scripts/assert_public_status.py

Public status assertion passed: Ethereum Mainnet is not authorized, public claims are bounded, and external-audit closure is not an active required gate.
RESULT: PASS
```

## python scripts/mainnet-authorization-check.py
```text
{
  "generated_at": "2026-06-11T17:46:16.689214+00:00",
  "MAINNET_DEPLOYMENT_AUTHORIZED": "NO",
  "decision": "NOT_AUTHORIZED",
  "blockers": [
    "MAINNET_TARGET must equal ethereum",
    "ALLOW_MAINNET_DEPLOYMENT must equal YES_ALL_GATES_APPROVED only after all real gates are complete and founder approval is explicit",
    "LEGAL_SIGNOFF_HASH missing or not bytes32",
    "TAX_SIGNOFF_HASH missing or not bytes32",
    "SECURITY_REVIEW_HASH missing or not bytes32",
    "PUBLIC_CLAIMS_REVIEW_HASH missing or not bytes32",
    "TREASURY_REVIEW_HASH missing or not bytes32",
    "AGIALPHA_TOKEN_VERIFICATION_HASH missing or not bytes32",
    "SEPOLIA_REHEARSAL_EVIDENCE_HASH missing or not bytes32",
    "AUTOMATED_SECURITY_TOOLCHAIN_HASH missing or not bytes32",
    "INTERNAL_SECURITY_REVIEW_HASH missing or not bytes32",
    "FOUNDER_APPROVAL_HASH missing or not bytes32",
    "AGIALPHA_TOKEN_ADDRESS missing or not EVM address",
    "FOUNDER_ADDRESS missing or not EVM address",
    "TREASURY_ADDRESS missing or not EVM address",
    "COMMERCIALIZATION_PERFORMANCE_ADMIN missing or not EVM address",
    "PROOF_REWARDS_ADMIN missing or not EVM address",
    "LIQUIDITY_ADMIN missing or not EVM address",
    "SECURITY_ADMIN missing or not EVM address",
    "COMMUNITY_ADMIN missing or not EVM address",
    "AGIALPHA_TOKEN_ADDRESS must be the existing Ethereum mainnet AGIALPHA token",
    "TECHNICALLY_MAINNET_READY is not YES",
    "technical: slither is pending/environment-blocked or not internally accepted",
    "technical: echidna is pending/environment-blocked or not internally accepted",
    "technical: mythril is pending/environment-blocked or not internally accepted",
    "technical: medusa is pending/environment-blocked or not internally accepted",
    "technical: foundry is pending/environment-blocked or not internally accepted",
    "technical: halmos is pending/environment-blocked or not internally accepted",
    "technical: semgrep is pending/environment-blocked or not internally accepted",
    "technical: smtchecker is pending/environment-blocked or not internally accepted",
    "technical: osv-scanner is pending/environment-blocked or not internally accepted",
    "technical: actionlint is pending/environment-blocked or not internally accepted",
    "technical: shellcheck is pending/environment-blocked or not internally accepted",
    "technical: gitleaks is pending/environment-blocked or not internally accepted",
    "technical: Public Ethereum Sepolia replay remains pending; only local chainId 11155111 rehearsal evidence is present",
    "technical: AGIALPHA token verification requires Ethereum mainnet RPC evidence",
    "technical: Treasury/founder address ceremony is not complete"
  ],
  "agialpha_mainnet_token_required": "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA",
  "deploy_command_if_authorized": null,
  "final_founder_confirmation_required": true,
  "mainnet_deployment_executed": false
}
RESULT: PASS
```

