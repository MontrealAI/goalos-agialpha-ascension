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
    qa = site / "qa/proof-mission-004"
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
        mission_html = inline_local_assets(site, "proof-mission-004.html")
        hub_html = inline_local_assets(site, "proof-missions.html")

        for name, width, height in [("desktop", 1440, 1100), ("mobile", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.emulate_media(reduced_motion="reduce")
            page.set_content(mission_html, wait_until="load")
            if "Sovereign Institution" not in page.title():
                errors.append(f"{name}: wrong Mission 004 title")
            if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
                errors.append(f"{name}: Mission 004 horizontal overflow")
            if page.locator(".si-route-item").count() != 34:
                errors.append(f"{name}: expected 34 proof-route entries")
            if page.locator(".si-validator").count() != 5:
                errors.append(f"{name}: expected five validator cards")
            if page.locator("text=Where governed intelligence learns to endure.").count() < 1:
                errors.append(f"{name}: hero subtitle missing")
            if page.locator("text=No mandate, no mission.").count() < 1:
                errors.append(f"{name}: constitutional rule missing")
            if name == "desktop":
                search = page.locator("#si-route-search")
                search.fill("TreasuryRouter")
                visible_count = page.locator(".si-route-item:not(.si-hidden)").count()
                if visible_count != 1:
                    errors.append(f"desktop: route search expected one TreasuryRouter result, found {visible_count}")
                search.fill("")
            if args.screenshots:
                target = qa / f"proof-mission-004-{name}.png"
                page.screenshot(path=str(target), full_page=True)
                screenshots.append(str(target.relative_to(site)))
            page.close()

        for name, width, height in [("hub-desktop", 1440, 1000), ("hub-mobile", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.emulate_media(reduced_motion="reduce")
            page.set_content(hub_html, wait_until="load")
            if "Proof Missions" not in page.title():
                errors.append(f"{name}: wrong Proof Missions title")
            if page.locator(".pm-card").count() != 4:
                errors.append(f"{name}: expected four mission cards")
            if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
                errors.append(f"{name}: Proof Missions horizontal overflow")
            if page.locator("text=The Sovereign Institution").count() < 1:
                errors.append(f"{name}: Mission 004 card missing")
            if args.screenshots:
                target = qa / f"proof-missions-{name}.png"
                page.screenshot(path=str(target), full_page=True)
                screenshots.append(str(target.relative_to(site)))
            page.close()

        home = browser.new_page(viewport={"width": 1440, "height": 1000})
        home.set_content(inline_local_assets(site, "index.html"), wait_until="load")
        for selector, label in [
            (".pgs-home", "Mission 001"),
            (".ap-home", "Mission 002"),
            (".cc-home", "Mission 003"),
            (".si-home", "Mission 004"),
        ]:
            if home.locator(selector).count() != 1:
                errors.append(f"homepage: {label} panel count is not one")
        if home.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"):
            errors.append("homepage: horizontal overflow after Mission 004 panel")
        if args.screenshots:
            target = qa / "proof-mission-004-homepage-panel.png"
            home.locator(".si-home").screenshot(path=str(target))
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
