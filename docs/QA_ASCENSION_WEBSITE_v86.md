# GoalOS v86 QA — Preserve Actual Website Mobile Final

v86 is a preservation release for the actual GoalOS AGIALPHA Ascension website. It keeps the v76-style website and adds a correction layer for mobile friendliness, overflow safety, link integrity, claim boundaries, and Dynamic AI effects.

## Local validation performed

- Build script: PASS
- Static verifier: PASS
- Broken-link scan: PASS
- Proof Card 001–031 presence: PASS
- No archive files in generated `site/`: PASS

## Browser QA

The package includes a Playwright/Chromium layout QA script and the GitHub Actions workflow installs Playwright Chromium before deployment. The local sandbox Chromium binary was not usable in headless mode, so the browser QA is designed to run in GitHub Actions as part of the autonomous deployment.

## Checks enforced by the workflow

- All required files exist.
- Every HTML page includes the v86 CSS patch and Dynamic AI script.
- Every local link resolves.
- No repository ZIP is required.
- No ZIP/7z/tar/gz/rar file is emitted into the public site.
- Proof Cards 001–031 exist.
- Claim-boundary scanner rejects unbounded AGI/ASI/superintelligence, ROI, token appreciation, or Mainnet settlement claims.
- Browser QA checks mobile/tablet/desktop viewports for horizontal scrolling and figure overflow.
