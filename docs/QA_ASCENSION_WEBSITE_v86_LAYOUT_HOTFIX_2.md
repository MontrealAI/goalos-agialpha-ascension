# GoalOS v86 Layout Hotfix 2 QA

This hotfix preserves the actual/current website and corrects the GitHub Actions browser-layout QA failures caused by overly strict checks on decorative and clipped SVG internals.

## What changed

- Preserves the actual v76/v86 visual website.
- Keeps the same autonomous v86 deployment workflow name.
- Replaces the browser QA script with a visible-scroll based layout check.
- Serves the generated site over localhost during QA instead of relying on file URLs.
- Treats decorative clipped SVG internals as allowed when they do not create user-visible horizontal scrolling.
- Keeps hard failures for real problems: user-scrollable horizontal overflow, navigation overflow, missing alt text, too few clickable controls, missing Dynamic AI signal.
- Strengthens the v86 CSS containment rules for cards, panels, figures, SVGs, visual modules, and mobile/tablet layouts.

## Expected result

The workflow step `Run browser layout and mobile QA` should pass on the preserved actual website instead of failing on `svg escapes parent` and `[class*=visual] viewport escape` false positives.
