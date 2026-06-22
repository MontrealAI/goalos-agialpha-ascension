#!/usr/bin/env python3
from pathlib import Path
import argparse, json, shutil, sys


def inline_local_assets(site: Path, rel: str) -> str:
    raw = (site / rel).read_text(encoding="utf-8")
    css = (site / "assets/goalos-v86-preserve.css").read_text(encoding="utf-8")
    js = (site / "assets/goalos-v86-dynamic-ai.js").read_text(encoding="utf-8")
    raw = raw.replace('<link rel="stylesheet" href="assets/goalos-v86-preserve.css">', f"<style>{css}</style>")
    raw = raw.replace('<script src="assets/goalos-v86-dynamic-ai.js" defer></script>', f"<script>{js}</script>")
    raw = raw.replace('<script defer src="assets/goalos-v86-dynamic-ai.js"></script>', f"<script>{js}</script>")
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    ap.add_argument("--screenshots", action="store_true")
    args = ap.parse_args()
    site = Path(args.site).resolve()
    qa = site / "qa" / "proof-gradient-sovereign"
    qa.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f"ERROR: Playwright missing: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    shots: list[str] = []
    with sync_playwright() as p:
        executable = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        browser = p.chromium.launch(headless=True, executable_path=executable) if executable else p.chromium.launch(headless=True)
        feature_html = inline_local_assets(site, "proof-gradient-challenge.html")

        for name, width, height in [("desktop", 1440, 1100), ("mobile", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.emulate_media(reduced_motion="reduce")
            page.set_content(feature_html, wait_until="load")
            if "Proof Gradient" not in page.title():
                errors.append(f"{name}: wrong page title")
            if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
                errors.append(f"{name}: horizontal overflow")
            if page.locator(".pgs-contract").count() != 48:
                errors.append(f"{name}: expected 48 contract cards")
            if page.locator("text=Where autonomous work earns the right to become capability.").count() < 1:
                errors.append(f"{name}: hero copy missing")
            page.locator("#pgs-search").fill("Chronicle")
            visible = page.locator(".pgs-contract:not([hidden])").count()
            if visible != 1:
                errors.append(f"{name}: contract search expected 1 result, found {visible}")
            if args.screenshots:
                target = qa / f"proof-gradient-{name}.png"
                page.screenshot(path=str(target), full_page=True)
                shots.append(str(target.relative_to(site)))
            page.close()

        home = browser.new_page(viewport={"width": 1440, "height": 1000})
        home.set_content(inline_local_assets(site, "index.html"), wait_until="load")
        if home.locator(".pgs-home").count() != 1:
            errors.append("homepage: feature panel count is not one")
        if args.screenshots:
            target = qa / "proof-gradient-homepage-panel.png"
            home.locator(".pgs-home").screenshot(path=str(target))
            shots.append(str(target.relative_to(site)))
        home.close()
        browser.close()

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "screenshots": shots,
        "viewports": ["1440x1100", "390x844"],
        "publicNetworkTransactionSent": False,
    }
    (qa / "visual-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
