# Upload guide — GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨

This release is prepared for installation through the GitHub website. You do not need Terminal, a code editor, a wallet, an API key, or a local development setup.

## What it adds

- `/agi-alpha-node-v0.html` — the interactive sovereign proof-node command deck.
- `/agi-alpha-node-v0-architecture.html` — the constitutional architecture and lineage dossier.
- `/index.html#agi-alpha-node-v0` — one additive gateway on the existing homepage.
- A deterministic eight-state work-unit simulation with eight peers, seven validators, five guardian domains, fourteen sealed artifacts, preserved dissent, and local evidence downloads.
- Automated build, static verification, regression testing, Chromium QA, artifact packaging, and GitHub Pages deployment.

## What it does not change

It does not replace the current website. It does not modify `website/v86_actual_site/**`, contracts, deployments, Mainnet evidence, Proof Missions, package manifests, lockfiles, or existing feature source. The two website workflow files are the only existing files that may be updated.

## GitHub Web UI installation

1. Create a branch named `feature/agi-alpha-node-v0` from `main`.
2. At the repository root, choose **Add file → Upload files**.
3. Upload the **contents** of the package folder `01_UPLOAD_TO_REPOSITORY_ROOT`—not the numbered parent folder itself.
4. Commit with:

   ```text
   Add GoalOS AGIALPHA Ascension AGI Alpha Node v0
   ```

5. Open `.github/workflows` on the same branch.
6. Choose **Add file → Upload files** and upload the two files from `02_UPLOAD_TO_DOT_GITHUB_WORKFLOWS`.
7. Commit with:

   ```text
   Integrate AGI Alpha Node v0 into autonomous Pages build
   ```

8. Open a pull request titled:

   ```text
   GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨
   ```

9. Wait for **GoalOS AGIALPHA Ascension v86 Smoke Test** to pass.
10. In **Files changed**, confirm there are eleven additive source/documentation files, at most two modified workflow files, and no deletions.
11. Merge to `main`.
12. In **Actions**, open **GoalOS AGIALPHA Ascension v86 Preserve Actual Website** and wait for the Pages deployment to become green.

## Live acceptance check

After deployment, open:

```text
https://montrealai.github.io/goalos-agialpha-ascension/agi-alpha-node-v0.html
https://montrealai.github.io/goalos-agialpha-ascension/agi-alpha-node-v0-architecture.html
```

On the flagship page:

1. Keep the Enterprise proof-node preset.
2. Select **Ascension** posture.
3. Click **Run the proof node**.
4. Confirm all eight states complete and the terminal state is `HUMAN_REVIEW_REQUIRED`.
5. Confirm a peer route, Alpha Work Unit receipt, validator quorum, one visible dissent, four guardian review signatures, and `14 / 14 sealed` artifacts appear.
6. Download **Evidence Docket** and **Review brief**.
7. Confirm the authority cards read `NOT_CERTIFIED`, `NOT_ACTIVATED`, `NO`, and `0` external actions.

## Safe rollback

Open the merged pull request and select **Revert**, then merge the generated revert pull request. Do not delete generated files directly from the GitHub Pages output; the autonomous action recreates the website from source.

For the illustrated, click-by-click version, use the package’s `00_START_HERE/OPEN_ME_FIRST.html` and `00_START_HERE/START_HERE_GITHUB_WEB_UI.md`.
