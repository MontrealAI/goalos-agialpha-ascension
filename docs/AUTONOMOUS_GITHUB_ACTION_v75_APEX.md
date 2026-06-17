# Autonomous GitHub Action — v75 Apex

This package includes the autonomous GitHub Pages build/deploy pair that was missing from the first v75 Apex package.

## Files added to `PATCH_TO_REPOSITORY_ROOT`

- `.github/workflows/autonomous-ascension-website-v75.yml`
- `.github/workflows/ascension-website-v75-smoke-test.yml`
- `scripts/build_goalos_agialpha_ascension_website_v75_apex.py`
- `scripts/verify_goalos_agialpha_ascension_website_v75_apex.py`
- `downloads/**`
- `resources/**`

## Principle

The action follows the same public-site principle used in the previous packages:

1. checkout repository
2. configure GitHub Pages
3. build a clean static artifact into `site/`
4. verify required pages, links, assets, claim boundary, and no ZIP files
5. upload QA reports
6. deploy with `actions/deploy-pages`

The builder publishes only public website files plus public assets/resources/downloads. It does not publish workflows, scripts, repository internals, contracts, caches, `node_modules`, private operator directories, or ZIP archives.

## Manual run

After applying the patch to the repository root:

```bash
python3 scripts/build_goalos_agialpha_ascension_website_v75_apex.py --out site
python3 scripts/verify_goalos_agialpha_ascension_website_v75_apex.py --site site
```

## GitHub run

Open GitHub → Actions → `Autonomous Ascension Website v75 Apex` → Run workflow.

The smoke-test workflow runs on pull requests touching website pages, assets, resources, downloads, the builder, verifier, or workflow files.
