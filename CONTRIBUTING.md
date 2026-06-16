# Contributing

## Current contribution posture

This repository is an audit-candidate implementation. Contributions should go through pull requests and human review.

## Required contribution rules

- Do not add secrets.
- Do not add paid buyer product files.
- Do not weaken mainnet gates.
- Do not use investment/yield/price-target language.
- Do not call the system audited or mainnet-authorized unless that is supported by signed evidence.
- Do not add autonomous deployment behavior without explicit founder approval.
- Include tests for contract or script changes.
- Update docs when changing public status, gates, or deployment behavior.
- Follow `docs/DOCUMENTATION_MAINTENANCE.md` for README, runbook, generated status, public website copy, and claim-boundary documentation updates.

## Good first contribution types

```text
docs cleanup
evidence docket examples
test coverage
schema validation
static QA
public claims review
readme clarity
developer UX
```

## Documentation contributions

Documentation changes must be evidence-first and claim-bounded. Prefer existing wrapper commands from `package.json`, link durable source-of-truth files, and run the validation commands listed in `docs/DOCUMENTATION_MAINTENANCE.md` for the changed document type. Do not update Mainnet deployment or contract verification status by prose-only edits.
