# Autonomous GitHub Action — GoalOS AGIALPHA Ascension v76 World Release

Final workflow path:

`.github/workflows/goalos-agialpha-ascension-autonomous-world-release.yml`

This workflow builds, verifies, deploys, and smoke-tests the public GitHub Pages website.

Normal deployment setting:

- Run manually from GitHub Actions.
- Leave `strict_repository_checks` off.

Advanced setting:

- Turn `strict_repository_checks` on only if you want long repository-wide advisory checks to block deployment if they fail or time out.

Main public release gates:

- Required pages exist.
- Required assets exist.
- No ZIP files are published into the public Pages artifact.
- Legacy Proof Card 028 quote is absent.
- New Proof Card 028 reformulation is present.
- Claim-boundary, paid-products, safety, and private-operator-data checks run when available; by default they are advisory so slow historical repository scans do not block a clean public-site deployment.
- Post-deploy smoke test checks live pages.
