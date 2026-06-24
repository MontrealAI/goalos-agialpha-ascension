#!/usr/bin/env python3
"""Run Chromium interaction, responsive, and adversarial QA for AGI Jobs v0 (v2)."""

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
from urllib.parse import urlparse

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record(results: list[dict[str, Any]], label: str, condition: bool, detail: Any = "") -> None:
    results.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})


def overflow(page: Any) -> dict[str, Any]:
    return page.evaluate("""() => ({documentWidth: document.documentElement.scrollWidth, viewportWidth: document.documentElement.clientWidth, bodyWidth: document.body.scrollWidth, overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2})""")


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


def inline_feature_page(site: Path, filename: str) -> str:
    html = (site / filename).read_text(encoding="utf-8")
    css = (site / "assets" / "agi-jobs-v0-v2.css").read_text(encoding="utf-8")
    javascript = (site / "assets" / "agi-jobs-v0-v2.js").read_text(encoding="utf-8").replace("</script", "<" + "\\/script")
    html = re.sub(r'<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<link\s+[^>]*href=["\']assets/agi-jobs-v0-v2\.css["\'][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src=["\']assets/agi-jobs-v0-v2\.js["\'][^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
    html = html.replace("</head>", f"<style data-qa-inline-styles>\n{css}\n</style>\n</head>", 1)
    return html.replace("</body>", f"<script>{javascript}</script>\n</body>", 1)


def inline_homepage(site: Path) -> str:
    html = (site / "index.html").read_text(encoding="utf-8")
    hrefs = re.findall(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', html, flags=re.IGNORECASE)
    css_parts: list[str] = []
    for href in hrefs:
        if href.startswith(("http://", "https://", "//")):
            continue
        path = site / href.split("?", 1)[0]
        if path.is_file():
            css_parts.append(path.read_text(encoding="utf-8"))
    html = re.sub(r'<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src=["\'][^"\']+["\'][^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
    combined_css = "\n".join(css_parts)
    return html.replace("</head>", f"<style data-qa-inline-styles>\n{combined_css}\n</style>\n</head>", 1)


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


def screenshot_view(page: Any, selector: str, destination: Path) -> None:
    page.locator(selector).scroll_into_view_if_needed()
    page.wait_for_timeout(120)
    page.screenshot(path=str(destination), full_page=False)


def run(site: Path, output: Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        report = {
            "schema": "goalos.agi_jobs_v0_v2.browser_qa.v3",
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
    external_requests: list[str] = []

    experience_html = inline_feature_page(site, "agi-jobs-v0-v2.html")
    market_html = inline_feature_page(site, "agi-jobs-v0-v2-market.html")
    settlement_html = inline_feature_page(site, "agi-jobs-v0-v2-settlement.html")
    memory_html = inline_feature_page(site, "agi-jobs-v0-v2-memory.html")
    architecture_html = inline_feature_page(site, "agi-jobs-v0-v2-architecture.html")
    homepage_html = inline_homepage(site)

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            context = browser.new_context(viewport={"width": 1600, "height": 1000}, device_scale_factor=1, reduced_motion="reduce", accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(25000)
            page.on("console", lambda message: console_errors.append(f"{page.url}: {message.text}") if message.type == "error" else None)
            page.on("pageerror", lambda error: console_errors.append(f"{page.url}: {error}"))
            page.on("requestfailed", lambda request: failed_requests.append(f"{request.method} {request.url}: {request.failure}"))

            def watch_request(request: Any) -> None:
                parsed = urlparse(request.url)
                if parsed.scheme in {"http", "https", "ws", "wss"} and parsed.hostname not in {"127.0.0.1", "localhost"}:
                    external_requests.append(f"{request.method} {request.url}")

            page.on("request", watch_request)

            page.set_content(experience_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "experience-title", page.title() == RELEASE_TITLE, page.title())
            record(results, "experience-hero-visible", page.locator("#aj-hero-title").is_visible(), page.locator("#aj-hero-title").inner_text())
            record(results, "experience-six-metrics", page.locator("#aj-hero-metrics > div").count() == 6, page.locator("#aj-hero-metrics > div").count())
            record(results, "experience-eight-presets", page.locator("#aj-preset option").count() == 8, page.locator("#aj-preset option").count())
            record(results, "experience-seven-job-classes", page.locator("#aj-job-class option").count() == 7, page.locator("#aj-job-class option").count())
            record(results, "experience-five-postures", page.locator("#aj-posture option").count() == 5, page.locator("#aj-posture option").count())
            record(results, "experience-four-risk-profiles", page.locator("#aj-risk option").count() == 4, page.locator("#aj-risk option").count())
            record(results, "experience-seven-incidents", page.locator("#aj-incident option").count() == 7, page.locator("#aj-incident option").count())
            record(results, "experience-fourteen-gates", page.locator(".aj-stage").count() == 14, page.locator(".aj-stage").count())
            record(results, "experience-twelve-institutions", page.locator(".aj-institution").count() == 12, page.locator(".aj-institution").count())
            record(results, "experience-twenty-four-artifacts", page.locator(".aj-artifact-card").count() == 24, page.locator(".aj-artifact-card").count())
            record(results, "experience-seven-validators", page.locator(".aj-validator").count() == 7, page.locator(".aj-validator").count())
            record(results, "experience-five-guardians", page.locator(".aj-guardian").count() == 5, page.locator(".aj-guardian").count())
            desktop_overflow = overflow(page)
            record(results, "experience-desktop-no-overflow", not desktop_overflow["overflow"], desktop_overflow)
            page.screenshot(path=str(output / "01-sovereign-labor-civilization-hero-desktop.png"), full_page=False)

            page.locator("#aj-job-form").evaluate("form => form.requestSubmit()")
            page.wait_for_function("window.__AGI_JOBS_STATE__ && window.__AGI_JOBS_STATE__.running === false")
            state = page.evaluate("() => JSON.parse(JSON.stringify(window.__AGI_JOBS_STATE__))")
            record(results, "runtime-terminal-human-settlement-review", state["terminal"] == "HUMAN_SETTLEMENT_REVIEW", state["terminal"])
            record(results, "runtime-prime-selected", bool(state["coalition"]["prime"]["id"]), state["coalition"]["prime"]["name"])
            record(results, "runtime-two-specialists", len(state["coalition"]["specialists"]) == 2, [item["id"] for item in state["coalition"]["specialists"]])
            record(results, "runtime-shadow-selected", bool(state["coalition"]["shadow"]["id"]), state["coalition"]["shadow"]["name"])
            record(results, "runtime-three-reserves", len(state["coalition"]["reserves"]) == 3, [item["id"] for item in state["coalition"]["reserves"]])
            record(results, "runtime-no-quarantine-default", len(state["quarantined"]) == 0, state["quarantined"])
            record(results, "runtime-work-graph-eight", len(state["packages"]) == 8, len(state["packages"]))
            record(results, "runtime-six-pass-one-dissent", state["votes"]["pass"] == 6 and state["votes"]["dissent"] == 1, state["votes"]["summary"])
            record(results, "runtime-five-guardian-clear", state["guardians"]["clear"] == 5 and state["guardians"]["veto"] == 0, state["guardians"]["summary"])
            record(results, "runtime-twenty-four-chain", len(state["chain"]) == 24, len(state["chain"]))
            record(results, "runtime-chain-head-64", len(state["chain"][-1]["commitment"]) == 64, state["chain"][-1]["commitment"])
            record(results, "runtime-docket-schema", state["docket"]["schema"] == "goalos.agi_jobs_v0_v2.evidence_docket.v3", state["docket"]["schema"])
            record(results, "runtime-live-token-zero", state["docket"]["settlement"]["live_token_movement"] is False, state["docket"]["settlement"])
            record(results, "runtime-authority-none", state["docket"]["terminal"]["authority"] == "NONE_GRANTED", state["docket"]["terminal"])
            record(results, "runtime-memory-not-authorized", state["docket"]["terminal"]["memory_promotion"] == "NOT_AUTHORIZED", state["docket"]["terminal"])
            record(results, "runtime-exports-enabled", all(not page.locator(selector).is_disabled() for selector in ["#aj-download-json", "#aj-download-md", "#aj-copy-summary"]), "")
            record(results, "runtime-ui-fourteen-gates", page.locator(".aj-stage.is-complete").count() + page.locator(".aj-stage.is-active").count() == 14, {"complete": page.locator(".aj-stage.is-complete").count(), "active": page.locator(".aj-stage.is-active").count()})
            screenshot_view(page, "#runtime", output / "02-fourteen-gate-proof-flight-desktop.png")
            screenshot_view(page, "#coalition", output / "03-pareto-coalition-foundry-desktop.png")
            screenshot_view(page, "#proof-chronicle", output / "04-twenty-four-artifact-chronicle-desktop.png")
            screenshot_view(page, "#parliament", output / "05-validator-parliament-guardians-desktop.png")

            with page.expect_download() as json_download_info:
                page.locator("#aj-download-json").click()
            json_download = json_download_info.value
            json_path = output / "runtime-evidence-docket.json"
            json_download.save_as(str(json_path))
            downloaded = json.loads(json_path.read_text(encoding="utf-8"))
            record(results, "runtime-json-download", downloaded.get("schema") == "goalos.agi_jobs_v0_v2.evidence_docket.v3" and len(downloaded.get("proof_chronicle", {}).get("artifacts", [])) == 24, json_download.suggested_filename)
            with page.expect_download() as md_download_info:
                page.locator("#aj-download-md").click()
            md_download = md_download_info.value
            md_path = output / "runtime-executive-review-brief.md"
            md_download.save_as(str(md_path))
            brief = md_path.read_text(encoding="utf-8")
            record(results, "runtime-brief-download", "HUMAN_SETTLEMENT_REVIEW" in brief and "Live token movement: **0**" in brief and "NONE_GRANTED" in brief, md_download.suggested_filename)

            fingerprint = {"run": state["run_id"], "prime": state["coalition"]["prime"]["id"], "chain": state["chain"][-1]["commitment"]}
            page.locator("#aj-job-form").evaluate("form => form.requestSubmit()")
            page.wait_for_function("window.__AGI_JOBS_STATE__ && window.__AGI_JOBS_STATE__.running === false")
            replay = page.evaluate("() => JSON.parse(JSON.stringify(window.__AGI_JOBS_STATE__))")
            replay_fingerprint = {"run": replay["run_id"], "prime": replay["coalition"]["prime"]["id"], "chain": replay["chain"][-1]["commitment"]}
            record(results, "runtime-deterministic-replay", fingerprint == replay_fingerprint, {"first": fingerprint, "second": replay_fingerprint})

            page.locator("#aj-incident").select_option("identity-drift")
            page.locator("#aj-job-form").evaluate("form => form.requestSubmit()")
            page.wait_for_function("window.__AGI_JOBS_STATE__ && window.__AGI_JOBS_STATE__.running === false")
            held = page.evaluate("() => JSON.parse(JSON.stringify(window.__AGI_JOBS_STATE__))")
            record(results, "incident-terminal-safe-hold", held["terminal"] == "SAFE_HOLD", held["terminal"])
            record(results, "incident-quarantine-one", len(held["quarantined"]) == 1, held["quarantined"])
            record(results, "incident-validator-rejects", held["votes"]["reject"] >= 1, held["votes"]["summary"])
            record(results, "incident-guardian-veto", held["guardians"]["veto"] >= 1, held["guardians"]["summary"])
            record(results, "incident-authority-still-none", held["docket"]["terminal"]["authority"] == "NONE_GRANTED" and held["docket"]["settlement"]["live_token_movement"] is False, held["docket"]["terminal"])
            screenshot_view(page, "#runtime", output / "06-adversarial-safe-hold-desktop.png")

            page.set_content(market_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "market-title", page.title() == f"Institutional Market Atlas · {RELEASE_TITLE}", page.title())
            record(results, "market-twelve-cards", page.locator(".aj-atlas-card").count() == 12, page.locator(".aj-atlas-card").count())
            record(results, "market-sixteen-archetypes", page.locator(".aj-archetype").count() == 16, page.locator(".aj-archetype").count())
            record(results, "market-eight-invariants", page.locator("#aj-economic-invariants > article").count() == 8, page.locator("#aj-economic-invariants > article").count())
            record(results, "market-frontier-rendered", page.locator("#aj-frontier circle.point").count() == 12, page.locator("#aj-frontier circle.point").count())
            initial_leader = page.locator("#aj-market-leader").inner_text()
            page.locator("#aj-market-posture").select_option("speed-aware")
            page.wait_for_timeout(100)
            record(results, "market-interactive-posture", bool(page.locator("#aj-market-leader").inner_text()) and page.locator("#aj-market-leader").inner_text() != "—", {"before": initial_leader, "after": page.locator("#aj-market-leader").inner_text()})
            record(results, "market-desktop-no-overflow", not overflow(page)["overflow"], overflow(page))
            page.screenshot(path=str(output / "07-institutional-market-atlas-desktop.png"), full_page=False)

            page.set_content(settlement_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "settlement-title", page.title() == f"Proof Settlement Chamber · {RELEASE_TITLE}", page.title())
            record(results, "settlement-six-allocations", page.locator(".aj-settlement-card").count() == 6, page.locator(".aj-settlement-card").count())
            record(results, "settlement-contribution-ledger", page.locator(".aj-contribution-row").count() >= 4, page.locator(".aj-contribution-row").count())
            record(results, "settlement-twenty-four-ledger", page.locator(".aj-ledger-row").count() == 24, page.locator(".aj-ledger-row").count())
            record(results, "settlement-docket-v3", "goalos.agi_jobs_v0_v2.evidence_docket.v3" in page.locator("#aj-docket-json").inner_text(), "")
            page.locator("#aj-ledger-search").fill("validator")
            visible_rows = page.locator(".aj-ledger-row").count()
            record(results, "settlement-ledger-search", 0 < visible_rows < 24, page.locator("#aj-ledger-count").inner_text())
            page.locator("#aj-ledger-search").fill("")
            record(results, "settlement-desktop-no-overflow", not overflow(page)["overflow"], overflow(page))
            page.screenshot(path=str(output / "08-proof-settlement-chamber-desktop.png"), full_page=False)
            screenshot_view(page, "#aj-docket-json", output / "09-evidence-docket-desktop.png")

            page.set_content(memory_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "memory-title", page.title() == f"Capability Memory Gate · {RELEASE_TITLE}", page.title())
            record(results, "memory-eight-rules", page.locator(".aj-memory-rule").count() == 8, page.locator(".aj-memory-rule").count())
            record(results, "memory-twelve-candidates", page.locator(".aj-memory-card").count() == 12, page.locator(".aj-memory-card").count())
            record(results, "memory-five-eras", page.locator(".aj-memory-era").count() == 5, page.locator(".aj-memory-era").count())
            record(results, "memory-human-pending", page.locator(".aj-memory-card .status").all_inner_texts().count("HUMAN PENDING") == 12, page.locator(".aj-memory-card .status").all_inner_texts()[:3])
            record(results, "memory-desktop-no-overflow", not overflow(page)["overflow"], overflow(page))
            page.screenshot(path=str(output / "10-capability-memory-gate-desktop.png"), full_page=False)

            page.set_content(architecture_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "architecture-title", page.title() == f"Constitutional Architecture · {RELEASE_TITLE}", page.title())
            record(results, "architecture-fourteen-modules", page.locator(".aj-module").count() == 14, page.locator(".aj-module").count())
            record(results, "architecture-sixteen-translations", page.locator(".aj-translation-row").count() == 16, page.locator(".aj-translation-row").count())
            record(results, "architecture-ten-principles", page.locator(".aj-principle").count() == 10, page.locator(".aj-principle").count())
            record(results, "architecture-ten-threats", page.locator(".aj-threat").count() == 10, page.locator(".aj-threat").count())
            record(results, "architecture-thirty-two-fingerprints", page.locator(".aj-lineage-row").count() == 32, page.locator(".aj-lineage-row").count())
            record(results, "architecture-nine-boundaries", page.locator(".aj-claim-list li").count() == 9, page.locator(".aj-claim-list li").count())
            lineage = page.locator("#aj-lineage-root").inner_text()
            record(results, "architecture-lineage-root", len(lineage) == 64, lineage)
            record(results, "architecture-desktop-no-overflow", not overflow(page)["overflow"], overflow(page))
            page.screenshot(path=str(output / "11-constitutional-architecture-desktop.png"), full_page=False)
            screenshot_view(page, "#aj-lineage-table", output / "12-traceable-lineage-desktop.png")

            page.set_content(homepage_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            gateway = page.locator("#agi-jobs-v0-v2")
            gateway.scroll_into_view_if_needed()
            record(results, "homepage-gateway-once", gateway.count() == 1 and gateway.is_visible(), gateway.count())
            record(results, "homepage-nav-link-once", page.locator('nav a[href="agi-jobs-v0-v2.html"]').count() == 1, page.locator('nav a[href="agi-jobs-v0-v2.html"]').count())
            linked_pages = ["agi-jobs-v0-v2.html", "agi-jobs-v0-v2-market.html", "agi-jobs-v0-v2-settlement.html", "agi-jobs-v0-v2-memory.html", "agi-jobs-v0-v2-architecture.html"]
            record(results, "homepage-five-links", all(page.locator(f'#agi-jobs-v0-v2 a[href="{name}"]').count() == 1 for name in linked_pages), "")
            record(results, "homepage-gateway-copy", "Every mission becomes a market" in gateway.inner_text(), gateway.inner_text()[:260])
            record(results, "homepage-desktop-no-overflow", not overflow(page)["overflow"], overflow(page))
            gateway.screenshot(path=str(output / "13-main-website-gateway-desktop.png"))

            page.set_viewport_size({"width": 1024, "height": 1366})
            page.set_content(experience_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "experience-tablet-no-overflow", not overflow(page)["overflow"], overflow(page))
            record(results, "experience-tablet-form-visible", page.locator("#aj-job-form").is_visible(), "")
            page.screenshot(path=str(output / "14-sovereign-labor-civilization-tablet.png"), full_page=False)

            page.set_viewport_size({"width": 390, "height": 844})
            page.set_content(experience_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "experience-mobile-no-overflow", not overflow(page)["overflow"], overflow(page))
            record(results, "experience-mobile-form-visible", page.locator("#aj-job-form").is_visible(), "")
            record(results, "experience-mobile-nav-visible", page.locator(".aj-nav-links").is_visible(), "")
            page.screenshot(path=str(output / "15-sovereign-labor-civilization-mobile.png"), full_page=False)

            page.set_content(memory_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector('html[data-aj-ready="true"]')
            record(results, "memory-mobile-no-overflow", not overflow(page)["overflow"], overflow(page))
            page.screenshot(path=str(output / "16-capability-memory-mobile.png"), full_page=False)

            page.set_content(homepage_html, wait_until="domcontentloaded")
            page.evaluate("window.scrollTo(0, 0)")
            page.locator("#agi-jobs-v0-v2").scroll_into_view_if_needed()
            record(results, "homepage-mobile-no-overflow", not overflow(page)["overflow"], overflow(page))
            page.locator("#agi-jobs-v0-v2").screenshot(path=str(output / "17-main-website-gateway-mobile.png"))
            context.close()
        finally:
            browser.close()

    record(results, "browser-console-errors-zero", not console_errors, console_errors)
    record(results, "browser-failed-requests-zero", not failed_requests, failed_requests)
    record(results, "browser-external-requests-zero", not external_requests, external_requests)
    failed = [item for item in results if item["status"] == "FAIL"]
    report = {
        "schema": "goalos.agi_jobs_v0_v2.browser_qa.v3",
        "release_title": RELEASE_TITLE,
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(results),
        "checks_passed": len(results) - len(failed),
        "checks_failed": len(failed),
        "checks": results,
        "diagnostics": {"console_errors": console_errors, "failed_requests": failed_requests, "external_requests": external_requests},
    }
    write_json(output / "browser-report.json", report)
    return report


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "site")
    parser.add_argument("--output", type=Path, default=root / "site" / "qa" / "agi-jobs-v0-v2-browser")
    args = parser.parse_args()
    report = run(args.site.resolve(), args.output.resolve())
    print(json.dumps({"status": report["status"], "checks_total": report["checks_total"], "checks_passed": report["checks_passed"], "checks_failed": report["checks_failed"], "output": str(args.output / "browser-report.json")}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
