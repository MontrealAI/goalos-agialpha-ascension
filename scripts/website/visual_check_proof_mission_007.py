#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

PAGE = "proof-mission-007.html"
REQUIRED = [PAGE, "proof-mission-006.html", "proof-missions.html", "index.html"]


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def write_report(output: Path, report: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "browser-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


def launch_browser(playwright):
    try:
        return playwright.chromium.launch(headless=True)
    except Exception:
        executable = (
            shutil.which("chromium")
            or shutil.which("chromium-browser")
            or shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
        )
        if not executable:
            raise
        return playwright.chromium.launch(
            headless=True, executable_path=executable, args=["--no-sandbox"]
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--output", default="site/qa/proof-mission-007")
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()

    site = Path(args.site).resolve()
    output = Path(args.output).resolve()
    missing = [
        name
        for name in REQUIRED
        if not (site / name).is_file() or (site / name).stat().st_size == 0
    ]
    if missing:
        write_report(
            output,
            {
                "status": "FAIL",
                "desktop": {},
                "mobile": {},
                "search": {},
                "hub": {},
                "homepage": {},
                "errors": [
                    "Generated page preflight failed. Missing or empty: "
                    + ", ".join(missing),
                    "Run build_proof_mission_006.py and build_proof_mission_007.py before browser QA.",
                ],
            },
        )
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        write_report(
            output,
            {
                "status": "FAIL",
                "desktop": {},
                "mobile": {},
                "search": {},
                "hub": {},
                "homepage": {},
                "errors": ["Playwright is required for browser QA: " + str(exc)],
            },
        )
        return 2

    output.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "FAIL",
        "desktop": {},
        "mobile": {},
        "search": {},
        "hub": {},
        "homepage": {},
        "errors": [],
    }

    try:
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            mission_html = (site / PAGE).read_text(encoding="utf-8")

            for label, width, height in (("desktop", 1440, 1100), ("mobile", 390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height})
                page.set_content(mission_html, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_selector("h1", state="visible", timeout=10000)
                title = norm(page.locator("h1").inner_text())
                overflow = page.evaluate(
                    "document.documentElement.scrollWidth-document.documentElement.clientWidth"
                )
                page.screenshot(
                    path=str(output / f"proof-mission-007-{label}.png"), full_page=True
                )
                report[label] = {
                    "title": title,
                    "horizontalOverflowPx": overflow,
                    "pass": title == "THE CIVILIZATIONAL COVENANT" and overflow <= 1,
                }
                if label == "desktop":
                    page.wait_for_selector("#cv-route-search", state="visible", timeout=10000)
                    page.locator("#cv-route-search").fill("Chronicle")
                    page.wait_for_timeout(150)
                    visible = int(page.locator("#cv-route-visible").inner_text())
                    report["search"] = {
                        "query": "Chronicle",
                        "visible": visible,
                        "pass": 1 <= visible < 48,
                    }
                page.close()

            for relative, key, screenshot_name in (
                ("proof-missions.html", "hub", "proof-missions-hub"),
                ("index.html", "homepage", "proof-mission-007-homepage-panel"),
            ):
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.set_content(
                    (site / relative).read_text(encoding="utf-8"),
                    wait_until="domcontentloaded",
                    timeout=20000,
                )
                overflow = page.evaluate(
                    "document.documentElement.scrollWidth-document.documentElement.clientWidth"
                )
                page.screenshot(
                    path=str(output / f"{screenshot_name}.png"), full_page=False
                )
                report[key] = {
                    "horizontalOverflowPx": overflow,
                    "pass": overflow <= 1,
                }
                page.close()

            browser.close()

        report["status"] = (
            "PASS"
            if all(
                report[key].get("pass", False)
                for key in ("desktop", "mobile", "search", "hub", "homepage")
            )
            else "FAIL"
        )
    except Exception as exc:
        report["errors"].append(str(exc))

    write_report(output, report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
