# GoalOS Sovereign Machine Economy Kernel v3 — Institutional Publication Layer r2

**Release:** `GOALOS-AGIALPHA-SME-KERNEL-V3-INSTITUTIONAL-PUBLICATION-V3.0-R2`  
**Repository baseline:** `076a7a7a8d1713d4849e95e1c58b8b6ccec0df03`  
**Executable interface:** Autonomous End-to-End Constellation v3.2.0  
**Mode:** additive, deterministic, repository-aligned, preservation-first  
**Canonical publication:** [Institutional Use-Case and Case-Study Edition v3.0](https://montrealai.github.io/GoalOS-AGIALPHA-Sovereign-Machine-Economy-Kernel-v3-Paper-Institutional-Use-Case-Edition-v3.0/00_START_HERE.html)

> A model can answer. An agent can act. An institution must prove.

## Public surfaces

| Route | Purpose |
|---|---|
| `/sovereign-machine-economy-kernel-v3-paper.html` | Flagship gateway, source-generated six-stage constellation, architecture, materials, reader paths, provenance, and claim boundary |
| `/sovereign-machine-economy-kernel-v3-use-cases.html` | Ten institutional operating patterns and seven worked reference case studies |
| `/sovereign-machine-economy-kernel-v3-publication-proof.html` | Publication validation, canonical PDF checksums, repository-alignment ledger, citation, and explicit non-claims |

The generated homepage receives one marked stylesheet link, one navigation link, and one institutional-edition gateway after the existing Kernel v3 surface. Each of the five executable Kernel pages receives one marked **Institutional Paper** link; the flagship Kernel receives an additional paper CTA. Nothing under `website/v86_actual_site/**` is edited.

## Exact repository alignment

The r2 source gate fails closed unless all of the following remain true:

- `content/sme-kernel-v3.json` matches its audited SHA-256 and exposes exactly six phases: `IDENTIFY → OUT-LEARN → OUT-THINK → OUT-DESIGN → OUT-STRATEGISE → OUT-EXECUTE`.
- The executable contract retains 17 constitutional states, 10 typed envelopes, and 5 signing authorities.
- Eighteen protected Kernel source, schema, template, runtime, verifier, and test files match one recorded source-set digest.
- The active v86 workflow either matches its audited pre-integration SHA-256 or contains the exact complete r2 marker blocks.
- The canonical `website/v86_actual_site/**` tree matches its audited digest.

The generated site emits `downloads/sme-kernel-v3-publication/repository-alignment.json` so reviewers can inspect the observed commit, protected files, source digests, interface contract, and preservation boundary.

## Source architecture

- `content/sme-kernel-v3-institutional-publication.json` — editorial, lineage, provenance, claim-boundary, and alignment contract.
- `website/features/sme-kernel-v3-publication/templates/base.html` — semantic shell, canonical metadata, Open Graph metadata, and ScholarlyArticle JSON-LD.
- `website/features/sme-kernel-v3-publication/assets/` — dedicated visual system, progressive enhancement, and three SHA-pinned publication visuals.
- `scripts/website/build_sme_kernel_v3_publication.py` — post-Kernel additive builder and five-manifest reconciler.
- `scripts/website/verify_sme_kernel_v3_publication.py` — source, alignment, semantic, reference, provenance, preservation, manifest, and public-artifact verifier.
- `scripts/website/visual_check_sme_kernel_v3_publication.py` — 15 browser checks across desktop, tablet, and mobile.
- `scripts/website/patch_v86_for_sme_kernel_v3_publication.py` — exact-hash, idempotent, marker-verified workflow patcher.
- `release/kernel-v3-institutional-publication-v3.0.0-r2/RELEASE_MANIFEST.json` — checksums for every versioned integration source file plus audited workflow and repository-alignment evidence.

## Preservation law

1. Snapshot the complete generated site after Kernel v3.
2. Verify the current repository alignment before changing generated output.
3. Generate three new pages, dedicated assets, versioned data, citation and qualification downloads, PDF provenance, and a repository-alignment ledger.
4. Add marked blocks to the generated homepage and marked links to the five generated Kernel pages.
5. Extend `routes.json`, `sitemap.xml`, and `site-status.json`.
6. Reconcile final hashes through the META-Agentic → AGI Alpha Node → AGI Jobs → Sovereign Machine Economy → Kernel v3 manifest chain.
7. Reject every removed pre-existing file and every undeclared pre-existing change.
8. Re-run predecessor verifiers, Kernel verification, publication verification, unit tests, browser QA, archive rejection, secret rejection, and v86 tree comparison before deployment.

The only pre-existing generated files permitted to change are `index.html`, `routes.json`, `sitemap.xml`, `site-status.json`, the five executable Kernel pages, and the five constitutional companion manifests.

## Provenance and security policy

The three principal PDFs remain on the canonical versioned publication host. The main site records their canonical URLs, byte sizes, and SHA-256 digests instead of duplicating large binaries. The one-time installer independently downloads and verifies those PDFs and the three selected visuals in temporary runner storage; only the three verified visuals enter the pull request.

Production builds perform no web scraping and fetch no mutable remote content. The smoke-test workflow uses full-length action commit pins and read-only repository permissions. The installer is repository- and branch-bound, checks the exact audited workflow and protected source sets, opens a draft pull request, and removes its own bootstrap workflow from the proposed change.

## Claim boundary

This layer presents a theoretical systems and protocol architecture, a browser-local executable reference implementation, and a falsifiable evaluation program. Institutional use cases and case studies are illustrative reference scenarios.

It does not assert achieved AGI or ASI, empirical state of the art, independent certification, legal authority, regulatory approval, guaranteed ROI, production authorization, live settlement, user-fund authorization, autonomous sovereignty, energy abundance, or civilization-scale capability.

## Local verification

```bash
python3 scripts/website/verify_sme_kernel_v3_publication.py --root . --source-only
python3 -m unittest discover -s test -p 'test_sme_kernel_v3_publication_website.py' -v
python3 scripts/website/patch_v86_for_sme_kernel_v3_publication.py --check
```

The live site remains unchanged until the generated draft pull request is reviewed, marked ready, passes the complete Pages workflow, and is merged.
