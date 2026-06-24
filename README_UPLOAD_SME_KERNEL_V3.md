# Upload GoalOS Sovereign Machine Economy Kernel v3 with GitHub Web UI

## Before you begin

Create a new branch from `main`. Do not upload the release ZIP itself. Upload only the files contained in the package's two upload folders.

## Repository-root upload

At the repository root, select **Add file → Upload files** and upload the contents of `01_UPLOAD_TO_REPOSITORY_ROOT`.

This adds the Kernel content contract, two JSON Schemas, five templates, five browser assets, four Python build/verification tools, one deterministic test suite, and documentation.

## Workflow upload

Open `.github/workflows`, select **Add file → Upload files**, and upload both files from `02_UPLOAD_TO_DOT_GITHUB_WORKFLOWS`.

- `goalos-sme-kernel-v3-smoke-test.yml` is new.
- `goalos-agialpha-ascension-v86-final.yml` replaces the existing production website workflow.

No other existing file should be replaced.

## Pull request review

The expected first-install diff is:

- 21 new files;
- 1 modified production workflow;
- 0 deletions.

Merge only after **GoalOS Sovereign Machine Economy Kernel v3 Smoke Test** is green. After merge, wait for both production jobs:

1. **Build, preserve, verify, and browser-test v86**
2. **Deploy v86 to GitHub Pages**

Then hard-refresh the public website and open `index.html#sme-kernel-v3`.

## Fail-closed check

Stop and review the upload if GitHub shows an unexpected deletion, a modification outside the production workflow, or a partial Kernel source set.
