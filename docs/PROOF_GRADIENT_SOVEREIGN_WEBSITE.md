# The Proof Gradient — Sovereign Website Integration

This integration adds one flagship page and one homepage feature panel to the generated GoalOS website.

## Public positioning

**Where autonomous work earns the right to become capability.**

The page is entirely GoalOS-native. It names no competitor or outside autoresearch company. It presents Public Proof Mission 001, the proof constitution, the complete acceptance chain, conditional AGIALPHA settlement, Mission 002 reuse, and the 48-contract Ethereum Mainnet substrate.

## Preservation model

The canonical directory `website/v86_actual_site/` is never edited. The existing v86 builder runs first. The additive builder then operates only on the transient `site/` directory.

Existing generated pages are preserved. The overlay adds:

- `proof-gradient-challenge.html`
- one marked homepage feature panel
- three public data downloads
- QA records and screenshots

The workflow refuses deployment if the Mainnet address map, verification total, postcheck, claim boundary, competitor-reference prohibition, local links, or responsive layout checks fail.

## Evidence boundary

The Ethereum Mainnet record contains 48 GoalOS-created contracts, all 48 recorded as source-verified, zero verification failures, 14 configured grants, and a passing 48-contract postcheck. The page states that this is infrastructure evidence, not external audit completion or autonomous scientific performance.

## Unified GitHub Pages architecture

The Sovereign page is integrated into the repository's single canonical GitHub Pages pipeline alongside the Ethereum Mainnet deployment record.

The unified build order is:

1. copy the byte-preserved `website/v86_actual_site/` source into the transient `site/` artifact;
2. validate the canonical Mainnet registry and Sovereign public-data snapshot against one another;
3. generate `ethereum-mainnet.html` and its homepage feature;
4. generate `proof-gradient-challenge.html` and its homepage feature;
5. verify cross-page navigation, public claims, contract totals, downloads, responsive layout, button contrast, and control sizing;
6. upload one Pages artifact and perform one Pages deployment.

There is intentionally no second Proof Gradient Pages deployment workflow. One deployment owner prevents one generated site from overwriting another.

The two generated experiences are cross-linked:

- the Ethereum Mainnet page links to the Proof Gradient;
- the Proof Gradient page links to the Ethereum Mainnet record;
- the homepage presents both additive, independently marked feature panels.

## Automated visual quality gates

Deployment fails closed when a required browser check detects:

- horizontal overflow;
- collapsed or uncentered content;
- missing page or edition markers;
- missing contract totals or public-data downloads;
- controls below 44 CSS pixels;
- Mainnet call-to-action contrast below 4.5:1;
- broken Mainnet/Proof Gradient cross-links;
- unexpected forms, wallet surfaces, archives, or private operator material.

The browser checks use self-contained inline assets for deterministic Mainnet rendering and do not require a wallet, RPC endpoint, API key, or public-network transaction.
