# Baseline Command Log

Generated: 2026-06-11T18:02:53Z

## npm ci
```text
npm warn deprecated inflight@1.0.6: This module is not supported, and leaks memory. Do not use it. Check out lru-cache if you want a good and tested way to coalesce async requests by a key value, which is much more comprehensive and powerful.
npm warn deprecated lodash.isequal@4.5.0: This package is deprecated. Use require('node:util').isDeepStrictEqual instead.
npm warn deprecated glob@8.1.0: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated glob@7.2.3: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated glob@5.0.15: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated glob@7.2.3: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated glob@7.1.7: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
npm warn deprecated uuid@8.3.2: uuid@10 and below is no longer supported.  For ESM codebases, update to uuid@latest.  For CommonJS codebases, use uuid@11 (but be aware this version will likely be deprecated in 2028).

added 597 packages, and audited 598 packages in 8s

44 vulnerabilities (18 low, 22 moderate, 4 high)

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
RESULT: PASS
```

## npm ls hardhat @nomicfoundation/hardhat-toolbox @nomicfoundation/hardhat-chai-matchers @openzeppelin/contracts typescript
```text
goalos-agialpha-ascension@4.3.0 /workspace/goalos-agialpha-ascension
├─┬ @nomicfoundation/hardhat-toolbox@5.0.0
│ ├─┬ @nomicfoundation/hardhat-chai-matchers@2.1.2
│ │ └── hardhat@2.28.6 deduped
│ ├─┬ @nomicfoundation/hardhat-ethers@3.1.3
│ │ └── hardhat@2.28.6 deduped
│ ├─┬ @nomicfoundation/hardhat-ignition-ethers@0.15.17
│ │ ├─┬ @nomicfoundation/hardhat-ignition@0.15.16
│ │ │ └── hardhat@2.28.6 deduped
│ │ └── hardhat@2.28.6 deduped
│ ├─┬ @nomicfoundation/hardhat-network-helpers@1.1.2
│ │ └── hardhat@2.28.6 deduped
│ ├─┬ @nomicfoundation/hardhat-verify@2.1.3
│ │ └── hardhat@2.28.6 deduped
│ ├─┬ @typechain/ethers-v6@0.5.1
│ │ ├─┬ ts-essentials@7.0.3
│ │ │ └── typescript@5.9.3 deduped
│ │ └── typescript@5.9.3 deduped
│ ├─┬ @typechain/hardhat@9.1.0
│ │ └── hardhat@2.28.6 deduped
│ ├─┬ hardhat-gas-reporter@1.0.10
│ │ └── hardhat@2.28.6 deduped
│ ├── hardhat@2.28.6 deduped
│ ├─┬ solidity-coverage@0.8.17
│ │ └── hardhat@2.28.6 deduped
│ ├─┬ typechain@8.3.2
│ │ └── typescript@5.9.3 deduped
│ └── typescript@5.9.3 deduped
├── @openzeppelin/contracts@4.9.6
├─┬ hardhat@2.28.6
│ └── typescript@5.9.3 deduped
├─┬ ts-node@10.9.2
│ └── typescript@5.9.3 deduped
└── typescript@5.9.3

RESULT: PASS
```

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

## npm run assert:public-status
```text

> goalos-agialpha-ascension@4.3.0 assert:public-status
> python scripts/assert_public_status.py

Public status assertion passed: Ethereum Mainnet is not authorized, public claims are bounded, and external-audit closure is not an active required gate.
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
    ✔ runs Aim -> Act -> Prove -> Evolve on-chain commitments (975ms)

  GoalOS AGIALPHA Ascension flow
    ✔ creates a Proof Seed using AGIALPHA (166ms)
    ✔ runs post -> claim -> submit -> review -> proof card -> credential -> reputation with AGIALPHA (137ms)
    ✔ anchors a legacy AGIJobManager record as reviewed history (98ms)

  GoalOS AGIALPHA Ascension v4 institutional controls
    ✔ records conformance, claim boundary, replay, chronicle and falsification records (85ms)
    ✔ supports commit-reveal validation (91ms)
    ✔ supports evaluator staking, slashing court, and reward vault (80ms)

  v4.3 Ethereum launch gate consistency
    ✔ uses Ethereum Sepolia and complete institutional gates


  8 passing (2s)

RESULT: PASS
```

## npm run test:all
```text

> goalos-agialpha-ascension@4.3.0 test:all
> hardhat test test/agialphaAscensionFlow.test.ts test/aepAscensionFlow.test.ts test/v4InstitutionalControls.test.ts test/v4_3EthereumGateConsistency.test.ts



  GoalOS AGIALPHA Ascension flow
    ✔ creates a Proof Seed using AGIALPHA (956ms)
    ✔ runs post -> claim -> submit -> review -> proof card -> credential -> reputation with AGIALPHA (146ms)
    ✔ anchors a legacy AGIJobManager record as reviewed history (106ms)

  AEP-001 / AGIALPHA Ascension proof-of-evolution spine
    ✔ runs Aim -> Act -> Prove -> Evolve on-chain commitments (174ms)

  GoalOS AGIALPHA Ascension v4 institutional controls
    ✔ records conformance, claim boundary, replay, chronicle and falsification records (93ms)
    ✔ supports commit-reveal validation (86ms)
    ✔ supports evaluator staking, slashing court, and reward vault (80ms)

  v4.3 Ethereum launch gate consistency
    ✔ uses Ethereum Sepolia and complete institutional gates


  8 passing (2s)

RESULT: PASS
```

## npm run static-check
```text

> goalos-agialpha-ascension@4.3.0 static-check
> python scripts/static_check.py

Static QA passed.
Files checked: 863
RESULT: PASS
```

## npm run readiness:v4.3
```text

> goalos-agialpha-ascension@4.3.0 readiness:v4.3
> python scripts/verify-readiness-v4-3.py

{
  "package": "GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_3_GATE_CLEAN_EVIDENCE_READY",
  "generated_at": "2026-06-11T18:03:34.149694+00:00",
  "static_readiness": "passed",
  "files_checked": 863,
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
  "sha256": "4264a4726ef0f9bc8983aa513bb3ba40ae1a1cc106e4aec3642da11804d1fd2d"
}
RESULT: PASS
```

