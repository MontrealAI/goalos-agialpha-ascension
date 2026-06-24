# Upload Guide — GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨

**Edition:** Sovereign Labor Civilization v3  
**Status:** ready for GitHub Web UI installation; not yet deployed.

This package is prepared for the GitHub website. No terminal, local Git installation, or coding is required.

## What this release adds

Five generated public surfaces:

- `agi-jobs-v0-v2.html` — Sovereign Labor Exchange and fourteen-gate proof flight.
- `agi-jobs-v0-v2-market.html` — Institutional Market Atlas and Pareto Coalition Foundry.
- `agi-jobs-v0-v2-settlement.html` — Proof Settlement Chamber and twenty-four-artifact Evidence Docket.
- `agi-jobs-v0-v2-memory.html` — reversible Capability Memory Gate.
- `agi-jobs-v0-v2-architecture.html` — constitutional architecture and thirty-two-fingerprint source lineage.

It also adds an idempotent homepage gateway at `index.html#agi-jobs-v0-v2`, an **AGI Jobs** top-navigation link, routes and sitemap entries, a pull-request smoke workflow, and a narrowly extended production Pages workflow.

## Before uploading

1. Download and extract the delivery ZIP on your computer.
2. Do **not** upload the ZIP itself.
3. In `MontrealAI/goalos-agialpha-ascension`, create a branch from `main` named:

   `feature/goalos-agi-jobs-v0-v2-civilization`

4. Keep all extracted folder paths intact.
5. Do not delete, rename, or move an existing repository file.

## Upload group 1 — repository root

1. Open the repository’s **Code** tab while the new branch is selected.
2. Choose **Add file → Upload files**.
3. On your computer, open `01_UPLOAD_TO_REPOSITORY_ROOT`.
4. Drag the **contents** of that folder into GitHub—not the enclosing folder itself.
5. Confirm GitHub preserves these paths: `content`, `docs`, `schemas`, `scripts`, `test`, `website`, and `README_UPLOAD_AGI_JOBS_V0_V2.md`.
6. Commit with:

   `Add AGI Jobs v0 (v2) Sovereign Labor Civilization`

This group contains sixteen AGI Jobs feature files. It does not contain generated website output.

## Upload group 2 — GitHub workflows

1. On the same branch, open `.github/workflows`.
2. Choose **Add file → Upload files**.
3. Upload both files from `02_UPLOAD_TO_DOT_GITHUB_WORKFLOWS`:
   - `goalos-agi-jobs-v0-v2-smoke-test.yml`
   - `goalos-agialpha-ascension-v86-final.yml`
4. Replacing `goalos-agialpha-ascension-v86-final.yml` is expected and necessary to add AGI Jobs to the autonomous Pages artifact.
5. Do not replace any other workflow.
6. Commit with:

   `Wire Sovereign Labor Civilization into autonomous Pages deployment`

## Expected GitHub change summary

For a **first AGI Jobs installation**, expect:

- **17 new files** — sixteen feature files plus one smoke workflow;
- **1 modified existing file** — the production Pages workflow;
- **0 deleted files**.

For an **upgrade from the earlier Sovereign Work Exchange package**, expect:

- **1 new file** — the Capability Memory page template;
- **17 modified files** — the prior AGI Jobs feature set and both workflows;
- **0 deleted files**.

The GitHub interface may group folder uploads differently, but the final **Files changed** tab must show no unexplained file and no deletion.

## Open the pull request

Use this title:

`GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨ — Sovereign Labor Civilization`

Copy the prepared description from `04_PULL_REQUEST/PULL_REQUEST_TEXT.md`.

Wait for:

`GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) Smoke Test`

to complete successfully. Do not merge while the check is red or still running.

## Merge and deploy

After the smoke test is green and the **Files changed** tab shows no unexplained deletion, merge into `main`.

The production workflow named:

`GoalOS AGIALPHA Ascension v86 Preserve Actual Website`

will start automatically. Wait for both jobs to become green:

1. `Build, preserve, verify, and browser-test v86`
2. `Deploy v86 to GitHub Pages`

After deployment, open:

`https://montrealai.github.io/goalos-agialpha-ascension/index.html#agi-jobs-v0-v2`

Use a hard refresh if your browser still shows the previous Pages artifact.

## Safety boundary

The release must never show a wallet prompt, token transfer, RPC request, production action, autonomous settlement, or autonomous capability promotion.

```text
Normal completion        HUMAN_SETTLEMENT_REVIEW
Budget/quorum review     HUMAN_REVIEW_REQUIRED
Severe incident          SAFE_HOLD
External authority       NONE_GRANTED
Wallet connections       0
Runtime network requests 0
Live token movements     0
External actions         0
Production activation    NOT_ACTIVATED
User-fund authorization  NO
```

## Recovery

When a workflow fails, open the red step and copy the first error block. Do not rerun a historical failed run after applying a fix; historical runs remain pinned to their old commit. Use the new commit’s run or manually start the workflow from `main`.
