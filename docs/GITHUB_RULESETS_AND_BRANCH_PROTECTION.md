# GitHub Rulesets and Branch Protection

## Recommended `main` ruleset

```text
Require a pull request before merging
Require approvals
Require review from Code Owners
Require status checks to pass
Require conversation resolution
Block force pushes
Block deletions
Require signed commits if available and practical
Restrict bypass to repository owner / emergency maintainer only
```

## Required status checks

```text
Repository safety check
Repository status check
Production continuation readiness check
Static QA
v4.3 readiness
```

## Sensitive paths

```text
contracts/**
scripts/**
schemas/**
.github/**
.env.example
package.json
docs/SAFE_CLAIMS.md
docs/MAINNET_NOT_AUTHORIZED_DECISION_v4_3.md
docs/PRODUCTION_CONTINUATION_PLAN.md
```
