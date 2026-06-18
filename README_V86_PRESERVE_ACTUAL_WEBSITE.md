# GoalOS AGIALPHA Ascension Website v86 — Preserve Actual Website Mobile Final

This release keeps the actual v76-style website and applies a mobile/responsive correction layer. It does not replace the website with the v85/v82 visual system.

## Correct architecture

The GitHub Action builds from expanded source files:

`website/v86_actual_site/`

It does **not** upload or require any repository ZIP. It does **not** copy unrelated legacy root pages into the deployed artifact.

## What it fixes

- Mobile navigation and wrapping.
- Horizontal overflow.
- Figure, image, SVG, table, canvas, and video containment.
- Footer link contrast.
- Whitepaper first-render style fallback.
- Lightweight Dynamic AI / ASI aura / RSI motion effects with reduced-motion support.
- Local-link verification.
- Claim-boundary scanning.
- Proof Card 001–031 presence.
- No public archive files in deployed `site/`.

## Web UI upload batches

Use `GoalOS_v86_PRESERVE_ACTUAL_WEB_UI_BATCHES.zip`.

Upload in order:

1. `01_AUTOMATION_AND_DOCS` to repository root.
2. `02_SITE_MAIN_HTML` to repository root.
3. `03_PROOF_CARDS_001_TO_016` to repository root.
4. `04_PROOF_CARDS_017_TO_031` to repository root.
5. `05_ASSETS_DOWNLOADS_RESOURCES_PART_A` to repository root.
6. `06_ASSETS_DOWNLOADS_RESOURCES_PART_B` to repository root.
7. Open `.github/workflows` in GitHub, then upload the two YAML files inside `07_WORKFLOWS_UPLOAD_TO_DOT_GITHUB_WORKFLOWS`.

Then run:

Actions → GoalOS AGIALPHA Ascension v86 Preserve Actual Website → Run workflow

## Important

After this deploys successfully, disable old deployment workflows that could overwrite v86.
