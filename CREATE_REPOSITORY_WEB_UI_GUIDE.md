# Create the GitHub Repository Through the Web UI

## Step 1 — Create repository

```text
Owner: MontrealAI
Repository name: goalos-agialpha-ascension
Description: GoalOS-native reimplementation of α‑AGI Ascension using AGIALPHA for proof-settled AI workflow work.
Visibility: Private first
Add README: no
Add .gitignore: no
License: no
```

## Step 2 — Upload Batch 01

```text
WEB_UI_UPLOAD_BATCHES/BATCH_01_ROOT_GITHUB_METADATA__SELECT_CONTENTS_AND_UPLOAD
```

Commit message:

```text
Initialize root files, GitHub metadata, schemas, audit, and QA
```

## Step 3 — Upload Batch 02

```text
WEB_UI_UPLOAD_BATCHES/BATCH_02_DOCS__SELECT_CONTENTS_AND_UPLOAD
```

Commit message:

```text
Add GoalOS AGIALPHA Ascension docs
```

## Step 4 — Upload Batch 03

```text
WEB_UI_UPLOAD_BATCHES/BATCH_03_CONTRACTS_SCHEMAS_AUDIT__SELECT_CONTENTS_AND_UPLOAD
```

Commit message:

```text
Add contracts, schemas, audit handoff, and QA artifacts
```

## Step 5 — Upload Batch 04

```text
WEB_UI_UPLOAD_BATCHES/BATCH_04_SCRIPTS_TESTS_APP__SELECT_CONTENTS_AND_UPLOAD
```

Commit message:

```text
Add scripts, tests, app shell, and deployment helpers
```

Select the contents of each batch folder, not the folder itself.

## Step 6 — Add topics

Use `GITHUB_REPOSITORY_SETTINGS.md`.

## Step 7 — Enable protections

```text
Security and analysis
Actions restrictions
Rulesets / branch protection
Least-privilege collaborators
```

## Step 8 — Create first issues

Use `docs/FIRST_10_GITHUB_ISSUES.md`.

## Step 9 — First CODEX handoff

Use `docs/CODEX_PRODUCTION_HANDOFF_PROMPT.md`.

## Do not upload

```text
.env
private keys
seed phrases
RPC secrets
API keys
buyer products
private Evidence Dockets
customer data
legal memos
tax memos
unredacted audit findings
```
