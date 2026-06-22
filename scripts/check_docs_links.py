#!/usr/bin/env python3
"""Validate repository Markdown links without turning archives into current docs.

Current documentation should fail closed on missing repository-relative links.
Historical paper/image references are reported as warnings because those files are
provenance records and are not used as current operator guidance.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections.abc import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^) #]+)")
WARNING_PREFIXES = (
    "docs/archive/",
    "docs/papers/",
)
DEFAULT_SCAN_PATHS = ("*.md", "docs/**/*.md")


def iter_markdown(root: pathlib.Path, patterns: Iterable[str]) -> Iterable[pathlib.Path]:
    seen: set[pathlib.Path] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def is_warning_only(path: pathlib.Path, root: pathlib.Path) -> bool:
    rel = path.relative_to(root).as_posix()
    return rel.startswith(WARNING_PREFIXES)


def collect_link_results(root: pathlib.Path, patterns: Iterable[str]) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    for path in iter_markdown(root, patterns):
        text = path.read_text(errors="ignore")
        for match in LINK_RE.finditer(text):
            target_raw = match.group(1)
            target = (path.parent / target_raw).resolve()
            if target.exists():
                continue
            message = f"{path.relative_to(root)} -> {target_raw}"
            if is_warning_only(path, root):
                warnings.append(message)
            else:
                failures.append(message)
    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check internal Markdown links.")
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=ROOT,
        help="Repository root to scan (defaults to this checkout).",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        help="Glob pattern to scan relative to root; may be supplied more than once.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    patterns = tuple(args.patterns or DEFAULT_SCAN_PATHS)
    failures, warnings = collect_link_results(root, patterns)

    if warnings:
        print("warning: unresolved historical/provenance links:")
        print("\n".join(warnings[:50]))
        if len(warnings) > 50:
            print(f"... {len(warnings) - 50} additional warning(s) omitted")

    if failures:
        print("error: unresolved current documentation links:")
        print("\n".join(failures[:50]))
        if len(failures) > 50:
            print(f"... {len(failures) - 50} additional error(s) omitted")
        return 1

    print("documentation links syntax/internal paths ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
