#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, json, time, os, sys

def copytree_clean(src: Path, out: Path):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for item in src.iterdir():
        # never copy upload archives or hidden build cache
        if item.suffix.lower() in {".zip", ".7z", ".tar", ".gz"}:
            continue
        dest = out / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns("*.zip","*.7z","*.tar","*.gz","__pycache__",".DS_Store"))
        else:
            shutil.copy2(item, dest)

def main():
    ap = argparse.ArgumentParser(description="Build GoalOS AGIALPHA Ascension v86 preserved actual website")
    ap.add_argument("--out", default="site")
    args = ap.parse_args()
    repo = Path.cwd()
    src = repo / "website" / "v86_actual_site"
    if not src.exists():
        print(f"ERROR: missing canonical source directory: {src}", file=sys.stderr)
        return 2
    out = repo / args.out
    copytree_clean(src, out)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    htmls = sorted(p.name for p in out.glob("*.html"))
    status = {
        "release": "v86-preserve-actual-site-mobile-final",
        "mode": "expanded-canonical-source-no-repo-zip",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "html_pages": len(htmls),
        "source": "website/v86_actual_site",
        "mobile_patch": "assets/goalos-v86-preserve.css",
        "dynamic_ai": "assets/goalos-v86-dynamic-ai.js",
        "no_repo_zip": True
    }
    (out / "site-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    # Ensure robots/sitemap if source lacks them.
    if not (out / "robots.txt").exists():
        (out / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: sitemap.xml\n", encoding="utf-8")
    if not (out / "sitemap.xml").exists():
        urls = "\n".join(f"<url><loc>https://montrealai.github.io/goalos-agialpha-ascension/{name}</loc></url>" for name in htmls)
        (out / "sitemap.xml").write_text(f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>{urls}</urlset>", encoding="utf-8")
    print(json.dumps(status, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
