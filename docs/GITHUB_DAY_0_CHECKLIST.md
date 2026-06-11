# GitHub Day-0 Checklist

## Before upload

- [ ] Repository name is `goalos-agialpha-ascension`.
- [ ] Visibility is private.
- [ ] GitHub-generated README is disabled.
- [ ] GitHub-generated `.gitignore` is disabled.
- [ ] GitHub-generated license is disabled.

## Upload

- [ ] Upload Batch 01.
- [ ] Upload Batch 02.
- [ ] Upload Batch 03.
- [ ] Upload Batch 04.
- [ ] Confirm `README.md` renders.
- [ ] Confirm `.github/workflows/agialpha-audit-candidate-ci.yml` exists.
- [ ] Confirm no old `goalos-jobs-production-rc-ci.yml` workflow exists.

## Security settings

- [ ] Enable Dependabot alerts.
- [ ] Enable secret scanning / push protection where available.
- [ ] Restrict GitHub Actions as appropriate.
- [ ] Create branch ruleset for `main`.
- [ ] Require PR review before merge.
- [ ] Require CODEOWNER review for sensitive paths.
- [ ] Require status checks.

## First issues

- [ ] Run Ethereum Sepolia rehearsal and fill Evidence Docket.
- [ ] Run compile/tests and publish engineering evidence.
- [ ] Prepare external audit closure package.
- [ ] Public claims review before public repository visibility.
