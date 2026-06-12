#!/usr/bin/env python3
from pathlib import Path
import argparse, re, textwrap, subprocess, sys, os, shutil


def extract_inline_builder(workflow_path: Path) -> str:
    text = workflow_path.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"python3\s+-\s+<<'PY'\n(.*?)\n\s*PY", text, flags=re.S)
    if not matches:
        raise RuntimeError("Could not find inline Python website builder in autonomous-github-pages.yml")
    # Use the longest heredoc; that is the premium website builder.
    code = max(matches, key=len)
    return textwrap.dedent(code)


def fallback_site(site: Path):
    site.mkdir(parents=True, exist_ok=True)
    index = site / "index.html"
    if not index.exists():
        index.write_text("""<!doctype html><html><head><meta charset='utf-8'><title>GoalOS AGIALPHA Ascension</title></head><body><main><h1>GoalOS AGIALPHA Ascension</h1><p>Fallback preview site generated for usage example smoke testing.</p></main></body></html>""", encoding="utf-8")
    (site / ".nojekyll").write_text("", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    workflow = Path(".github/workflows/autonomous-github-pages.yml")
    try:
        code = extract_inline_builder(workflow)
        temp = Path(".goalos_usage_example_extracted_builder.py")
        temp.write_text(code, encoding="utf-8")
        subprocess.run([sys.executable, str(temp)], check=True)
        if site != Path("site") and Path("site").exists():
            if site.exists(): shutil.rmtree(site)
            shutil.copytree("site", site)
    except Exception as exc:
        print(f"WARNING: existing site builder extraction failed: {exc}")
        fallback_site(site)
    subprocess.run([sys.executable, "scripts/add_goalos_agialpha_usage_example_to_site.py", "--site", str(site)], check=True)
    print("Usage example preview built at", site)

if __name__ == "__main__":
    main()
