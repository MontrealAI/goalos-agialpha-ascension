#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

VIEWPORTS = (("desktop", 1440, 1100), ("mobile", 390, 844))
MIN_CONTROL_HEIGHT = 44


def inline_local_assets(site: Path, rel: str) -> str:
    raw = (site / rel).read_text(encoding="utf-8")
    css = (site / "assets/goalos-v86-preserve.css").read_text(encoding="utf-8")
    js = (site / "assets/goalos-v86-dynamic-ai.js").read_text(encoding="utf-8")
    raw = raw.replace('<link rel="stylesheet" href="assets/goalos-v86-preserve.css">', f"<style>{css}</style>")
    raw = raw.replace('<script src="assets/goalos-v86-dynamic-ai.js" defer></script>', f"<script>{js}</script>")
    raw = raw.replace('<script defer src="assets/goalos-v86-dynamic-ai.js"></script>', f"<script>{js}</script>")
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()
    site = Path(args.site).resolve()
    qa = site / "qa" / "proof-gradient-sovereign"
    qa.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f"ERROR: Playwright missing: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    screenshots: list[str] = []
    with sync_playwright() as playwright:
        executable = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=executable,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        feature_html = inline_local_assets(site, "proof-gradient-challenge.html")

        for name, width, height in VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.emulate_media(reduced_motion="reduce")
            console_errors: list[str] = []
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.set_content(feature_html, wait_until="load")

            if "Proof Gradient" not in page.title():
                errors.append(f"{name}: wrong page title")
            if page.locator('body[data-proof-gradient-edition="sovereign-v3"]').count() != 1:
                errors.append(f"{name}: Sovereign v3 design marker missing")
            if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
                errors.append(f"{name}: horizontal overflow")
            if page.locator(".pgs-contract").count() != 48:
                errors.append(f"{name}: expected 48 contract cards")
            if page.locator("text=Where autonomous work earns the right to become capability.").count() < 1:
                errors.append(f"{name}: hero copy missing")
            if page.locator('a[href="ethereum-mainnet.html"]').count() < 2:
                errors.append(f"{name}: Mainnet record cross-links missing")
            if page.locator(".pgs-hero h1").bounding_box() is None:
                errors.append(f"{name}: hero heading is not visible")

            for index in range(page.locator(".pgs-actions .pgs-btn").count()):
                button = page.locator(".pgs-actions .pgs-btn").nth(index)
                box = button.bounding_box()
                if box is None or box["height"] < MIN_CONTROL_HEIGHT:
                    errors.append(f"{name}: action button is hidden or below {MIN_CONTROL_HEIGHT}px")

            page.locator("#pgs-search").fill("Chronicle")
            visible = page.locator(".pgs-contract:not([hidden])").count()
            if visible != 1:
                errors.append(f"{name}: contract search expected 1 result, found {visible}")
            page.locator("#pgs-search").fill("")
            if page.locator(".pgs-contract:not([hidden])").count() != 48:
                errors.append(f"{name}: clearing search did not restore 48 cards")

            if console_errors:
                warnings.extend(f"{name}: console error: {message}" for message in console_errors[:10])
            if args.screenshots:
                target = qa / f"proof-gradient-{name}.png"
                page.screenshot(path=str(target), full_page=True)
                screenshots.append(str(target.relative_to(site)))
            page.close()

        home = browser.new_page(viewport={"width": 1440, "height": 1000})
        home.set_content(inline_local_assets(site, "index.html"), wait_until="load")
        if home.locator(".pgs-home").count() != 1:
            errors.append("homepage: Proof Gradient feature panel count is not one")
        if home.locator("#ethereum-mainnet-record").count() != 1:
            errors.append("homepage: Ethereum Mainnet feature panel count is not one")
        if home.locator('.pgs-home a[href="ethereum-mainnet.html"]').count() != 1:
            errors.append("homepage: Proof Gradient feature does not link to the Mainnet record")
        if home.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
            errors.append("homepage: horizontal overflow")
        if args.screenshots and home.locator(".pgs-home").count() == 1:
            target = qa / "proof-gradient-homepage-panel.png"
            home.locator(".pgs-home").screenshot(path=str(target))
            screenshots.append(str(target.relative_to(site)))
        home.close()
        browser.close()

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "screenshots": screenshots,
        "viewports": [f"{width}x{height}" for _, width, height in VIEWPORTS],
        "minimumControlHeight": MIN_CONTROL_HEIGHT,
        "edition": "SOVEREIGN_V3",
        "publicNetworkTransactionSent": False,
    }
    (qa / "visual-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
