# Upload guide — GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨

This release is designed for the **GitHub web interface**. No terminal or local development environment is required.

## What you upload

Upload the release package’s `01_UPLOAD_TO_REPOSITORY_ROOT` contents to the repository root. Then upload the two prepared workflow files from `02_UPLOAD_TO_DOT_GITHUB_WORKFLOWS` into `.github/workflows`.

Do **not** upload the ZIP itself and do **not** upload the `00_START_HERE` or `03_PREVIEW_AND_QA` folders into the repository.

## What changes

The upload adds the Node’s content, templates, local assets, build scripts, verifier, browser QA, tests, and documentation. It replaces only these two existing automation files:

- `.github/workflows/goalos-agialpha-ascension-v86-final.yml`
- `.github/workflows/goalos-agialpha-ascension-v86-smoke-test.yml`

No file under `website/v86_actual_site/**` is replaced. No contract, deployment record, Proof Mission, package manifest, lockfile, or prior feature source is removed or edited.

## What GitHub does automatically

On the pull request, the smoke workflow builds the complete existing website, generates all prior public features in order, detects any complete META-Agentic installation, snapshots the result, adds the Sovereign Citadel, verifies preservation, runs twelve regression tests, executes Chromium interaction and adversarial QA, and uploads a preview artifact.

After merge to `main`, the production workflow repeats those gates and deploys the complete `site` artifact to GitHub Pages.

## Safe review checklist

Before merging, confirm:

- the smoke workflow is green;
- there are no unexplained deleted files;
- the change list contains the new Node source files and at most the two workflow modifications;
- the generated preview contains `agi-alpha-node-v0.html`, `agi-alpha-node-v0-architecture.html`, and `agi-alpha-node-v0-proof-ledger.html`;
- the final boundary reads `HUMAN_REVIEW_REQUIRED` or `SAFE_HOLD`;
- no wallet, RPC secret, API key, or private operator material appears in the change.

See `docs/AGI_ALPHA_NODE_V0_WEBSITE.md` for the architecture, security model, source lineage, and exact build contract.
