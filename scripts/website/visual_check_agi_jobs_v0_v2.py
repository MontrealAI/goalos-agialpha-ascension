#!/usr/bin/env python3
"""Run Chromium interaction, responsive, and adversarial QA for AGI Jobs v0 (v2)."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension AGI Jobs v0 (v2) ✨"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record(results: list[dict[str, Any]], label: str, condition: bool, detail: Any = "") -> None:
    results.append({"label": label, "status": "PASS" if condition else "FAIL", "detail": detail})


def overflow(page: Any) -> dict[str, Any]:
    return page.evaluate(
        """() => ({
          documentWidth: document.documentElement.scrollWidth,
          viewportWidth: document.documentElement.clientWidth,
          bodyWidth: document.body.scrollWidth,
          overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
        })"""
    )


def inline_feature_page(site: Path, filename: str) -> str:
    html = (site / filename).read_text(encoding="utf-8")
    css = (site / "assets" / "agi-jobs-v0-v2.css").read_text(encoding="utf-8")
    javascript = (site / "assets" / "agi-jobs-v0-v2.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    html = re.sub(r'<meta\s+http-equiv="Content-Security-Policy"[^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<link\s+[^>]*rel=[\'\"]stylesheet[\'\"][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src=[\'\"][^\'\"]+[\'\"][^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
    html = html.replace("</head>", f"<style data-qa-inline-styles>\n{css}\n</style>\n</head>", 1)
    return html.replace("</body>", f"<script>{javascript}</script>\n</body>", 1)


def inline_homepage(site: Path) -> str:
    html = (site / "index.html").read_text(encoding="utf-8")
    hrefs = re.findall(r'<link\s+[^>]*rel=[\'\"]stylesheet[\'\"][^>]*href=[\'\"]([^\'\"]+)', html, flags=re.IGNORECASE)
    css_parts: list[str] = []
    for href in hrefs:
        if href.startswith(("http://", "https://", "//")):
            continue
        path = site / href.split("?", 1)[0]
        if path.is_file():
            css_parts.append(path.read_text(encoding="utf-8"))
    html = re.sub(r'<meta\s+http-equiv="Content-Security-Policy"[^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<link\s+[^>]*rel=[\'\"]stylesheet[\'\"][^>]*>\s*', "", html, flags=re.IGNORECASE)
    html = re.sub(r'<script\s+[^>]*src=[\'\"][^\'\"]+[\'\"][^>]*>\s*</script>\s*', "", html, flags=re.IGNORECASE)
    combined_css = "\n".join(css_parts)
    return html.replace("</head>", f"<style data-qa-inline-styles>\n{combined_css}\n</style>\n</head>", 1)


def launch_browser(playwright: Any) -> Any:
    args = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
    executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or os.environ.get("CHROMIUM_PATH") or shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if executable:
        return playwright.chromium.launch(headless=True, executable_path=executable, args=args)
    return playwright.chromium.launch(headless=True, args=args)


def attach_diagnostics(page: Any, console_errors: list[str], failed_requests: list[str], external_requests: list[str]) -> None:
    page.on("console", lambda message: console_errors.append(f"{page.url}: {message.text}") if message.type == "error" else None)
    page.on("pageerror", lambda error: console_errors.append(f"{page.url}: {error}"))
    page.on("requestfailed", lambda request: failed_requests.append(f"{request.method} {request.url}: {request.failure}"))
    page.on("request", lambda request: external_requests.append(f"{request.method} {request.url}") if request.url.startswith(("http://", "https://", "ws://", "wss://")) else None)


def wait_ready(page: Any) -> None:
    page.wait_for_selector('html[data-aj-ready="true"]', timeout=20000)


def run_flight(page: Any) -> dict[str, Any]:
    page.locator("#aj-job-form").evaluate("form => form.requestSubmit()")
    page.wait_for_function("window.__AGI_JOBS_STATE__ && !window.__AGI_JOBS_STATE__.running", timeout=25000)
    return page.evaluate("() => JSON.parse(JSON.stringify(window.__AGI_JOBS_STATE__))")


def screenshot_view(page: Any, selector: str, destination: Path) -> None:
    page.locator(selector).scroll_into_view_if_needed()
    page.wait_for_timeout(100)
    page.screenshot(path=str(destination), full_page=False)


def set_page(page: Any, html: str) -> None:
    page.set_content(html, wait_until="domcontentloaded")
    wait_ready(page)


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
    proof_html = inline_feature_page(site, "agi-jobs-v0-v2-proof.html")
    settlement_html = inline_feature_page(site, "agi-jobs-v0-v2-settlement.html")
    architecture_html = inline_feature_page(site, "agi-jobs-v0-v2-architecture.html")
    homepage_html = inline_homepage(site)

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            context = browser.new_context(viewport={"width": 1600, "height": 1000}, device_scale_factor=1, reduced_motion="reduce", accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(20000)
            attach_diagnostics(page, console_errors, failed_requests, external_requests)

            set_page(page, experience_html)
            record(results, "experience-title", page.title() == RELEASE_TITLE, page.title())
            record(results, "experience-hero-visible", page.locator("#aj-hero-title").is_visible(), page.locator("#aj-hero-title").inner_text())
            record(results, "experience-five-metrics", page.locator("#aj-hero-metrics > *").count() == 5, page.locator("#aj-hero-metrics > *").count())
            record(results, "experience-seven-theses", page.locator("#aj-thesis-grid > *").count() == 7, page.locator("#aj-thesis-grid > *").count())
            record(results, "experience-eight-presets", page.locator("#aj-preset option").count() == 8, page.locator("#aj-preset option").count())
            record(results, "experience-seven-job-classes", page.locator("#aj-job-class option").count() == 7, page.locator("#aj-job-class option").count())
            record(results, "experience-five-postures", page.locator("#aj-posture option").count() == 5, page.locator("#aj-posture option").count())
            record(results, "experience-four-risk-profiles", page.locator("#aj-risk option").count() == 4, page.locator("#aj-risk option").count())
            record(results, "experience-seven-incidents", page.locator("#aj-incident option").count() == 7, page.locator("#aj-incident option").count())
            record(results, "experience-sixteen-gates", page.locator(".aj-gate").count() == 16, page.locator(".aj-gate").count())
            record(results, "experience-eight-work-packages", page.locator(".aj-work-package").count() == 8, page.locator(".aj-work-package").count())
            record(results, "experience-twenty-four-artifacts", page.locator(".aj-artifact").count() == 24, page.locator(".aj-artifact").count())
            record(results, "experience-initial-authority-none", page.locator("#aj-terminal-facts").inner_text().count("NONE_GRANTED") == 1, page.locator("#aj-terminal-facts").inner_text())
            desktop_overflow = overflow(page)
            record(results, "experience-desktop-no-overflow", not desktop_overflow["overflow"], desktop_overflow)
            page.screenshot(path=str(output / "01-work-civilization-hero-desktop.png"), full_page=False)
            record(results, "screenshot-work-civilization-hero", (output / "01-work-civilization-hero-desktop.png").is_file(), "")

            first = run_flight(page)
            docket = first["docket"]
            record(results, "runtime-terminal-human-settlement-review", docket["authority"]["terminal_state"] == "HUMAN_SETTLEMENT_REVIEW", docket["authority"]["terminal_state"])
            record(results, "runtime-council-id", docket["market"]["council"]["id"].startswith("COUNCIL-") and len(docket["market"]["council"]["id"]) == 20, docket["market"]["council"]["id"])
            record(results, "runtime-five-council-authorities", page.locator(".aj-council-role").count() == 5, page.locator(".aj-council-role").count())
            record(results, "runtime-two-reserves", len(docket["market"]["council"]["reserves"]) == 2, docket["market"]["council"]["reserves"])
            record(results, "runtime-twelve-market-rows", page.locator(".aj-market-row").count() == 12 and len(docket["market"]["ranking"]) == 12, page.locator(".aj-market-row").count())
            record(results, "runtime-pareto-frontier-present", len(docket["market"]["frontier"]) >= 1, docket["market"]["frontier"])
            record(results, "runtime-work-graph-complete", len(docket["work_graph"]) == 8 and page.locator(".aj-work-package.is-complete").count() == 8, len(docket["work_graph"]))
            record(results, "runtime-nine-validator-seats", docket["parliament"]["seats"] == 9 and page.locator(".aj-validator-seat").count() == 9, docket["parliament"]["seats"])
            record(results, "runtime-eight-pass-one-dissent", docket["parliament"]["pass"] == 8 and docket["parliament"]["dissent"] == 1 and docket["parliament"]["reject"] == 0, docket["parliament"])
            record(results, "runtime-threshold-seven", docket["parliament"]["threshold"] == 7 and page.locator("#aj-quorum").inner_text() == "8 / 7", page.locator("#aj-quorum").inner_text())
            record(results, "runtime-dissent-visible", "DISSENT" in page.locator("#aj-dissent-title").inner_text(), page.locator("#aj-dissent-title").inner_text())
            record(results, "runtime-six-guardians-clear", len(docket["guardians"]) == 6 and all(item["status"] == "CLEAR" for item in docket["guardians"]), docket["guardians"])
            record(results, "runtime-twenty-four-chain", docket["evidence"]["artifact_count"] == 24 and len(docket["evidence"]["artifacts"]) == 24, docket["evidence"]["artifact_count"])
            record(results, "runtime-chain-head-64", len(docket["evidence"]["chain_head"]) == 64, docket["evidence"]["chain_head"])
            record(results, "runtime-run-commitment-64", len(docket["run_commitment"]) == 64, docket["run_commitment"])
            record(results, "runtime-docket-schema-v3", docket["schema"] == "goalos.agi_jobs_v0_v2.evidence_docket.v3", docket["schema"])
            record(results, "runtime-zero-external-actions", docket["authority"]["external_actions"] == 0 and docket["authority"]["network_requests"] == 0, docket["authority"])
            record(results, "runtime-zero-wallet-and-token", docket["authority"]["wallet_connections"] == 0 and docket["authority"]["live_token_movements"] == 0, docket["authority"])
            record(results, "runtime-authority-none", docket["authority"]["external_authority"] == "NONE_GRANTED", docket["authority"])
            record(results, "runtime-factual-not-certified", docket["authority"]["factual_correctness"] == "NOT_CERTIFIED", docket["authority"])
            record(results, "runtime-exports-enabled", all(not page.locator(selector).is_disabled() for selector in ["#aj-download-docket", "#aj-download-brief", "#aj-copy-summary"]), "")
            screenshot_view(page, "#flight", output / "02-sixteen-gate-proof-flight-desktop.png")
            screenshot_view(page, "#market-council", output / "03-pareto-council-desktop.png")
            screenshot_view(page, "#parliament", output / "04-proof-parliament-desktop.png")
            screenshot_view(page, "#evidence", output / "05-evidence-constellation-desktop.png")
            for filename in ["02-sixteen-gate-proof-flight-desktop.png", "03-pareto-council-desktop.png", "04-proof-parliament-desktop.png", "05-evidence-constellation-desktop.png"]:
                record(results, f"screenshot:{filename}", (output / filename).is_file(), "")

            with page.expect_download() as docket_download_info:
                page.locator("#aj-download-docket").click()
            docket_download = docket_download_info.value
            docket_path = output / "runtime-evidence-docket.json"
            docket_download.save_as(str(docket_path))
            downloaded_docket = json.loads(docket_path.read_text(encoding="utf-8"))
            record(results, "runtime-json-download", downloaded_docket.get("schema") == "goalos.agi_jobs_v0_v2.evidence_docket.v3" and downloaded_docket.get("authority", {}).get("external_actions") == 0, docket_download.suggested_filename)
            with page.expect_download() as brief_download_info:
                page.locator("#aj-download-brief").click()
            brief_download = brief_download_info.value
            brief_path = output / "runtime-executive-review-brief.md"
            brief_download.save_as(str(brief_path))
            brief = brief_path.read_text(encoding="utf-8")
            record(results, "runtime-brief-download", "HUMAN_SETTLEMENT_REVIEW" in brief and "NONE_GRANTED" in brief and "Evidence artifacts: 24" in brief, brief_download.suggested_filename)

            fingerprint = {"run": docket["run_id"], "council": docket["market"]["council"]["id"], "chain": docket["evidence"]["chain_head"], "commitment": docket["run_commitment"]}
            second = run_flight(page)["docket"]
            second_fingerprint = {"run": second["run_id"], "council": second["market"]["council"]["id"], "chain": second["evidence"]["chain_head"], "commitment": second["run_commitment"]}
            record(results, "runtime-deterministic-replay", fingerprint == second_fingerprint, {"first": fingerprint, "second": second_fingerprint})

            page.locator("#aj-risk").select_option("low")
            low = run_flight(page)["docket"]
            record(results, "runtime-low-risk-three-seats", low["parliament"]["seats"] == 3 and low["parliament"]["threshold"] == 2, low["parliament"])
            record(results, "runtime-low-risk-two-pass-one-dissent", low["parliament"]["pass"] == 2 and low["parliament"]["dissent"] == 1, low["parliament"])

            page.locator("#aj-risk").select_option("critical")
            page.locator("#aj-incident").select_option("identity-drift")
            held = run_flight(page)["docket"]
            record(results, "incident-identity-terminal-safe-hold", held["authority"]["terminal_state"] == "SAFE_HOLD", held["authority"]["terminal_state"])
            record(results, "incident-identity-rejects", held["parliament"]["reject"] == 2, held["parliament"])
            record(results, "incident-identity-guardian-veto", any(item["id"] == "H01" and item["status"] == "VETO" for item in held["guardians"]), held["guardians"])
            record(results, "incident-identity-evidence-preserved", held["evidence"]["artifact_count"] == 24 and held["authority"]["external_authority"] == "NONE_GRANTED", held["authority"])
            screenshot_view(page, "#terminal", output / "06-safe-hold-desktop.png")

            page.locator("#aj-incident").select_option("budget-rupture")
            budget = run_flight(page)["docket"]
            record(results, "incident-budget-human-review", budget["authority"]["terminal_state"] == "HUMAN_REVIEW_REQUIRED", budget["authority"]["terminal_state"])
            record(results, "incident-budget-guardian-veto", any(item["id"] == "H04" and item["status"] == "VETO" for item in budget["guardians"]), budget["guardians"])

            page.locator("#aj-incident").select_option("license-conflict")
            dispute = run_flight(page)["docket"]
            record(results, "incident-rights-dispute-open", dispute["authority"]["terminal_state"] == "DISPUTE_OPEN", dispute["authority"]["terminal_state"])
            record(results, "incident-rights-two-dissents", dispute["parliament"]["dissent"] == 2, dispute["parliament"])
            record(results, "incident-rights-guardian-veto", any(item["id"] == "H03" and item["status"] == "VETO" for item in dispute["guardians"]), dispute["guardians"])

            page.locator("#aj-incident").select_option("validator-capture")
            captured = run_flight(page)["docket"]
            record(results, "incident-validator-capture-safe-hold", captured["authority"]["terminal_state"] == "SAFE_HOLD", captured["authority"]["terminal_state"])
            record(results, "incident-validator-capture-abstentions", captured["parliament"]["abstain"] >= 2 and captured["parliament"]["reject"] >= 1, captured["parliament"])
            record(results, "incident-market-guardian-veto", any(item["id"] == "H05" and item["status"] == "VETO" for item in captured["guardians"]), captured["guardians"])

            set_page(page, market_html)
            record(results, "market-title", page.title() == "AGI Jobs v0 (v2) — Guild Market", page.title())
            record(results, "market-twelve-guilds", page.locator(".aj-guild-card").count() == 12, page.locator(".aj-guild-card").count())
            record(results, "market-sixteen-archetypes", page.locator(".aj-archetype").count() == 16, page.locator(".aj-archetype").count())
            record(results, "market-twelve-ranking-rows", page.locator(".aj-market-row").count() == 12, page.locator(".aj-market-row").count())
            record(results, "market-twelve-chart-points", page.locator(".aj-chart-point").count() == 12, page.locator(".aj-chart-point").count())
            record(results, "market-five-postures", page.locator("#aj-market-posture option").count() == 5, page.locator("#aj-market-posture option").count())
            record(results, "market-seven-classes", page.locator("#aj-market-class option").count() == 7, page.locator("#aj-market-class option").count())
            record(results, "market-four-risks", page.locator("#aj-market-risk option").count() == 4, page.locator("#aj-market-risk option").count())
            initial_leader = page.locator("#aj-market-leader").inner_text()
            page.locator("#aj-market-posture").select_option("discovery-rigorous")
            page.locator("#aj-market-class").select_option("research")
            page.wait_for_timeout(100)
            changed_leader = page.locator("#aj-market-leader").inner_text()
            record(results, "market-interactive-recompute", bool(changed_leader) and changed_leader != "NONE" and page.locator("#aj-market-leader-score").inner_text() != "—", {"before": initial_leader, "after": changed_leader})
            record(results, "market-frontier-visible", "FRONTIER" in page.locator("#aj-market-frontier-label").inner_text(), page.locator("#aj-market-frontier-label").inner_text())
            market_overflow = overflow(page)
            record(results, "market-desktop-no-overflow", not market_overflow["overflow"], market_overflow)
            page.screenshot(path=str(output / "07-guild-market-desktop.png"), full_page=False)
            screenshot_view(page, ".aj-observatory-grid", output / "08-pareto-observatory-desktop.png")

            set_page(page, proof_html)
            record(results, "proof-title", page.title() == "AGI Jobs v0 (v2) — Proof Parliament", page.title())
            record(results, "proof-nine-validator-records", page.locator(".aj-proof-validator").count() == 9, page.locator(".aj-proof-validator").count())
            record(results, "proof-one-dissent-card", page.locator(".aj-proof-validator.dissent").count() == 1, page.locator(".aj-proof-validator.dissent").count())
            record(results, "proof-twenty-four-ledger-rows", page.locator(".aj-ledger-row").count() == 24, page.locator(".aj-ledger-row").count())
            record(results, "proof-ten-threats", page.locator(".aj-threat-card").count() == 10, page.locator(".aj-threat-card").count())
            record(results, "proof-sample-commitment", len(page.locator("#aj-proof-docket-head").inner_text()) == 64, page.locator("#aj-proof-docket-head").inner_text())
            record(results, "proof-docket-v3", "goalos.agi_jobs_v0_v2.evidence_docket.v3" in page.locator("#aj-docket-json").inner_text(), "")
            page.locator("#aj-ledger-search").fill("validator")
            visible_rows = page.locator(".aj-ledger-row:not(.is-hidden)").count()
            record(results, "proof-ledger-search", 0 < visible_rows < 24, {"visible": visible_rows, "label": page.locator("#aj-ledger-count").inner_text()})
            page.locator("#aj-ledger-search").fill("")
            proof_overflow = overflow(page)
            record(results, "proof-desktop-no-overflow", not proof_overflow["overflow"], proof_overflow)
            page.screenshot(path=str(output / "09-proof-parliament-desktop.png"), full_page=False)
            screenshot_view(page, ".aj-proof-docket", output / "10-evidence-docket-desktop.png")

            set_page(page, settlement_html)
            record(results, "settlement-title", page.title() == "AGI Jobs v0 (v2) — Settlement Constitution", page.title())
            record(results, "settlement-six-allocations", page.locator(".aj-settlement-allocation").count() == 6, page.locator(".aj-settlement-allocation").count())
            record(results, "settlement-six-conditions", page.locator(".aj-condition-card").count() == 6, page.locator(".aj-condition-card").count())
            record(results, "settlement-six-memory-deltas", page.locator(".aj-memory-delta").count() == 6, page.locator(".aj-memory-delta").count())
            record(results, "settlement-passport-candidate", bool(page.locator("#aj-passport-name").inner_text()) and "Candidate scope" in page.locator("#aj-passport-scope").inner_text(), page.locator("#aj-passport-scope").inner_text())
            record(results, "settlement-passport-skills", page.locator("#aj-passport-skills span").count() >= 4, page.locator("#aj-passport-skills span").count())
            page.locator("#aj-settlement-reward").fill("30000")
            page.wait_for_timeout(80)
            record(results, "settlement-interactive-total", page.locator("#aj-settlement-total").inner_text() == "30,000 αU", page.locator("#aj-settlement-total").inner_text())
            unit_sum = page.locator(".aj-settlement-allocation strong").evaluate_all("nodes => nodes.reduce((sum,node)=>sum+Number(node.textContent.replace(/[^0-9.]/g,'')),0)")
            record(results, "settlement-allocation-sum", abs(float(unit_sum) - 30000) < 0.01, unit_sum)
            settlement_overflow = overflow(page)
            record(results, "settlement-desktop-no-overflow", not settlement_overflow["overflow"], settlement_overflow)
            page.screenshot(path=str(output / "11-settlement-constitution-desktop.png"), full_page=False)
            screenshot_view(page, ".aj-memory-grid", output / "12-revocable-memory-desktop.png")

            set_page(page, architecture_html)
            record(results, "architecture-title", page.title() == "AGI Jobs v0 (v2) — Constitutional Architecture", page.title())
            record(results, "architecture-sixteen-modules", page.locator(".aj-module-card").count() == 16, page.locator(".aj-module-card").count())
            record(results, "architecture-sixteen-translations", page.locator(".aj-translation-row").count() == 16, page.locator(".aj-translation-row").count())
            record(results, "architecture-ten-principles", page.locator(".aj-principle-card").count() == 10, page.locator(".aj-principle-card").count())
            record(results, "architecture-ten-threats", page.locator(".aj-threat-arch-card").count() == 10, page.locator(".aj-threat-arch-card").count())
            record(results, "architecture-thirty-two-fingerprints", page.locator(".aj-lineage-row").count() == 32, page.locator(".aj-lineage-row").count())
            record(results, "architecture-six-mainnet-cards", page.locator("#aj-mainnet-context > div").count() == 6, page.locator("#aj-mainnet-context > div").count())
            record(results, "architecture-ten-claim-boundaries", page.locator("#aj-claim-list li").count() == 10, page.locator("#aj-claim-list li").count())
            lineage_root = page.locator("#aj-lineage-root").inner_text()
            record(results, "architecture-lineage-root", len(lineage_root) == 64 and lineage_root == "71663cf756cad1347f71a70e1f9cf6071101ab3f494def62e13d268a9066f6fd", lineage_root)
            architecture_overflow = overflow(page)
            record(results, "architecture-desktop-no-overflow", not architecture_overflow["overflow"], architecture_overflow)
            page.screenshot(path=str(output / "13-constitutional-architecture-desktop.png"), full_page=False)
            screenshot_view(page, "#aj-lineage-table", output / "14-source-lineage-desktop.png")

            page.set_content(homepage_html, wait_until="domcontentloaded")
            gateway = page.locator("#agi-jobs-v0-v2")
            gateway.scroll_into_view_if_needed()
            record(results, "homepage-gateway-once", gateway.count() == 1 and gateway.is_visible(), gateway.count())
            record(results, "homepage-nav-link-once", page.locator('a[href="agi-jobs-v0-v2.html"]', has_text="AGI Jobs").count() == 1, page.locator('a[href="agi-jobs-v0-v2.html"]', has_text="AGI Jobs").count())
            record(results, "homepage-five-feature-links", all(page.locator(f'#agi-jobs-v0-v2 a[href="{name}"]').count() == 1 for name in ["agi-jobs-v0-v2.html", "agi-jobs-v0-v2-market.html", "agi-jobs-v0-v2-proof.html", "agi-jobs-v0-v2-settlement.html", "agi-jobs-v0-v2-architecture.html"]), "")
            record(results, "homepage-flagship-copy", "A market of minds" in gateway.inner_text() and "THE WORK" in gateway.inner_text() and "CIVILIZATION" in gateway.inner_text(), gateway.inner_text()[:260])
            record(results, "homepage-four-counts", page.locator(".aj-home-stat").count() == 4, page.locator(".aj-home-stat").count())
            record(results, "homepage-monument", page.locator(".aj-home-monument").is_visible() and page.locator(".aj-home-node").count() == 5, page.locator(".aj-home-node").count())
            home_overflow = overflow(page)
            record(results, "homepage-desktop-no-overflow", not home_overflow["overflow"], home_overflow)
            gateway.screenshot(path=str(output / "15-main-website-gateway-desktop.png"))

            page.set_viewport_size({"width": 1024, "height": 1366})
            set_page(page, experience_html)
            tablet_overflow = overflow(page)
            record(results, "experience-tablet-no-overflow", not tablet_overflow["overflow"], tablet_overflow)
            record(results, "experience-tablet-form-visible", page.locator("#aj-job-form").is_visible(), "")
            record(results, "experience-tablet-seal-visible", page.locator(".aj-civilization-seal").is_visible(), "")
            page.screenshot(path=str(output / "16-work-civilization-tablet.png"), full_page=False)

            page.set_viewport_size({"width": 390, "height": 844})
            set_page(page, experience_html)
            mobile_overflow = overflow(page)
            record(results, "experience-mobile-no-overflow", not mobile_overflow["overflow"], mobile_overflow)
            record(results, "experience-mobile-form-visible", page.locator("#aj-job-form").is_visible(), "")
            record(results, "experience-mobile-nav-visible", page.locator(".aj-nav-links").is_visible(), "")
            record(results, "experience-mobile-terminal-visible", page.locator("#aj-terminal-state").is_visible(), "")
            page.screenshot(path=str(output / "17-work-civilization-mobile.png"), full_page=False)

            page.set_content(homepage_html, wait_until="domcontentloaded")
            mobile_gateway = page.locator("#agi-jobs-v0-v2")
            mobile_gateway.scroll_into_view_if_needed()
            mobile_home_overflow = overflow(page)
            record(results, "homepage-mobile-no-overflow", not mobile_home_overflow["overflow"], mobile_home_overflow)
            record(results, "homepage-mobile-gateway-visible", mobile_gateway.is_visible(), "")
            mobile_gateway.screenshot(path=str(output / "18-main-website-gateway-mobile.png"))
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
    print(json.dumps({"status": report["status"], "checks_total": report["checks_total"], "checks_passed": report["checks_passed"], "checks_failed": report["checks_failed"], "output": str(args.output / 'browser-report.json')}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
