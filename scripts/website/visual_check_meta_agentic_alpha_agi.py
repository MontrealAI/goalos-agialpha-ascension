#!/usr/bin/env python3
"""Run Chromium interaction and visual QA for GoalOS META-Agentic α-AGI."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import socket
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator

RELEASE_TITLE = "GoalOS AGIALPHA Ascension META-AGENTIC α‑AGI 👁️✨"


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


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


@contextlib.contextmanager
def serve(directory: Path) -> Iterator[str]:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = int(probe.getsockname()[1])
    handler = partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def inline_release_page(site: Path, filename: str) -> str:
    html = (site / filename).read_text(encoding="utf-8")
    css = "\n".join((site / "assets" / name).read_text(encoding="utf-8") for name in ("goalos-v86-preserve.css", "meta-agentic-alpha-agi.css"))
    javascript = (site / "assets" / "meta-agentic-alpha-agi.js").read_text(encoding="utf-8").replace("</script", "<" + "\\/script")
    data = json.loads((site / "data" / "meta-agentic-alpha-agi.json").read_text(encoding="utf-8"))
    data_literal = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    html = re.sub(r'<meta\s+http-equiv="Content-Security-Policy"[^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<link\s+[^>]*rel="stylesheet"[^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src="[^"]+"[^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
    html = html.replace("</head>", f"<style data-qa-inline-styles>\n{css}\n</style>\n</head>", 1)
    scripts = f"<script>window.GOALOS_META_AGENTIC_DATA={data_literal};</script>\n<script>{javascript}</script>\n"
    return html.replace("</body>", scripts + "</body>", 1)


def inline_homepage(site: Path) -> str:
    html = (site / "index.html").read_text(encoding="utf-8")
    css = "\n".join((site / "assets" / name).read_text(encoding="utf-8") for name in ("goalos-v86-preserve.css", "meta-agentic-alpha-agi.css"))
    html = re.sub(r'<link\s+[^>]*rel=[\'"]stylesheet[\'"][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src=[\'"][^\'"]+[\'"][^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
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


def attach_diagnostics(page: Any, console_errors: list[str], failed_requests: list[str]) -> None:
    page.on("console", lambda message: console_errors.append(f"{page.url}: {message.text}") if message.type == "error" else None)
    page.on("pageerror", lambda error: console_errors.append(f"{page.url}: {error}"))
    page.on("requestfailed", lambda request: failed_requests.append(f"{request.method} {request.url}: {request.failure}"))


def wait_ready(page: Any) -> None:
    page.wait_for_selector('html[data-maa-ready="true"]', timeout=15000)


def run_flagship(page: Any) -> tuple[str, str]:
    page.locator("#maa-mission").fill("Design the most defensible enterprise launch sequence for GoalOS as the proof, evaluation, and authorization layer for high-consequence autonomous AI work.")
    page.locator("#maa-decision").fill("Select the first paid deployment wedge, its independent proof gates, and its reversible ninety-day pilot sequence.")
    page.locator('input[name="posture"][value="ascension"]').check()
    page.locator("#maa-budget").select_option("full")
    page.locator("#maa-reviewer").check()
    page.locator("#maa-launch").click()
    page.wait_for_selector('#maa-app[data-run-state="HUMAN_REVIEW_READY"]', timeout=20000)
    return page.locator("#maa-run-id").inner_text(), page.locator(".maa-candidate-card.is-selected").get_attribute("data-candidate-id") or ""


def run(site: Path, output: Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        report = {
            "schema": "goalos.meta_agentic_alpha_agi.browser_qa.v2",
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
    failed_requests: list[str] = []
    experience_html = inline_release_page(site, "meta-agentic-alpha-agi.html")
    architecture_html = inline_release_page(site, "meta-agentic-alpha-agi-architecture.html")
    homepage_html = inline_homepage(site)

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            desktop = browser.new_context(viewport={"width": 1440, "height": 1000}, device_scale_factor=1, reduced_motion="reduce", accept_downloads=True)
            page = desktop.new_page()
            attach_diagnostics(page, console_errors, failed_requests)
            page.set_content(experience_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(page)
            check(results, "experience-document-load", True, page.url)
            check(results, "experience-title", page.title() == RELEASE_TITLE, page.title())
            check(results, "experience-hero-visible", page.locator("#maa-title").is_visible(), page.locator("#maa-title").inner_text())
            check(results, "experience-default-boundary", "No live model" in page.locator(".maa-boundary-chip").inner_text(), page.locator(".maa-boundary-chip").inner_text())
            check(results, "experience-nine-agent-constitution", page.locator(".maa-agent-card").count() == 9, page.locator(".maa-agent-card").count())
            desktop_overflow = overflow(page)
            check(results, "experience-desktop-no-horizontal-overflow", not desktop_overflow["overflow"], desktop_overflow)
            page.screenshot(path=str(output / "experience-hero-desktop.png"), full_page=False)
            check(results, "experience-hero-desktop-screenshot", (output / "experience-hero-desktop.png").is_file(), str(output / "experience-hero-desktop.png"))

            first_run_id, first_selected_id = run_flagship(page)
            candidate_count = page.locator(".maa-candidate-card").count()
            frontier_count = page.locator(".maa-candidate-card.is-frontier").count()
            selected_count = page.locator(".maa-candidate-card.is-selected").count()
            check(results, "runtime-human-review-ready", page.locator("#maa-runtime-state").inner_text() == "HUMAN REVIEW READY", page.locator("#maa-runtime-state").inner_text())
            check(results, "runtime-flagship-population-24", candidate_count == 24, candidate_count)
            check(results, "runtime-pareto-frontier-nonempty", 1 <= frontier_count < candidate_count, frontier_count)
            check(results, "runtime-single-selected-institution", selected_count == 1, selected_count)
            check(results, "runtime-eight-proof-gates", page.locator("#maa-gate-count").inner_text().startswith("8 / 8"), page.locator("#maa-gate-count").inner_text())
            check(results, "runtime-six-layer-constitution", page.locator("#maa-constitution-list dt").count() == 6 and page.locator("#maa-constitution-list dd").count() == 6, {"dt": page.locator("#maa-constitution-list dt").count(), "dd": page.locator("#maa-constitution-list dd").count()})
            check(results, "runtime-zero-external-actions", page.locator("#maa-action-count").inner_text() == "0", page.locator("#maa-action-count").inner_text())
            check(results, "runtime-decision-boundary", page.locator("#maa-decision-state").inner_text() == "HUMAN REVIEW REQUIRED", page.locator("#maa-decision-state").inner_text())
            check(results, "runtime-lineage-interactive", page.locator(".maa-lineage-node").count() == 24, page.locator(".maa-lineage-node").count())
            check(results, "runtime-pareto-plot-interactive", page.locator(".maa-plot-point").count() == 24, page.locator(".maa-plot-point").count())

            with page.expect_download(timeout=10000) as download_info:
                page.locator("#maa-download").click()
            docket_download = download_info.value
            docket_path = output / "sample-evidence-docket.json"
            docket_download.save_as(str(docket_path))
            docket = json.loads(docket_path.read_text(encoding="utf-8"))
            docket_ok = (
                docket.get("schema") == "goalos.meta_agentic_alpha_agi.evidence_docket.v2"
                and len(docket.get("evolution_engine", {}).get("candidates", [])) == 24
                and docket.get("decision_state", {}).get("status") == "HUMAN_REVIEW_READY"
                and docket.get("authorization", {}).get("external_actions") == 0
                and docket.get("authorization", {}).get("production_activation") == "WITHHELD"
            )
            check(results, "runtime-json-docket-v2", docket_ok, {"filename": docket_download.suggested_filename, "run": docket.get("run", {}).get("id")})

            with page.expect_download(timeout=10000) as brief_info:
                page.locator("#maa-download-md").click()
            brief_download = brief_info.value
            brief_path = output / "sample-executive-brief.md"
            brief_download.save_as(str(brief_path))
            brief = brief_path.read_text(encoding="utf-8")
            check(results, "runtime-executive-brief", "HUMAN_REVIEW_READY" in brief and "External actions: 0" in brief and "Selected institution" in brief, brief_download.suggested_filename)

            page.locator("#maa-reset").click()
            page.locator("#maa-reviewer").check()
            page.locator("#maa-launch").click()
            page.wait_for_selector('#maa-app[data-run-state="HUMAN_REVIEW_READY"]', timeout=20000)
            second_run_id = page.locator("#maa-run-id").inner_text()
            second_selected_id = page.locator(".maa-candidate-card.is-selected").get_attribute("data-candidate-id") or ""
            check(results, "runtime-deterministic-run-id", first_run_id == second_run_id, {"first": first_run_id, "second": second_run_id})
            check(results, "runtime-deterministic-selection", first_selected_id == second_selected_id, {"first": first_selected_id, "second": second_selected_id})

            page.locator("#mission-lab").scroll_into_view_if_needed()
            page.wait_for_timeout(150)
            page.screenshot(path=str(output / "experience-foundry-desktop.png"), full_page=False)
            check(results, "experience-foundry-desktop-screenshot", (output / "experience-foundry-desktop.png").is_file(), str(output / "experience-foundry-desktop.png"))
            page.locator("#proof").scroll_into_view_if_needed()
            page.wait_for_timeout(150)
            page.screenshot(path=str(output / "experience-proof-desktop.png"), full_page=False)
            check(results, "experience-proof-desktop-screenshot", (output / "experience-proof-desktop.png").is_file(), str(output / "experience-proof-desktop.png"))

            architecture = desktop.new_page()
            attach_diagnostics(architecture, console_errors, failed_requests)
            architecture.set_content(architecture_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(architecture)
            check(results, "architecture-document-load", True, architecture.url)
            check(results, "architecture-translation-six-rows", architecture.locator(".maa-map-row:not(.maa-map-head)").count() == 6, architecture.locator(".maa-map-row:not(.maa-map-head)").count())
            check(results, "architecture-eight-state-cards", architecture.locator(".maa-state-card").count() == 8, architecture.locator(".maa-state-card").count())
            check(results, "architecture-nine-agent-powers", architecture.locator(".maa-architecture-agent").count() == 9, architecture.locator(".maa-architecture-agent").count())
            check(results, "architecture-six-governance-principles", architecture.locator(".maa-governance-card").count() == 6, architecture.locator(".maa-governance-card").count())
            architecture_overflow = overflow(architecture)
            check(results, "architecture-desktop-no-horizontal-overflow", not architecture_overflow["overflow"], architecture_overflow)
            architecture.screenshot(path=str(output / "architecture-desktop.png"), full_page=False)
            check(results, "architecture-desktop-screenshot", (output / "architecture-desktop.png").is_file(), str(output / "architecture-desktop.png"))

            homepage = desktop.new_page()
            homepage.set_content(homepage_html, wait_until="domcontentloaded", timeout=30000)
            gateway = homepage.locator(".maa-home-gateway")
            gateway.scroll_into_view_if_needed()
            check(results, "homepage-gateway-visible", gateway.is_visible(), gateway.count())
            check(results, "homepage-feature-links", homepage.locator('a[href="meta-agentic-alpha-agi.html"]').count() >= 2, homepage.locator('a[href="meta-agentic-alpha-agi.html"]').count())
            gateway.screenshot(path=str(output / "homepage-gateway-desktop.png"))
            check(results, "homepage-gateway-desktop-screenshot", (output / "homepage-gateway-desktop.png").is_file(), str(output / "homepage-gateway-desktop.png"))
            desktop.close()

            tablet = browser.new_context(viewport={"width": 1024, "height": 1366}, device_scale_factor=1, reduced_motion="reduce")
            tablet_page = tablet.new_page()
            attach_diagnostics(tablet_page, console_errors, failed_requests)
            tablet_page.set_content(experience_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(tablet_page)
            tablet_overflow = overflow(tablet_page)
            check(results, "experience-tablet-no-horizontal-overflow", not tablet_overflow["overflow"], tablet_overflow)
            check(results, "experience-tablet-composer-visible", tablet_page.locator("#maa-mission-form").is_visible(), tablet_page.locator("#maa-mission-form").count())
            tablet_page.screenshot(path=str(output / "experience-tablet.png"), full_page=False)
            check(results, "experience-tablet-screenshot", (output / "experience-tablet.png").is_file(), str(output / "experience-tablet.png"))
            tablet.close()

            mobile = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, reduced_motion="reduce", accept_downloads=True)
            mobile_page = mobile.new_page()
            attach_diagnostics(mobile_page, console_errors, failed_requests)
            mobile_page.set_content(experience_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(mobile_page)
            mobile_overflow = overflow(mobile_page)
            check(results, "experience-mobile-no-horizontal-overflow", not mobile_overflow["overflow"], mobile_overflow)
            check(results, "experience-mobile-hero-visible", mobile_page.locator("#maa-title").is_visible(), mobile_page.locator("#maa-title").count())
            mobile_page.locator(".maa-nav-toggle").click()
            check(results, "experience-mobile-navigation", mobile_page.locator("#maa-nav").evaluate("node => node.classList.contains('is-open')"), mobile_page.locator("#maa-nav").get_attribute("class"))
            mobile_page.locator(".maa-nav-toggle").click()
            mobile_page.screenshot(path=str(output / "experience-mobile.png"), full_page=False)
            check(results, "experience-mobile-screenshot", (output / "experience-mobile.png").is_file(), str(output / "experience-mobile.png"))
            run_flagship(mobile_page)
            mobile_page.locator("#mission-lab").scroll_into_view_if_needed()
            mobile_page.wait_for_timeout(150)
            mobile_runtime_overflow = overflow(mobile_page)
            check(results, "experience-mobile-runtime-no-horizontal-overflow", not mobile_runtime_overflow["overflow"], mobile_runtime_overflow)
            mobile_page.screenshot(path=str(output / "experience-foundry-mobile.png"), full_page=False)
            check(results, "experience-foundry-mobile-screenshot", (output / "experience-foundry-mobile.png").is_file(), str(output / "experience-foundry-mobile.png"))

            mobile_architecture = mobile.new_page()
            attach_diagnostics(mobile_architecture, console_errors, failed_requests)
            mobile_architecture.set_content(architecture_html, wait_until="domcontentloaded", timeout=30000)
            wait_ready(mobile_architecture)
            mobile_arch_overflow = overflow(mobile_architecture)
            check(results, "architecture-mobile-no-horizontal-overflow", not mobile_arch_overflow["overflow"], mobile_arch_overflow)
            mobile_architecture.screenshot(path=str(output / "architecture-mobile.png"), full_page=False)
            check(results, "architecture-mobile-screenshot", (output / "architecture-mobile.png").is_file(), str(output / "architecture-mobile.png"))
            mobile.close()
        except PlaywrightTimeoutError as exc:
            check(results, "browser-timeout", False, str(exc))
        except Exception as exc:
            check(results, "browser-unexpected-error", False, f"{type(exc).__name__}: {exc}")
        finally:
            browser.close()

    check(results, "browser-console-clean", not console_errors, console_errors)
    check(results, "browser-network-clean", not failed_requests, failed_requests)
    failed = [item for item in results if item["status"] != "PASS"]
    report = {
        "schema": "goalos.meta_agentic_alpha_agi.browser_qa.v2",
        "release_title": RELEASE_TITLE,
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(results),
        "checks_passed": len(results) - len(failed),
        "checks_failed": len(failed),
        "checks": results,
        "screenshots": sorted(path.name for path in output.glob("*.png")),
        "downloads": sorted(path.name for path in output.glob("sample-*")),
        "qa_mode": "served-generated-release-desktop-tablet-mobile-interaction-runtime",
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
        args.output = args.site / "qa" / "meta-agentic-alpha-agi"
    return args


def main() -> int:
    args = parse_args()
    report = run(args.site.resolve(), args.output.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
