#!/usr/bin/env python3
"""Run Chromium interaction and visual QA for GoalOS AGI Alpha Node v0."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Alpha Node v0 ⚡️✨"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check(results: list[dict[str, Any]], label: str, condition: bool, detail: Any = "") -> None:
    results.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})


def overflow(page: Any) -> dict[str, int | bool]:
    return page.evaluate(
        """() => ({
          documentWidth: document.documentElement.scrollWidth,
          viewportWidth: document.documentElement.clientWidth,
          bodyWidth: document.body.scrollWidth,
          overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
        })"""
    )


def inline_release_page(site: Path, filename: str) -> str:
    html = (site / filename).read_text(encoding="utf-8")
    css = (site / "assets" / "agi-alpha-node-v0.css").read_text(encoding="utf-8")
    javascript = (site / "assets" / "agi-alpha-node-v0.js").read_text(encoding="utf-8").replace("</script", "<" + "\\/script")
    html = re.sub(r'<meta\s+http-equiv="Content-Security-Policy"[^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<link\s+[^>]*rel="stylesheet"[^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src="[^"]+"[^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
    html = html.replace("</head>", f"<style data-qa-inline-styles>\n{css}\n</style>\n</head>", 1)
    return html.replace("</body>", f"<script>{javascript}</script>\n</body>", 1)


def inline_homepage(site: Path) -> str:
    html = (site / "index.html").read_text(encoding="utf-8")
    asset_names = ["goalos-v86-preserve.css", "meta-agentic-alpha-agi.css", "agi-alpha-node-v0.css"]
    css = "\n".join((site / "assets" / name).read_text(encoding="utf-8") for name in asset_names if (site / "assets" / name).is_file())
    html = re.sub(r'<link\s+[^>]*rel=[\'\"]stylesheet[\'\"][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src=[\'\"][^\'\"]+[\'\"][^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
    return html.replace("</head>", f"<style data-qa-inline-styles>\n{css}\n</style>\n</head>", 1)


def launch_browser(playwright: Any) -> Any:
    args = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
    try:
        return playwright.chromium.launch(headless=True, args=args)
    except Exception:
        executable = (
            os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
            or os.environ.get("CHROMIUM_PATH")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
            or shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
        )
        if not executable:
            raise
        return playwright.chromium.launch(headless=True, executable_path=executable, args=args)


def attach_diagnostics(page: Any, console_errors: list[str], network_requests: list[str], failed_requests: list[str]) -> None:
    page.on("console", lambda message: console_errors.append(f"{page.url}: {message.text}") if message.type == "error" else None)
    page.on("pageerror", lambda error: console_errors.append(f"{page.url}: {error}"))
    page.on("request", lambda request: network_requests.append(f"{request.method} {request.url}") if not request.url.startswith(("about:", "data:", "blob:")) else None)
    page.on("requestfailed", lambda request: failed_requests.append(f"{request.method} {request.url}: {request.failure}"))


def wait_ready(page: Any) -> None:
    page.wait_for_selector('html[data-aan-ready="true"]', timeout=15000)


def run_cycle(page: Any) -> tuple[str, dict[str, Any]]:
    page.locator("#aan-preset").select_option("enterprise")
    page.locator("#aan-posture").select_option("ascension")
    page.locator("#aan-quorum").evaluate("node => { node.value = '5'; node.dispatchEvent(new Event('input', {bubbles:true})); }")
    page.locator("#aan-node-form").evaluate("form => form.requestSubmit()")
    page.wait_for_function("document.querySelector('#aan-final-state').textContent === 'HUMAN_REVIEW_REQUIRED'", timeout=15000)
    run_id = page.locator("#aan-run-id").inner_text()
    docket = page.evaluate("window.__AAN_QA__.getDocket()")
    return run_id, docket


def run(site: Path, output: Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        report = {
            "schema": "goalos.agi_alpha_node_v0.browser_qa.v1",
            "status": "FAIL",
            "checks_total": 1,
            "checks_passed": 0,
            "checks_failed": 1,
            "checks": [{"label": "playwright-import", "status": "FAIL", "detail": str(exc)}],
        }
        write_json(output / "browser-report.json", report)
        return report

    output.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    console_errors: list[str] = []
    network_requests: list[str] = []
    failed_requests: list[str] = []
    experience_html = inline_release_page(site, "agi-alpha-node-v0.html")
    architecture_html = inline_release_page(site, "agi-alpha-node-v0-architecture.html")
    homepage_html = inline_homepage(site)

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            context = browser.new_context(
                viewport={"width": 1440, "height": 1000},
                device_scale_factor=1,
                reduced_motion="reduce",
                accept_downloads=True,
            )
            page = context.new_page()
            page.set_default_timeout(15000)
            page.set_default_navigation_timeout(30000)
            attach_diagnostics(page, console_errors, network_requests, failed_requests)

            print("QA desktop experience", flush=True)
            page.set_content(experience_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(page)
            check(results, "experience-document-load", True, page.url)
            check(results, "experience-title", page.title() == RELEASE_TITLE, page.title())
            check(results, "experience-hero-visible", page.locator("#aan-hero-title").is_visible(), page.locator("#aan-hero-title").inner_text())
            check(results, "experience-default-deny-visible", "DEFAULT DENY" in page.locator(".aan-deny-strip").inner_text(), page.locator(".aan-deny-strip").inner_text())
            check(results, "experience-eight-stage-rail", page.locator(".aan-stage").count() == 8, page.locator(".aan-stage").count())
            check(results, "experience-eight-peer-ledger", page.locator("#aan-peer-table tr").count() == 8, page.locator("#aan-peer-table tr").count())
            check(results, "experience-seven-validators", page.locator(".aan-validator-card").count() == 7, page.locator(".aan-validator-card").count())
            check(results, "experience-fourteen-artifacts", page.locator("#aan-artifact-list li").count() == 14, page.locator("#aan-artifact-list li").count())
            desktop_overflow = overflow(page)
            check(results, "experience-desktop-no-horizontal-overflow", not desktop_overflow["overflow"], desktop_overflow)
            page.screenshot(path=str(output / "experience-hero-desktop.png"), full_page=False)
            check(results, "experience-hero-desktop-screenshot", (output / "experience-hero-desktop.png").is_file(), str(output / "experience-hero-desktop.png"))

            first_run_id, first_docket = run_cycle(page)
            check(results, "runtime-human-review-required", page.locator("#aan-final-state").inner_text() == "HUMAN_REVIEW_REQUIRED", page.locator("#aan-final-state").inner_text())
            check(results, "runtime-all-eight-gates-complete", page.locator(".aan-stage.is-complete").count() == 8, page.locator(".aan-stage.is-complete").count())
            check(results, "runtime-alpha-work-unit-generated", page.locator("#aan-metric-wu").inner_text() not in {"", "—"}, page.locator("#aan-metric-wu").inner_text())
            admitted = page.locator(".aan-peer-status.accepted").count()
            check(results, "runtime-peer-route-admitted", 3 <= admitted <= 5, admitted)
            check(results, "runtime-validator-quorum", page.locator("#aan-quorum-label").inner_text().startswith("QUORUM 5 RECORDED"), page.locator("#aan-quorum-label").inner_text())
            check(results, "runtime-dissent-visible", page.locator(".aan-validator-card.dissent").count() == 1, page.locator(".aan-validator-card.dissent").count())
            check(results, "runtime-four-guardian-signatures", page.locator(".aan-guardian.signed").count() == 4, page.locator(".aan-guardian.signed").count())
            check(results, "runtime-fourteen-artifacts-sealed", page.locator("#aan-artifact-count").inner_text() == "14 / 14 sealed", page.locator("#aan-artifact-count").inner_text())
            check(results, "runtime-authority-none", page.locator("#aan-authority").inner_text() == "NONE GRANTED", page.locator("#aan-authority").inner_text())
            auth = first_docket.get("authorization_state", {})
            docket_ok = (
                first_docket.get("schema") == "goalos.agi_alpha_node_v0.node_evidence_docket.v1"
                and first_docket.get("deterministic_seed", "").startswith("0x")
                and auth.get("state") == "HUMAN_REVIEW_REQUIRED"
                and auth.get("authority") == "NONE_GRANTED"
                and auth.get("factual_correctness") == "NOT_CERTIFIED"
                and auth.get("external_actions") == 0
                and len(first_docket.get("artifact_chain", [])) == 14
            )
            check(results, "runtime-docket-contract", docket_ok, auth)

            with page.expect_download(timeout=10000) as docket_info:
                page.locator("#aan-download-json").click()
            docket_download = docket_info.value
            docket_path = output / "sample-node-evidence-docket.json"
            docket_download.save_as(str(docket_path))
            downloaded_docket = json.loads(docket_path.read_text(encoding="utf-8"))
            check(results, "runtime-evidence-download", downloaded_docket.get("run_id") == first_docket.get("run_id") and downloaded_docket.get("authorization_state", {}).get("external_actions") == 0, docket_download.suggested_filename)

            with page.expect_download(timeout=10000) as brief_info:
                page.locator("#aan-download-md").click()
            brief_download = brief_info.value
            brief_path = output / "sample-executive-review-brief.md"
            brief_download.save_as(str(brief_path))
            brief = brief_path.read_text(encoding="utf-8")
            check(results, "runtime-review-brief-download", "HUMAN_REVIEW_REQUIRED" in brief and "External actions: 0" in brief and "Authority: NONE GRANTED" in brief, brief_download.suggested_filename)

            page.locator("#aan-reset").click()
            second_run_id, second_docket = run_cycle(page)
            check(results, "runtime-deterministic-run-id", first_run_id == second_run_id, {"first": first_run_id, "second": second_run_id})
            check(results, "runtime-deterministic-receipt", first_docket.get("work_unit_receipt") == second_docket.get("work_unit_receipt"), {"first": first_docket.get("work_unit_receipt", {}).get("receipt_id"), "second": second_docket.get("work_unit_receipt", {}).get("receipt_id")})
            check(results, "runtime-deterministic-route", first_docket.get("peer_route") == second_docket.get("peer_route"), first_docket.get("peer_route", {}).get("route_id"))

            page.locator("#aan-reset").click()
            page.locator("#aan-pause").click()
            check(results, "runtime-safe-hold-state", page.locator("#aan-state-banner b").inner_text() == "SAFE_HOLD", page.locator("#aan-state-banner b").inner_text())
            check(results, "runtime-safe-hold-disables-run", page.locator("#aan-run").is_disabled(), page.locator("#aan-run").is_disabled())
            page.locator("#aan-pause").click()
            check(results, "runtime-safe-hold-reversible", not page.locator("#aan-run").is_disabled(), page.locator("#aan-run").is_disabled())
            run_cycle(page)

            for anchor, filename, label in [
                ("#command-deck", "experience-command-deck-desktop.png", "command-deck"),
                ("#peer-mesh", "experience-peer-mesh-desktop.png", "peer-mesh"),
                ("#consensus", "experience-consensus-desktop.png", "consensus"),
                ("#evidence", "experience-evidence-desktop.png", "evidence"),
            ]:
                page.locator(anchor).scroll_into_view_if_needed()
                page.wait_for_timeout(100)
                page.screenshot(path=str(output / filename), full_page=False)
                check(results, f"experience-{label}-desktop-screenshot", (output / filename).is_file(), str(output / filename))

            print("QA architecture desktop", flush=True)
            page.set_content(architecture_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(page)
            check(results, "architecture-document-load", True, page.url)
            check(results, "architecture-six-operating-planes", page.locator("#aan-system-map > article").count() == 6, page.locator("#aan-system-map > article").count())
            check(results, "architecture-eight-translations", page.locator(".aan-translation-card").count() == 8, page.locator(".aan-translation-card").count())
            check(results, "architecture-eight-state-cards", page.locator("#aan-arch-pipeline > li").count() == 8, page.locator("#aan-arch-pipeline > li").count())
            check(results, "architecture-seven-boundaries", page.locator("#aan-boundary-list > li").count() == 7, page.locator("#aan-boundary-list > li").count())
            architecture_overflow = overflow(page)
            check(results, "architecture-desktop-no-horizontal-overflow", not architecture_overflow["overflow"], architecture_overflow)
            page.screenshot(path=str(output / "architecture-desktop.png"), full_page=False)
            check(results, "architecture-desktop-screenshot", (output / "architecture-desktop.png").is_file(), str(output / "architecture-desktop.png"))

            print("QA homepage desktop", flush=True)
            page.set_content(homepage_html, wait_until="domcontentloaded", timeout=30000)
            gateway = page.locator(".aan-home-gateway")
            gateway.scroll_into_view_if_needed()
            check(results, "homepage-gateway-visible", gateway.is_visible(), gateway.count())
            check(results, "homepage-feature-links", page.locator('a[href="agi-alpha-node-v0.html"]').count() >= 2, page.locator('a[href="agi-alpha-node-v0.html"]').count())
            check(results, "homepage-meta-agentic-preserved", page.locator(".maa-home-gateway").count() == 1, page.locator(".maa-home-gateway").count())
            gateway.screenshot(path=str(output / "homepage-gateway-desktop.png"))
            check(results, "homepage-gateway-desktop-screenshot", (output / "homepage-gateway-desktop.png").is_file(), str(output / "homepage-gateway-desktop.png"))

            print("QA tablet", flush=True)
            page.set_viewport_size({"width": 1024, "height": 1366})
            page.set_content(experience_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(page)
            tablet_overflow = overflow(page)
            check(results, "experience-tablet-no-horizontal-overflow", not tablet_overflow["overflow"], tablet_overflow)
            check(results, "experience-tablet-command-visible", page.locator("#aan-node-form").is_visible(), page.locator("#aan-node-form").count())
            page.screenshot(path=str(output / "experience-tablet.png"), full_page=False)
            check(results, "experience-tablet-screenshot", (output / "experience-tablet.png").is_file(), str(output / "experience-tablet.png"))

            print("QA mobile", flush=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.set_content(experience_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(page)
            mobile_overflow = overflow(page)
            check(results, "experience-mobile-no-horizontal-overflow", not mobile_overflow["overflow"], mobile_overflow)
            check(results, "experience-mobile-hero-visible", page.locator("#aan-hero-title").is_visible(), page.locator("#aan-hero-title").count())
            page.locator("#aan-nav-toggle").click()
            check(results, "experience-mobile-navigation", page.locator("#aan-nav").evaluate("node => node.classList.contains('is-open')"), page.locator("#aan-nav").get_attribute("class"))
            page.locator("#aan-nav-toggle").click()
            page.screenshot(path=str(output / "experience-mobile-hero.png"), full_page=False)
            check(results, "experience-mobile-hero-screenshot", (output / "experience-mobile-hero.png").is_file(), str(output / "experience-mobile-hero.png"))
            print("QA mobile cycle", flush=True)
            run_cycle(page)
            print("QA mobile evidence", flush=True)
            page.locator("#evidence").scroll_into_view_if_needed()
            page.wait_for_timeout(100)
            mobile_runtime_overflow = overflow(page)
            check(results, "experience-mobile-runtime-no-horizontal-overflow", not mobile_runtime_overflow["overflow"], mobile_runtime_overflow)
            page.screenshot(path=str(output / "experience-mobile-evidence.png"), full_page=False)
            check(results, "experience-mobile-evidence-screenshot", (output / "experience-mobile-evidence.png").is_file(), str(output / "experience-mobile-evidence.png"))

            print("QA mobile architecture", flush=True)
            page.set_content(architecture_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(page)
            page.locator("#aan-nav-toggle").click()
            check(results, "architecture-mobile-navigation", page.locator("#aan-nav").evaluate("node => node.classList.contains('is-open')"), page.locator("#aan-nav").get_attribute("class"))
            mobile_arch_overflow = overflow(page)
            check(results, "architecture-mobile-no-horizontal-overflow", not mobile_arch_overflow["overflow"], mobile_arch_overflow)
            page.screenshot(path=str(output / "architecture-mobile.png"), full_page=False)
            check(results, "architecture-mobile-screenshot", (output / "architecture-mobile.png").is_file(), str(output / "architecture-mobile.png"))
            print("QA browser phases complete", flush=True)
            context.close()
        except PlaywrightTimeoutError as exc:
            check(results, "browser-timeout", False, str(exc))
        except Exception as exc:
            check(results, "browser-unexpected-error", False, f"{type(exc).__name__}: {exc}")
        finally:
            browser.close()

    check(results, "browser-console-clean", not console_errors, console_errors)
    check(results, "browser-network-zero", not network_requests, network_requests)
    check(results, "browser-failed-requests-zero", not failed_requests, failed_requests)
    failed = [item for item in results if item["status"] != "PASS"]
    report = {
        "schema": "goalos.agi_alpha_node_v0.browser_qa.v1",
        "release_title": RELEASE_TITLE,
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(results),
        "checks_passed": len(results) - len(failed),
        "checks_failed": len(failed),
        "checks": results,
        "screenshots": sorted(path.name for path in output.glob("*.png")),
        "downloads": sorted(path.name for path in output.glob("sample-*")),
        "qa_mode": "inline-generated-release-desktop-tablet-mobile-interaction-runtime",
    }
    write_json(output / "browser-report.json", report)
    return report


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.output is None:
        args.output = args.site / "qa" / "agi-alpha-node-v0"
    return args


def main() -> int:
    args = parse_args()
    report = run(args.site.resolve(), args.output.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
