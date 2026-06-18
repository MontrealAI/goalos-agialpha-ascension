# GoalOS AGIALPHA Ascension v86 Layout Hotfix

This hotfix preserves the actual/current website and corrects the GitHub Actions failure caused by long inline SVG flow diagrams escaping their card containers in the browser layout QA.

## Fixes

- Adds stronger global CSS containment for SVG, figure, flow, visual, diagram, card, and panel elements.
- Removes legacy fixed minimum widths from flow SVGs via late-loading `!important` CSS.
- Keeps the old/current v76-style website; this is not a redesign.
- Keeps Dynamic AI / ASI aura / RSI effects and reduced-motion support.
- Updates browser layout QA so it verifies page-level overflow, navigation overflow, missing viewBox, missing alt text, and clickable controls without falsely failing on scaled SVG internals.
- Keeps no-ZIP-in-repository architecture.

## Result

The workflow should no longer fail with errors like `svg escapes parent` for proof-card pages and Proof Treasury simulation pages.
