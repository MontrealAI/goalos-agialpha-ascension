# GoalOS AGIALPHA Ascension v86 Layout Hotfix QA

## Static checks completed locally

- Build script: PASS
- Static verifier: PASS
- HTML page count: 69
- Required files present: PASS
- Proof Cards 001–031 present: PASS
- No archives in repository upload root: PASS

## Browser QA correction

The previous workflow failure was caused by the QA script treating long inline SVG flow diagrams as parent escapes even when the page itself was contained. This hotfix both hardens CSS containment and updates the QA logic to check production-relevant conditions: no horizontal scroll, no nav overflow, no container viewport escape, SVG viewBox presence, image alt text, and visible clickable controls.

## Upload scope

For a minimal hotfix, upload only:

- `website/v86_actual_site/assets/goalos-v86-preserve.css`
- `scripts/visual_layout_check_v86.py`
- optional docs in `docs/`

The full package is also safe to upload.
