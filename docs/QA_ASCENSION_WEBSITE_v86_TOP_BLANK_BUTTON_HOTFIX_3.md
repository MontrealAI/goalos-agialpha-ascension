# GoalOS v86 Top Blank + Button Contrast Hotfix 3 QA

Purpose: preserve the current live website while fixing two user-visible regressions:

1. the homepage could render a blank particle/aura screen above the actual content;
2. some footer/navigation buttons could render pale text on white pills.

Fixes:
- pins `.asi-bg`, `.asi-canvas`, and `.v86-ai-canvas` as fixed non-flow background layers;
- prevents dynamic AI canvases from pushing the homepage content below the fold;
- forces the homepage hero title and action area to remain visible;
- sets high-contrast button/link colors in footers and dark sections;
- extends browser QA to catch a hidden homepage H1, non-fixed AI canvases, and white-on-white footer links.

This hotfix does not redesign the site, does not upload ZIP files into the repo, and does not replace the current website style.
