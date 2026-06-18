#!/usr/bin/env python3
"""Build the GoalOS AGIALPHA Ascension Website v76 World Release static Pages artifact.

This builder is intentionally conservative: it publishes only public website files,
public assets, and linked resource/download directories. It does not publish the
repository internals, workflows, scripts, contracts, caches, private operator data,
node_modules, or ZIP archives.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Iterable

RELEASE = "GoalOS AGIALPHA Ascension Website v76 — World Release Autonomous Command"
VERSION = "v76-world-release"
PUBLIC_DIRS = ["assets", "downloads", "resources"]
ROOT_PUBLIC_NAMES = {
    ".nojekyll",
    "robots.txt",
    "sitemap.xml",
    "manifest.webmanifest",
    "site-status.json",
    "routes.json",
    "QA_REPORT.json",
    "QA_REPORT_v76.json",
}
ROOT_PUBLIC_SUFFIXES = {".html", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico"}
BLOCKED_DIR_PARTS = {
    ".git",
    ".github",
    ".private",
    "private",
    "node_modules",
    "cache",
    "artifacts",
    "typechain",
    "typechain-types",
    "contracts",
    "ignition",
    "test",
    "tests",
    "scripts",
    "LOCAL_BUILD_CHECK",
}
BLOCKED_SUFFIXES = {
    ".zip",
    ".env",
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".keystore",
    ".wallet",
    ".sqlite",
    ".db",
    ".log",
}
TEXT_SUFFIXES = {".html", ".js", ".css", ".json", ".xml", ".txt", ".md", ".csv", ".webmanifest", ".svg"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def blocked(path: Path) -> bool:
    parts = set(path.parts)
    if parts & BLOCKED_DIR_PARTS:
        return True
    if path.suffix.lower() in BLOCKED_SUFFIXES:
        return True
    if path.name.startswith(".") and path.name != ".nojekyll":
        return True
    return False


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_public_dir(root: Path, out: Path, rel_dir: str, copied: list[str]) -> None:
    src_dir = root / rel_dir
    if not src_dir.exists():
        return
    for src in src_dir.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(root)
        if blocked(rel):
            continue
        copy_file(src, out / rel)
        copied.append(str(rel).replace("\\", "/"))


def copy_root_public_files(root: Path, out: Path, copied: list[str]) -> None:
    for src in root.iterdir():
        if not src.is_file():
            continue
        if src.name in ROOT_PUBLIC_NAMES or src.suffix.lower() in ROOT_PUBLIC_SUFFIXES:
            if blocked(Path(src.name)):
                continue
            copy_file(src, out / src.name)
            copied.append(src.name)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def html_pages(out: Path) -> list[str]:
    return sorted(str(p.relative_to(out)).replace("\\", "/") for p in out.rglob("*.html"))


def write_qa(out: Path, copied: list[str]) -> None:
    qa_dir = out / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    pages = html_pages(out)
    manifest = {
        "release": RELEASE,
        "version": VERSION,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "page_count": len(pages),
        "pages": pages,
        "copied_file_count": len(copied),
        "copied_files_sha256": {
            rel: sha256_file(out / rel)
            for rel in copied
            if (out / rel).is_file() and (out / rel).suffix.lower() in TEXT_SUFFIXES
        },
        "public_boundary": {
            "zip_files_allowed": False,
            "private_operator_data_allowed": False,
            "external_claims_without_repository_evidence_allowed": False,
        },
    }
    (qa_dir / "QA_ASCENSION_WEBSITE_v76_WORLD_RELEASE.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    md = [
        f"# {RELEASE} QA",
        "",
        f"Generated: `{manifest['generated_at_utc']}`",
        "",
        f"- HTML pages: {len(pages)}",
        f"- Public files copied: {len(copied)}",
        "- ZIP files: disallowed",
        "- Private operator data: disallowed",
        "- Deployment mode: static GitHub Pages artifact",
        "",
        "## Pages",
    ]
    md.extend(f"- `{page}`" for page in pages)
    (qa_dir / "QA_ASCENSION_WEBSITE_v76_WORLD_RELEASE.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site", help="Output directory for GitHub Pages artifact")
    args = parser.parse_args()

    root = repo_root()
    out = (root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()
    if out == root or root in out.parents and out.name in {".", ""}:
        raise SystemExit("Refusing to build into repository root")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    copied: list[str] = []
    copy_root_public_files(root, out, copied)
    for rel_dir in PUBLIC_DIRS:
        copy_public_dir(root, out, rel_dir, copied)

    (out / ".nojekyll").write_text("", encoding="utf-8")
    if ".nojekyll" not in copied:
        copied.append(".nojekyll")

    if not (out / "index.html").exists():
        raise SystemExit("index.html was not copied into the public site artifact")

    write_qa(out, sorted(set(copied)))
    print(f"Built {RELEASE} into {out}")
    print(f"Copied {len(set(copied))} public files; {len(html_pages(out))} HTML pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
