#!/usr/bin/env python3
"""Fail-closed, idempotent patch for the active GoalOS v86 Pages workflow."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

EXPECTED_V86_SHA256 = "aa5695af1d7b8967149020fffd57d521e67b648eb3229dde75cec47dd3b5dca2"
PATH_START = "      # GOALOS_SME_KERNEL_V3_PUBLICATION_PATHS_START"
PATH_END = "      # GOALOS_SME_KERNEL_V3_PUBLICATION_PATHS_END"
COMPILE_START = "      # GOALOS_SME_KERNEL_V3_PUBLICATION_COMPILE_START"
COMPILE_END = "      # GOALOS_SME_KERNEL_V3_PUBLICATION_COMPILE_END"
BUILD_START = "      # GOALOS_SME_KERNEL_V3_PUBLICATION_BUILD_START"
BUILD_END = "      # GOALOS_SME_KERNEL_V3_PUBLICATION_BUILD_END"
SUMMARY_START = "            # GOALOS_SME_KERNEL_V3_PUBLICATION_SUMMARY_START"
SUMMARY_END = "            # GOALOS_SME_KERNEL_V3_PUBLICATION_SUMMARY_END"
ARTIFACT_START = "            # GOALOS_SME_KERNEL_V3_PUBLICATION_ARTIFACTS_START"
ARTIFACT_END = "            # GOALOS_SME_KERNEL_V3_PUBLICATION_ARTIFACTS_END"

PATH_BLOCK = """      # GOALOS_SME_KERNEL_V3_PUBLICATION_PATHS_START
      - 'content/sme-kernel-v3-institutional-publication.json'
      - 'website/features/sme-kernel-v3-publication/**'
      - 'scripts/website/build_sme_kernel_v3_publication.py'
      - 'scripts/website/snapshot_sme_kernel_v3_publication_site.py'
      - 'scripts/website/verify_sme_kernel_v3_publication.py'
      - 'scripts/website/visual_check_sme_kernel_v3_publication.py'
      - 'scripts/website/patch_v86_for_sme_kernel_v3_publication.py'
      - 'test/test_sme_kernel_v3_publication_website.py'
      - 'docs/SME_KERNEL_V3_INSTITUTIONAL_PUBLICATION.md'
      - 'release/kernel-v3-institutional-publication-v3.0.0-r2/RELEASE_MANIFEST.json'
      - '.github/workflows/goalos-sme-kernel-v3-institutional-publication-smoke-test.yml'
      # GOALOS_SME_KERNEL_V3_PUBLICATION_PATHS_END
"""

COMPILE_BLOCK = """      # GOALOS_SME_KERNEL_V3_PUBLICATION_COMPILE_START
      - name: Compile and parse the repository-aligned Kernel v3 institutional publication tooling
        run: |
          python3 -m py_compile \\
            scripts/website/build_sme_kernel_v3_publication.py \\
            scripts/website/snapshot_sme_kernel_v3_publication_site.py \\
            scripts/website/verify_sme_kernel_v3_publication.py \\
            scripts/website/visual_check_sme_kernel_v3_publication.py \\
            scripts/website/patch_v86_for_sme_kernel_v3_publication.py \\
            test/test_sme_kernel_v3_publication_website.py
          node --check website/features/sme-kernel-v3-publication/assets/sme-kernel-v3-publication.js
          python3 scripts/website/verify_sme_kernel_v3_publication.py --root . --source-only
      # GOALOS_SME_KERNEL_V3_PUBLICATION_COMPILE_END
"""

BUILD_BLOCK = """      # GOALOS_SME_KERNEL_V3_PUBLICATION_BUILD_START
      - name: Snapshot the generated institution before the repository-aligned publication layer
        run: python3 scripts/website/snapshot_sme_kernel_v3_publication_site.py --site site --output "$RUNNER_TEMP/sme-kernel-v3-publication-prebuild.json"

      - name: Build the Kernel v3 institutional publication layer additively
        run: SOURCE_DATE_EPOCH=1782259200 python3 scripts/website/build_sme_kernel_v3_publication.py --site site --root .

      - name: Assert the institutional publication and alignment-ledger outputs exist
        shell: bash
        run: |
          set -euo pipefail
          for file in \\
            site/sovereign-machine-economy-kernel-v3-paper.html \\
            site/sovereign-machine-economy-kernel-v3-use-cases.html \\
            site/sovereign-machine-economy-kernel-v3-publication-proof.html \\
            site/sme-kernel-v3-publication-manifest.json \\
            site/assets/sme-kernel-v3-publication.css \\
            site/assets/sme-kernel-v3-publication.js \\
            site/assets/cover-institutional-use-case-edition-v3.png \\
            site/assets/kernel-v3-figure-gallery.jpg \\
            site/assets/kernel-v3-use-case-gallery.jpg \\
            site/data/sme-kernel-v3-institutional-publication.json \\
            site/downloads/sme-kernel-v3-publication/publication-provenance.json \\
            site/downloads/sme-kernel-v3-publication/repository-alignment.json \\
            site/downloads/sme-kernel-v3-publication/kernel-v3-institutional-publication.bib \\
            site/downloads/sme-kernel-v3-publication/institutional-use-case-qualification-worksheet.md \\
            site/qa/sme-kernel-v3-publication-build.json; do
            test -s "$file" || { echo "Missing institutional publication output: $file"; find site -maxdepth 4 -type f | sort; exit 1; }
          done

      - name: Verify preservation, provenance, repository alignment, semantics, and regressions
        run: |
          python3 scripts/website/verify_sme_kernel_v3_publication.py \\
            --root . \\
            --site site \\
            --baseline "$RUNNER_TEMP/sme-kernel-v3-publication-prebuild.json" \\
            --output site/qa/sme-kernel-v3-publication-static.json
          python3 -m unittest discover -s test -p 'test_sme_kernel_v3_publication_website.py' -v

      - name: Browser-test the publication and executable Kernel at desktop, tablet, and mobile widths
        run: python3 scripts/website/visual_check_sme_kernel_v3_publication.py --site site --output site/qa/sme-kernel-v3-publication-browser

      - name: Re-verify every constitutional engine after publication reconciliation
        shell: bash
        run: |
          set -euo pipefail
          python3 scripts/website/verify_meta_agentic_alpha_agi.py --site site
          python3 scripts/website/verify_agi_alpha_node_v0.py \\
            --site site \\
            --root . \\
            --output site/qa/agi-alpha-node-v0-static-post-publication.json
          if [[ "${FIRST_REAL_LOOP_STATE:-none}" == 'complete' ]]; then
            python3 scripts/website/verify_goalos_first_real_loop.py \\
              --site site \\
              --content content/goalos-first-real-loop.json \\
              --schema schemas/goalos-first-real-loop-evidence-docket.schema.json
          fi
          python3 scripts/website/verify_agi_jobs_v0_v2.py \\
            --site site \\
            --root . \\
            --schema schemas/agi-jobs-v0-v2-evidence-docket.schema.json \\
            --output site/qa/agi-jobs-v0-v2-static-post-publication.json
          python3 scripts/website/verify_sovereign_machine_economy.py \\
            --site site \\
            --root . \\
            --content content/sovereign-machine-economy.json \\
            --schema schemas/sovereign-machine-economy-docket.schema.json \\
            --output site/qa/sovereign-machine-economy-static-post-publication.json
          python3 scripts/website/verify_sme_kernel_v3.py \\
            --site site \\
            --root . \\
            --content content/sme-kernel-v3.json \\
            --envelope-schema schemas/sme-kernel-v3-envelope.schema.json \\
            --bundle-schema schemas/sme-kernel-v3-mission-bundle.schema.json \\
            --output site/qa/sme-kernel-v3-static-post-publication.json
          python3 scripts/website/verify_sme_kernel_v3_publication.py \\
            --root . \\
            --site site \\
            --baseline "$RUNNER_TEMP/sme-kernel-v3-publication-prebuild.json" \\
            --output site/qa/sme-kernel-v3-publication-static-final.json
          find website/v86_actual_site -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum > "$RUNNER_TEMP/v86-source.after-publication"
          cmp "$RUNNER_TEMP/v86-source.before" "$RUNNER_TEMP/v86-source.after-publication"
          test "$(grep -c 'GOALOS_SME_KERNEL_V3_PUBLICATION_HOME_START' site/index.html)" -eq 1
          test "$(grep -c 'GOALOS_SME_KERNEL_V3_PUBLICATION_NAV_START' site/index.html)" -eq 1
          test "$(grep -c 'GOALOS_SME_KERNEL_V3_PUBLICATION_STYLE_START' site/index.html)" -eq 1
          for page in \\
            site/sovereign-machine-economy-kernel-v3.html \\
            site/sovereign-machine-economy-kernel-v3-protocol.html \\
            site/sovereign-machine-economy-kernel-v3-chronicle.html \\
            site/sovereign-machine-economy-kernel-v3-verifier.html \\
            site/sovereign-machine-economy-kernel-v3-sdk.html; do
            test "$(grep -c 'GOALOS_SME_KERNEL_V3_PUBLICATION_KERNEL_LINK_START' "$page")" -eq 1
          done

      - name: Assert final institutional-publication QA evidence exists
        shell: bash
        run: |
          set -euo pipefail
          for file in \\
            site/qa/sme-kernel-v3-publication-build.json \\
            site/qa/sme-kernel-v3-publication-static.json \\
            site/qa/sme-kernel-v3-publication-browser/browser-report.json \\
            site/qa/sme-kernel-v3-publication-static-final.json \\
            site/qa/agi-alpha-node-v0-static-post-publication.json \\
            site/qa/agi-jobs-v0-v2-static-post-publication.json \\
            site/qa/sovereign-machine-economy-static-post-publication.json \\
            site/qa/sme-kernel-v3-static-post-publication.json; do
            test -s "$file" || { echo "Missing final institutional-publication QA evidence: $file"; exit 1; }
          done
      # GOALOS_SME_KERNEL_V3_PUBLICATION_BUILD_END
"""

SUMMARY_BLOCK = """            # GOALOS_SME_KERNEL_V3_PUBLICATION_SUMMARY_START
            echo '- Kernel v3 Institutional Use-Case and Case-Study Edition v3.0 r2 generated with a flagship paper gateway, ten-use-case atlas, seven reference scenarios, and publication-proof ledger.'
            echo '- Publication surfaces are repository-aligned to the Autonomous End-to-End Constellation v3.2.0: six source-generated phases, 18 protected Kernel source files, the audited v86 workflow baseline, and an unchanged canonical v86 tree.'
            echo '- Canonical PDF provenance, pinned visuals, citation metadata, explicit claim boundaries, static verification, 15 browser checks, and five-manifest reconciliation passed before deployment.'
            echo '- Institutional scenarios remain illustrative and claim-bounded; no certification, production authorization, legal authority, guaranteed ROI, live settlement, user-fund authorization, or external authority is asserted.'
            # GOALOS_SME_KERNEL_V3_PUBLICATION_SUMMARY_END
"""

ARTIFACT_BLOCK = """            # GOALOS_SME_KERNEL_V3_PUBLICATION_ARTIFACTS_START
            site/sovereign-machine-economy-kernel-v3-paper.html
            site/sovereign-machine-economy-kernel-v3-use-cases.html
            site/sovereign-machine-economy-kernel-v3-publication-proof.html
            site/sme-kernel-v3-publication-manifest.json
            site/assets/sme-kernel-v3-publication.css
            site/assets/sme-kernel-v3-publication.js
            site/assets/cover-institutional-use-case-edition-v3.png
            site/assets/kernel-v3-figure-gallery.jpg
            site/assets/kernel-v3-use-case-gallery.jpg
            site/data/sme-kernel-v3-institutional-publication.json
            site/downloads/sme-kernel-v3-publication/
            site/qa/sme-kernel-v3-publication-build.json
            site/qa/sme-kernel-v3-publication-static.json
            site/qa/sme-kernel-v3-publication-browser/
            # GOALOS_SME_KERNEL_V3_PUBLICATION_ARTIFACTS_END
"""

BLOCKS = [
  (PATH_START, PATH_END, PATH_BLOCK),
  (COMPILE_START, COMPILE_END, COMPILE_BLOCK),
  (BUILD_START, BUILD_END, BUILD_BLOCK),
  (SUMMARY_START, SUMMARY_END, SUMMARY_BLOCK),
  (ARTIFACT_START, ARTIFACT_END, ARTIFACT_BLOCK),
]


def sha_text(value: str) -> str:
  return hashlib.sha256(value.encode("utf-8")).hexdigest()


def insert_once(raw: str, anchor: str, block: str, *, before: bool, label: str) -> str:
  if raw.count(anchor) != 1:
    raise RuntimeError(f"Expected exactly one {label} anchor; found {raw.count(anchor)}")
  return raw.replace(anchor, block + anchor if before else anchor + block, 1)


def existing_block(raw: str, start: str, end: str) -> str | None:
  has_start = start in raw
  has_end = end in raw
  if has_start != has_end:
    raise RuntimeError(f"Partial marker block detected: {start}")
  if not has_start:
    return None
  if raw.count(start) != 1 or raw.count(end) != 1:
    raise RuntimeError(f"Malformed marker block: {start}")
  match = re.search(re.escape(start) + r".*?" + re.escape(end) + r"\n?", raw, re.S)
  if not match:
    raise RuntimeError(f"Unable to read marker block: {start}")
  return match.group(0)


def main() -> int:
  root = Path(__file__).resolve().parents[2]
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--workflow", type=Path, default=root / ".github/workflows/goalos-agialpha-ascension-v86-final.yml")
  parser.add_argument("--require-sha256", default=EXPECTED_V86_SHA256, help="Expected SHA-256 for the unpatched active workflow")
  parser.add_argument("--check", action="store_true", help="Validate exact patchability or exact installed blocks without writing")
  args = parser.parse_args()
  workflow = args.workflow.resolve()
  if not workflow.is_file():
    raise SystemExit(f"Active v86 workflow missing: {workflow}")
  raw = workflow.read_text(encoding="utf-8")
  observed_blocks = [existing_block(raw, start, end) for start, end, _ in BLOCKS]
  if any(item is not None for item in observed_blocks):
    if not all(item is not None for item in observed_blocks):
      raise RuntimeError("Partial institutional-publication workflow patch detected; refusing a mixed state")
    mismatches = [start for (start, _, expected), observed in zip(BLOCKS, observed_blocks) if observed != expected]
    if mismatches:
      raise RuntimeError(f"Installed publication workflow blocks drifted: {', '.join(mismatches)}")
    print(f"PASS: workflow contains the exact repository-aligned publication patch ({sha_text(raw)})")
    return 0
  observed_sha = sha_text(raw)
  if observed_sha != args.require_sha256:
    raise RuntimeError(f"Workflow SHA-256 drifted: expected {args.require_sha256}, observed {observed_sha}. Re-audit the latest workflow before patching.")
  patched = raw
  patched = insert_once(patched, "      - '.github/workflows/goalos-agialpha-ascension-v86-final.yml'\n", PATH_BLOCK, before=True, label="path-filter")
  patched = insert_once(patched, "      - name: Parse required constitutional-civilization runtimes under Node.js\n", COMPILE_BLOCK, before=True, label="compile")
  patched = insert_once(patched, "      - name: Reject archives and private operator material in public site\n", BUILD_BLOCK, before=True, label="post-Kernel build")
  patched = insert_once(patched, "            echo '- Kernel v3 remains browser-local and fail-closed: external authority NONE_GRANTED; external actions, network calls, wallet activity, token movements, live model calls, and automatic memory promotion remain zero or disabled.'\n", SUMMARY_BLOCK, before=False, label="executive summary")
  patched = insert_once(patched, "            site/assets/first-real-loop/\n", ARTIFACT_BLOCK, before=True, label="preview artifact")
  for start, end, expected in BLOCKS:
    if existing_block(patched, start, end) != expected:
      raise RuntimeError(f"Patch contract failed: {start}")
  if args.check:
    print(f"PASS: audited workflow is patchable; proposed SHA-256 {sha_text(patched)}")
    return 0
  workflow.write_text(patched, encoding="utf-8")
  print(f"PASS: patched {workflow}; SHA-256 {sha_text(patched)}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
