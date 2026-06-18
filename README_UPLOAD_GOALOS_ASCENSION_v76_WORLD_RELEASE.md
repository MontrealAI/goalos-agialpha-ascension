# GoalOS AGIALPHA Ascension — v76 World Release: Web UI Deployment Guide

This package contains everything needed to publish the final static website through GitHub Pages using an autonomous GitHub Action.

You do not need the command line.

## What to upload

Upload the **contents** of this folder into your GitHub repository:

`PATCH_TO_REPOSITORY_ROOT/`

Important: open `PATCH_TO_REPOSITORY_ROOT`, select everything inside it, and upload those files/folders to the repository root. Do **not** upload the folder itself as a nested folder.

## Simple deployment steps

1. Download and unzip this package.
2. Open the unzipped folder.
3. Open `PATCH_TO_REPOSITORY_ROOT`.
4. Go to your GitHub repository in your browser.
5. Click **Add file**.
6. Click **Upload files**.
7. Drag everything inside `PATCH_TO_REPOSITORY_ROOT` into the GitHub upload page.
8. Scroll down to **Commit changes**.
9. Use this commit message:

   `Deploy GoalOS AGIALPHA Ascension v76 World Release`

10. Choose **Commit directly to the main branch** if GitHub allows it.
11. Click **Commit changes**.
12. Go to **Settings** → **Pages**.
13. Under **Build and deployment**, set **Source** to **GitHub Actions**.
14. Go to the **Actions** tab.
15. Click **GoalOS AGIALPHA Ascension — Autonomous World Release**.
16. Click **Run workflow**.
17. Leave **strict_repository_checks** turned **off** for normal deployment.
18. Click the green **Run workflow** button.
19. Wait for the workflow to finish with green check marks.
20. Open the published website URL shown in the deployment summary or in **Settings** → **Pages**.

## Optional cleanup of older workflows

If your repository already has older v75 workflow files, the final action can still deploy the site, but you may see duplicate Actions runs. To keep the repository clean, delete these older workflow files if they exist:

- `.github/workflows/autonomous-ascension-website-v75.yml`
- `.github/workflows/ascension-website-v75-smoke-test.yml`

Keep this final workflow:

- `.github/workflows/goalos-agialpha-ascension-autonomous-world-release.yml`

## What the autonomous action does

The action automatically:

1. checks out the repository,
2. configures GitHub Pages,
3. builds a clean public `site/` folder,
4. verifies required pages and assets,
5. blocks ZIP files from the public artifact,
6. blocks the old Proof Card 028 quote,
7. verifies the new Proof Card 028 reformulation,
8. runs available claim-boundary and public repository checks as advisory checks unless strict mode is turned on,
9. uploads QA artifacts,
10. deploys the website to GitHub Pages,
11. smoke-tests the published pages.

## Proof Card 028 replacement

The legacy phrase was replaced with:

> “The civilizational prize is not ownership of a mythical machine. It is verified capability that compounds: evidence-backed missions, reviewer-cleared upgrades, reusable memory, and governed productive capacity.”

This is more native to GoalOS because it frames value as proof-governed capability compounding, not ownership of a speculative machine.

## Troubleshooting

If the workflow fails:

1. Open the failed workflow run.
2. Click the red failed job.
3. Open the failed step.
4. Read the message shown there.

Most likely fixes:

- If Pages is not configured: go to **Settings** → **Pages** and set **Source** to **GitHub Actions**.
- If upload failed: upload the contents of `PATCH_TO_REPOSITORY_ROOT`, not the folder itself.
- If an old quote is detected: make sure `proof-card-028.html` came from this v76 package.
- If an older workflow ran instead: run the final workflow named **GoalOS AGIALPHA Ascension — Autonomous World Release**.

## Final release boundary

This package is a public-alpha website release. It does not claim achieved AGI, achieved ASI, achieved superintelligence, token appreciation, investment return, external audit completion, legal/tax approval, production certification, or Ethereum Mainnet deployment unless explicitly evidenced by repository source-of-truth files.
