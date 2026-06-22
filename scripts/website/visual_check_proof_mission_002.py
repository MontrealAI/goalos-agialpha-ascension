#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def inline_local_assets(site: Path, relative: str) -> str:
    raw = (site / relative).read_text(encoding="utf-8")
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
    qa = site / "qa" / "proof-mission-002"
    qa.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f"ERROR: Playwright missing: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    screenshots: list[str] = []
    with sync_playwright() as playwright:
        executable = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        browser = playwright.chromium.launch(headless=True, executable_path=executable) if executable else playwright.chromium.launch(headless=True)
        mission_html = inline_local_assets(site, "proof-mission-002.html")
        hub_html = inline_local_assets(site, "proof-missions.html")

        for name, width, height in [("desktop", 1440, 1100), ("mobile", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.emulate_media(reduced_motion="reduce")
            page.set_content(mission_html, wait_until="load")
            if "Ascension Protocol" not in page.title():
                errors.append(f"{name}: wrong Mission 002 title")
            if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
                errors.append(f"{name}: Mission 002 horizontal overflow")
            if page.locator(".ap-route-item").count() != 17:
                errors.append(f"{name}: expected 17 proof-route entries")
            if page.locator("text=Where proven capability learns to travel.").count() < 1:
                errors.append(f"{name}: hero subtitle missing")
            if page.locator("text=No transfer without provenance.").count() < 1:
                errors.append(f"{name}: constitutional rule missing")
            if args.screenshots:
                target = qa / f"proof-mission-002-{name}.png"
                page.screenshot(path=str(target), full_page=True)
                screenshots.append(str(target.relative_to(site)))
            page.close()

        for name, width, height in [("hub-desktop", 1440, 1000), ("hub-mobile", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.emulate_media(reduced_motion="reduce")
            page.set_content(hub_html, wait_until="load")
            if "Proof Missions" not in page.title():
                errors.append(f"{name}: wrong Proof Missions title")
            if page.locator(".pm-card").count() != 2:
                errors.append(f"{name}: expected two mission cards")
            if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
                errors.append(f"{name}: Proof Missions horizontal overflow")
            if args.screenshots:
                target = qa / f"proof-missions-{name}.png"
                page.screenshot(path=str(target), full_page=True)
                screenshots.append(str(target.relative_to(site)))
            page.close()

        home = browser.new_page(viewport={"width": 1440, "height": 1000})
        home.set_content(inline_local_assets(site, "index.html"), wait_until="load")
        if home.locator(".pgs-home").count() != 1:
            errors.append("homepage: Mission 001 panel count is not one")
        if home.locator(".ap-home").count() != 1:
            errors.append("homepage: Mission 002 panel count is not one")
        if args.screenshots:
            target = qa / "proof-mission-002-homepage-panel.png"
            home.locator(".ap-home").screenshot(path=str(target))
            screenshots.append(str(target.relative_to(site)))
        home.close()
        browser.close()

    report = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "screenshots": screenshots,
        "viewports": ["1440x1100", "390x844"],
        "publicNetworkTransactionSent": False,
    }
    (qa / "visual-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
