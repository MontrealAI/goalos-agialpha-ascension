#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

PAGE = "proof-mission-008.html"
REQUIRED = [PAGE, "proof-mission-007.html", "proof-missions.html", "index.html"]


def norm(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def write_report(output: Path, report: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "browser-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
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
            headless=True,
            executable_path=executable,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--output", default="site/qa/proof-mission-008")
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()

    site = Path(args.site).resolve()
    output = Path(args.output).resolve()
    missing = [name for name in REQUIRED if not (site / name).is_file() or (site / name).stat().st_size == 0]
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
                    "Generated page preflight failed. Missing or empty: " + ", ".join(missing),
                    "Run build_proof_mission_007.py and build_proof_mission_008.py before browser QA.",
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
                page.set_content(mission_html, wait_until="domcontentloaded", timeout=20_000)
                page.wait_for_selector("h1", state="visible", timeout=10_000)
                title = norm(page.locator("h1").inner_text())
                overflow = page.evaluate(
                    "document.documentElement.scrollWidth-document.documentElement.clientWidth"
                )
                if args.screenshots:
                    page.screenshot(path=str(output / f"proof-mission-008-{label}.png"), full_page=True)
                report[label] = {
                    "title": title,
                    "horizontalOverflowPx": overflow,
                    "pass": title == "THE OPEN FUTURE" and overflow <= 1,
                }
                if label == "desktop":
                    page.wait_for_selector("#of-route-search", state="visible", timeout=10_000)
                    page.locator("#of-route-search").fill("Chronicle")
                    page.wait_for_timeout(150)
                    visible = int(page.locator("#of-route-visible").inner_text())
                    report["search"] = {
                        "query": "Chronicle",
                        "visible": visible,
                        "pass": 1 <= visible < 48,
                    }
                page.close()

            hub = browser.new_page(viewport={"width": 1440, "height": 1000})
            hub.set_content((site / "proof-missions.html").read_text(encoding="utf-8"), wait_until="domcontentloaded")
            hub_overflow = hub.evaluate(
                "document.documentElement.scrollWidth-document.documentElement.clientWidth"
            )
            hub_cards = hub.locator(".of-mission-card").count()
            if args.screenshots:
                hub.screenshot(path=str(output / "proof-missions-hub.png"), full_page=False)
            report["hub"] = {
                "horizontalOverflowPx": hub_overflow,
                "missionCards": hub_cards,
                "pass": hub_overflow <= 1 and hub_cards >= 8,
            }
            hub.close()

            homepage_html = (site / "index.html").read_text(encoding="utf-8")
            homepage_checks = []
            for label, width, height in (("desktop", 1440, 1000), ("mobile", 390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height})
                page.set_content(homepage_html, wait_until="domcontentloaded", timeout=20_000)
                page.wait_for_selector(".cv-home", state="attached", timeout=10_000)
                page.wait_for_selector(".of-home", state="visible", timeout=10_000)
                metrics = page.evaluate(
                    """() => {
                      const prior = document.querySelector('.cv-home');
                      const current = document.querySelector('.of-home');
                      const pr = prior.getBoundingClientRect();
                      const cr = current.getBoundingClientRect();
                      const cs = getComputedStyle(current);
                      return {
                        viewport: innerWidth,
                        prior: {left: pr.left, right: pr.right, width: pr.width, bottom: pr.bottom},
                        current: {left: cr.left, right: cr.right, width: cr.width, top: cr.top},
                        borderRadius: cs.borderRadius,
                        backgroundImage: cs.backgroundImage,
                        stats: current.querySelectorAll('.of-home-stat').length,
                        buttons: current.querySelectorAll('.of-home-actions a').length,
                        seriesMarker: current.dataset.proofMissionSeries || '',
                        missionMarker: current.dataset.proofMission || '',
                        overflow: document.documentElement.scrollWidth-document.documentElement.clientWidth
                      };
                    }"""
                )
                width_delta = abs(metrics["current"]["width"] - metrics["prior"]["width"])
                left_delta = abs(metrics["current"]["left"] - metrics["prior"]["left"])
                right_delta = abs(metrics["current"]["right"] - metrics["prior"]["right"])
                gap = metrics["current"]["top"] - metrics["prior"]["bottom"]
                current_within_viewport = (
                    metrics["current"]["left"] >= -1
                    and metrics["current"]["right"] <= metrics["viewport"] + 1
                )
                passed = (
                    current_within_viewport
                    and width_delta <= 2
                    and left_delta <= 2
                    and right_delta <= 2
                    and abs(gap) <= 2
                    and metrics["borderRadius"] in ("0px", "0px 0px 0px 0px")
                    and metrics["stats"] == 4
                    and metrics["buttons"] == 3
                    and metrics["seriesMarker"] == "sovereign"
                    and metrics["missionMarker"] == "008"
                )
                metrics.update(
                    {
                        "label": label,
                        "widthDeltaVsMission007": width_delta,
                        "leftDeltaVsMission007": left_delta,
                        "rightDeltaVsMission007": right_delta,
                        "verticalGapAfterMission007": gap,
                        "pass": passed,
                    }
                )
                homepage_checks.append(metrics)
                if args.screenshots:
                    page.locator(".of-home").screenshot(
                        path=str(output / f"proof-mission-008-homepage-panel-{label}.png")
                    )
                page.close()

            report["homepage"] = {
                "viewports": homepage_checks,
                "pass": all(item["pass"] for item in homepage_checks),
                "designRequirement": "Mission 008 must be full-bleed and geometrically aligned with Mission 007; inherited overflow elsewhere is reported but does not authorize modifying prior missions",
            }
            browser.close()

        report["status"] = (
            "PASS"
            if all(report[key].get("pass", False) for key in ("desktop", "mobile", "search", "hub", "homepage"))
            else "FAIL"
        )
    except Exception as exc:
        report["errors"].append(str(exc))

    write_report(output, report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
