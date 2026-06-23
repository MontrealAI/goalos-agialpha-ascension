# START HERE — GitHub Web UI installation

## GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨

This package is designed for a non-technical installation through GitHub’s website. No Terminal, code editor, API key, wallet, or local development environment is required.

The release adds one flagship Institution Foundry, one architecture dossier, and one homepage gateway. It does not replace the existing website. The canonical v86 source, Proof Missions, Ethereum Mainnet record, contracts, deployments, package manifests, and unrelated files remain untouched.

## What the live release adds

```text
/meta-agentic-alpha-agi.html
/meta-agentic-alpha-agi-architecture.html
/index.html#meta-agentic-alpha-agi
```

Inside the Institution Foundry, a visitor can compose a mission, evolve 12/24/36 deterministic candidate institutions, inspect four generations and the Pareto frontier, compare rejected lineages, inspect the selected six-layer constitution, pass eight proof gates, and export an Evidence Docket v2 plus an Executive Brief.

The final state is always a hard human boundary: `HUMAN_REVIEW_READY`. The public experience performs no model call, source retrieval, wallet connection, transaction, settlement, message, or external action.

## The package has five folders

```text
00_START_HERE
01_UPLOAD_TO_REPOSITORY_ROOT
02_UPLOAD_TO_DOT_GITHUB_WORKFLOWS
03_PREVIEW_AND_QA
04_AUDIT
```

Upload only folders **01** and **02** as described below. Folders **03** and **04** are review material and do not belong in the repository.

## Step 1 — create a safe branch

1. Open `MontrealAI/goalos-agialpha-ascension` on GitHub.
2. Click the branch selector above the file list; it currently shows `main`.
3. Type `meta-agentic-alpha-agi-ascension`.
4. Click **Create branch: meta-agentic-alpha-agi-ascension from main**.
5. Confirm the selector now shows the new branch.

Nothing live changes until this branch is merged.

## Step 2 — upload the additive source

1. Remain at the repository root on `meta-agentic-alpha-agi-ascension`.
2. Click **Add file** → **Upload files**.
3. On your computer, open `01_UPLOAD_TO_REPOSITORY_ROOT`.
4. Drag the six entries *inside* that folder into GitHub—not the numbered parent folder.
5. Confirm GitHub shows these repository-root paths:

```text
content/
website/
scripts/
test/
docs/
README_UPLOAD_META_AGENTIC_ALPHA_AGI.md
```

6. Enter this commit message:

```text
Add GoalOS META-Agentic alpha AGI Institution Foundry
```

7. Click **Commit changes** to the current branch.

This batch contains eleven files. Existing files outside the listed paths must not appear as deleted or modified.

## Step 3 — install the autonomous action integration

1. In the same branch, open `.github`, then `workflows`.
2. Click **Add file** → **Upload files**.
3. Open `02_UPLOAD_TO_DOT_GITHUB_WORKFLOWS` on your computer.
4. Drag in:

```text
goalos-agialpha-ascension-v86-final.yml
goalos-agialpha-ascension-v86-smoke-test.yml
```

5. Confirm the filenames exactly match the existing workflows.
6. Enter this commit message:

```text
Wire META-Agentic release into autonomous Pages build
```

7. Commit to the current branch.

These are the only existing files that may need replacement. They preserve the complete prior workflow and add the feature path triggers, additive build, static verifier, regression suite, browser QA, artifact packaging, and Pages deployment. When GitHub reports “no changes,” the repository already contains the required action integration; continue to the next step.

## Step 4 — open the pull request

1. Return to the repository’s main page.
2. Click **Compare & pull request** for the new branch.
3. Use this exact title:

```text
GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨
```

4. Create the pull request.
5. Open **Checks** and wait for **GoalOS AGIALPHA Ascension v86 Smoke Test** to become green.
6. Open **Files changed** and confirm:
   - the eleven additive source/documentation files are present;
   - at most the two named workflow files are modified;
   - no file is deleted;
   - `website/v86_actual_site/**`, contracts, deployments, package files, and lockfiles are unchanged.
7. Click **Merge pull request** → **Confirm merge**.

## Step 5 — watch the autonomous production build

1. Open the repository’s **Actions** tab.
2. Select **GoalOS AGIALPHA Ascension v86 Preserve Actual Website**.
3. Open the run triggered by the merge.
4. Confirm the META-Agentic stages pass:

```text
Build GoalOS AGIALPHA Ascension META-AGENTIC α-AGI additively
Assert META-Agentic α-AGI generated outputs exist
Verify, regression-test, and browser-test META-Agentic α-AGI
```

5. Confirm **Deploy v86 to GitHub Pages** is green.

The action rebuilds the complete website from controlled source, adds the new feature only after all prior site builders finish, verifies hashes and non-claims, tests preservation/idempotence, runs Chromium QA at desktop/tablet/mobile sizes, rejects private material, publishes the complete Pages artifact, and deploys it.

## Step 6 — verify the live experience

Open:

```text
https://montrealai.github.io/goalos-agialpha-ascension/meta-agentic-alpha-agi.html
https://montrealai.github.io/goalos-agialpha-ascension/meta-agentic-alpha-agi-architecture.html
```

Then perform this acceptance check:

1. Keep the flagship mission or enter your own.
2. Select **Ascension** posture and **24 institutions**.
3. Click **Evolve the institution**.
4. Confirm the run displays 24 candidates, a non-empty Pareto frontier, one selected institution, a six-layer constitution, and `8 / 8` proof gates.
5. Click several candidate/lineage nodes and verify the inspector changes.
6. Download **Evidence Docket** and **Executive Brief**.
7. Confirm the terminal display says **HUMAN REVIEW READY** and **HUMAN REVIEW REQUIRED**.

## Manual deployment only when necessary

A merge to `main` normally triggers production automatically. For a manual rerun:

1. Open **Actions**.
2. Select **GoalOS AGIALPHA Ascension v86 Preserve Actual Website**.
3. Click **Run workflow**.
4. Select `main`, then click the green **Run workflow** button.

## One-time GitHub Pages setting

When GitHub says Pages is not configured:

1. Open **Settings** → **Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Return to **Actions** and rerun the production workflow.

Do not select **Deploy from a branch**. This repository publishes the generated `site/` artifact through its autonomous workflow.

## Safe rollback

Open the merged pull request and click **Revert**. Merge the generated revert pull request. Do not manually delete files from the live Pages site; every deployment recreates generated output.

## Release acceptance standard

A successful release has all of the following:

- the original website and existing routes still load;
- exactly one META-Agentic homepage gateway is present;
- both new routes work on desktop and mobile;
- the flagship run is deterministic and reaches `HUMAN_REVIEW_READY`;
- both review records download;
- no account, key, wallet, external request, transaction, or action is requested;
- the production and smoke workflows are green.

The prepared release candidate passed 56/56 static checks, 9/9 regression tests, and 46/46 Chromium interaction/visual checks before packaging.
