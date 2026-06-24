#!/usr/bin/env python3
"""Run Chromium interaction, adversarial, responsive, and visual QA for the Sovereign Machine Economy."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

RELEASE_TITLE = "GoalOS AGIALPHA Ascension Sovereign Machine Economy 👁️⚡️✨"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record(results: list[dict[str, Any]], label: str, condition: bool, detail: Any = "") -> None:
    results.append({"label":label,"status":"PASS" if condition else "FAIL","detail":detail})


def overflow(page: Any) -> dict[str, Any]:
    return page.evaluate("""() => ({documentWidth:document.documentElement.scrollWidth,viewportWidth:document.documentElement.clientWidth,bodyWidth:document.body.scrollWidth,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2})""")


def inline_page(site: Path, filename: str) -> str:
    html = (site / filename).read_text(encoding="utf-8")
    css = (site / "assets/sovereign-machine-economy.css").read_text(encoding="utf-8")
    javascript = (site / "assets/sovereign-machine-economy.js").read_text(encoding="utf-8").replace("</script", "<" + "\\/script")
    html = re.sub(r'<meta\s+http-equiv="Content-Security-Policy"[^>]*>\s*', "", html, flags=re.I)
    html = re.sub(r'<link\s+[^>]*rel="stylesheet"[^>]*>\s*', "", html, flags=re.I)
    html = re.sub(r'<script\s+[^>]*src="[^"]+"[^>]*>\s*</script>\s*', "", html, flags=re.I)
    html = html.replace("</head>", f"<style data-qa-inline-styles>\n{css}\n</style>\n</head>", 1)
    return html.replace("</body>", f"<script>{javascript}</script>\n</body>", 1)


def inline_homepage(site: Path) -> str:
    html = (site / "index.html").read_text(encoding="utf-8")
    hrefs = re.findall(r'<link\s+[^>]*rel=[\'\"]stylesheet[\'\"][^>]*href=[\'\"]([^\'\"]+)', html, flags=re.I)
    css_parts: list[str] = []
    for href in hrefs:
        if href.startswith(("http://","https://","//")): continue
        path = site / href.split("?",1)[0]
        if path.is_file(): css_parts.append(path.read_text(encoding="utf-8"))
    html = re.sub(r'<link\s+[^>]*rel=[\'\"]stylesheet[\'\"][^>]*>\s*', "", html, flags=re.I)
    html = re.sub(r'<script\s+[^>]*src=[\'\"][^\'\"]+[\'\"][^>]*>\s*</script>\s*', "", html, flags=re.I)
    combined_css = "\n".join(css_parts)
    return html.replace("</head>", f"<style data-qa-inline-styles>\n{combined_css}\n</style>\n</head>", 1)


def launch_browser(playwright: Any) -> Any:
    args = ["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"]
    executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or os.environ.get("CHROMIUM_PATH") or shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if executable: return playwright.chromium.launch(headless=True, executable_path=executable, args=args)
    return playwright.chromium.launch(headless=True, args=args)


def attach(page: Any, console_errors: list[str], external_requests: list[str], failed_requests: list[str]) -> None:
    page.on("console", lambda message: console_errors.append(f"{page.url}: {message.text}") if message.type == "error" else None)
    page.on("pageerror", lambda error: console_errors.append(f"{page.url}: {error}"))
    page.on("request", lambda request: external_requests.append(f"{request.method} {request.url}") if request.url.startswith(("http://","https://","ws://","wss://")) else None)
    page.on("requestfailed", lambda request: failed_requests.append(f"{request.method} {request.url}: {request.failure}"))


def wait_ready(page: Any) -> None:
    page.wait_for_selector('html[data-sme-ready="true"]', timeout=20000)


def launch_cycle(page: Any) -> dict[str, Any]:
    page.locator("#sme-mission-form").evaluate("form => form.requestSubmit()")
    page.wait_for_function("window.__SME_STATE__ && !window.__SME_STATE__.running && window.__SME_STATE__.docket", timeout=25000)
    return page.evaluate("() => JSON.parse(JSON.stringify(window.__SME_STATE__))")


def screenshot_view(page: Any, selector: str, destination: Path) -> None:
    page.locator(selector).scroll_into_view_if_needed(); page.wait_for_timeout(100); page.screenshot(path=str(destination), full_page=False)


def run(site: Path, output: Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        report={"schema":"goalos.sovereign_machine_economy.browser_qa.v2","status":"FAIL","checks_total":1,"checks_passed":0,"checks_failed":1,"checks":[{"label":"playwright-import","status":"FAIL","detail":str(exc)}]}
        write_json(output/"browser-report.json",report); return report
    output.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]]=[]; console_errors: list[str]=[]; external_requests: list[str]=[]; failed_requests: list[str]=[]
    experience=inline_page(site,"sovereign-machine-economy.html")
    observatory=inline_page(site,"sovereign-machine-economy-observatory.html")
    architecture=inline_page(site,"sovereign-machine-economy-architecture.html")
    ledger=inline_page(site,"sovereign-machine-economy-ledger.html")
    memory=inline_page(site,"sovereign-machine-economy-memory.html")
    passport=inline_page(site,"sovereign-machine-economy-passport.html")
    homepage=inline_homepage(site)
    with sync_playwright() as playwright:
        browser=launch_browser(playwright)
        try:
            context=browser.new_context(viewport={"width":1600,"height":1000},device_scale_factor=1,reduced_motion="reduce",accept_downloads=True)
            page=context.new_page(); page.set_default_timeout(18000); attach(page,console_errors,external_requests,failed_requests)
            page.set_content(experience,wait_until="domcontentloaded"); wait_ready(page)
            record(results,"experience-load",page.title()==RELEASE_TITLE,page.title())
            record(results,"experience-hero-visible",page.locator("#sme-hero-title").is_visible(),page.locator("#sme-hero-title").inner_text())
            record(results,"experience-six-metrics",page.locator("#sme-hero-metrics .sme-metric").count()==6,page.locator("#sme-hero-metrics .sme-metric").count())
            record(results,"experience-three-engines",page.locator("#sme-source-releases .sme-source-card").count()==3,page.locator("#sme-source-releases .sme-source-card").count())
            record(results,"experience-twenty-one-gates",page.locator("#sme-gate-rail .sme-gate").count()==21,page.locator("#sme-gate-rail .sme-gate").count())
            record(results,"experience-fifteen-handoffs",page.locator("#sme-handoff-grid .sme-handoff-card").count()==15,page.locator("#sme-handoff-grid .sme-handoff-card").count())
            record(results,"experience-three-universes",page.locator("#sme-universe-preview .sme-universe-card").count()==3,page.locator("#sme-universe-preview .sme-universe-card").count())
            record(results,"experience-four-review-actions",page.locator("#sme-review-actions button").count()==4,page.locator("#sme-review-actions button").count())
            record(results,"experience-six-boundaries",page.locator("#sme-boundary-grid .sme-boundary-card").count()==6,page.locator("#sme-boundary-grid .sme-boundary-card").count())
            record(results,"experience-form-visible",page.locator("#sme-mission-form").is_visible(),"")
            desktop=overflow(page); record(results,"experience-desktop-no-overflow",not desktop["overflow"],desktop)
            page.screenshot(path=str(output/"01-sovereign-machine-economy-hero-desktop.png"),full_page=False)
            normal=launch_cycle(page)
            record(results,"runtime-terminal-human-settlement-review",normal["terminal"]=="HUMAN_SETTLEMENT_REVIEW",normal["terminal"])
            record(results,"runtime-three-engines",bool(normal["institution"]) and bool(normal["node"]) and bool(normal["market"]),{"institution":normal["institution"]["id"],"node":normal["node"]["id"],"market":normal["market"]["id"]})
            record(results,"runtime-six-roles",len(normal["institution"]["roles"])==6,len(normal["institution"]["roles"]))
            record(results,"runtime-primary-route-four",len(normal["node"]["primary"])==4,len(normal["node"]["primary"]))
            record(results,"runtime-shadow-route-three",len(normal["node"]["shadow"])==3,len(normal["node"]["shadow"]))
            record(results,"runtime-coalition-six",len(normal["market"]["coalition"])==6,len(normal["market"]["coalition"]))
            record(results,"runtime-parliament-seven",normal["market"]["parliament"]["seats"]==7,normal["market"]["parliament"])
            record(results,"runtime-dissent-one",normal["market"]["parliament"]["dissent"]==1,normal["market"]["parliament"])
            dissenting=[item for item in normal["market"]["parliament"]["opinions"] if item["verdict"]=="DISSENT"]
            record(results,"runtime-independent-dissent-seat",len(dissenting)==1 and (str(dissenting[0].get("id","")).upper()=="V09" or "independent dissent" in str(dissenting[0].get("name","")).lower()),dissenting)
            record(results,"runtime-fifteen-handoffs",len(normal["handoffs"])==15,len(normal["handoffs"]))
            record(results,"runtime-forty-eight-artifacts",len(normal["artifacts"])==48,len(normal["artifacts"]))
            record(results,"runtime-economy-root",len(normal["docket"]["economy_root"])==64,normal["docket"]["economy_root"])
            record(results,"runtime-authority-none",normal["docket"]["authority"]["external_authority"]=="NONE_GRANTED",normal["docket"]["authority"])
            record(results,"runtime-zero-external-actions",normal["docket"]["authority"]["external_actions"]==0,normal["docket"]["authority"])
            record(results,"runtime-memory-human",normal["memory"]["status"]=="HUMAN_PROMOTION_REQUIRED" and normal["memory"]["automatic_promotion"] is False,normal["memory"])
            record(results,"runtime-three-counterfactuals",len(normal["docket"]["counterfactuals"])==3,len(normal["docket"]["counterfactuals"]))
            record(results,"runtime-review-pending",normal["docket"]["review"]["status"]=="PENDING_HUMAN_REVIEW",normal["docket"]["review"])
            record(results,"runtime-review-no-authority",normal["docket"]["review"]["authority_granted"] is False and normal["docket"]["review"]["settlement_authorized"] is False and normal["docket"]["review"]["memory_promoted"] is False,normal["docket"]["review"])
            record(results,"runtime-gates-complete",page.locator(".sme-gate.is-complete").count()>=20,page.locator(".sme-gate.is-complete").count())
            record(results,"runtime-downloads-enabled",all(not page.locator(f"#{item}").is_disabled() for item in ["sme-download-json","sme-download-md","sme-copy-summary"]),"")
            screenshot_view(page,"#mission-theatre",output/"02-constitutional-mission-theatre-desktop.png")
            screenshot_view(page,"#handoff-ledger",output/"03-interinstitutional-handoff-ledger-desktop.png")
            with page.expect_download() as info:
                page.locator("#sme-download-json").click()
            json_download=info.value; json_path=output/"runtime-sovereign-machine-economy-docket.json"; json_download.save_as(str(json_path)); downloaded=json.loads(json_path.read_text(encoding="utf-8"))
            record(results,"runtime-json-download",downloaded.get("schema")=="goalos.sovereign_machine_economy.docket.v2" and downloaded.get("evidence",{}).get("artifact_count")==48 and len(downloaded.get("counterfactuals",[]))==3,json_download.suggested_filename)
            with page.expect_download() as info:
                page.locator("#sme-download-md").click()
            md_download=info.value; md_path=output/"runtime-sovereign-machine-economy-brief.md"; md_download.save_as(str(md_path)); brief=md_path.read_text(encoding="utf-8")
            record(results,"runtime-brief-download","HUMAN_SETTLEMENT_REVIEW" in brief and "External actions: 0" in brief and "NONE_GRANTED" in brief,md_download.suggested_filename)
            page.locator('button[data-review-action="approve-deliberation"]').click()
            reviewed=page.evaluate("() => JSON.parse(JSON.stringify(window.__SME_STATE__))")
            record(results,"review-chamber-approval-recorded",reviewed["docket"]["review"]["status"]=="APPROVED_FOR_DELIBERATION" and len(reviewed["docket"]["review"]["record"])==64,reviewed["docket"]["review"])
            record(results,"review-chamber-authority-still-withheld",reviewed["docket"]["review"]["authority_granted"] is False and reviewed["docket"]["authority"]["external_authority"]=="NONE_GRANTED",reviewed["docket"]["authority"])
            screenshot_view(page,"#sme-review-chamber",output/"03-human-review-chamber-desktop.png")
            fingerprint={"institution":normal["institution"]["id"],"route":normal["node"]["route_id"],"coalition":normal["market"]["coalition_id"],"root":normal["docket"]["economy_root"]}
            page.locator("#sme-reset").click(); replay=launch_cycle(page); fingerprint2={"institution":replay["institution"]["id"],"route":replay["node"]["route_id"],"coalition":replay["market"]["coalition_id"],"root":replay["docket"]["economy_root"]}
            record(results,"runtime-deterministic-replay",fingerprint==fingerprint2,{"first":fingerprint,"second":fingerprint2})
            page.locator("#sme-reset").click(); page.locator("#sme-incident").select_option("identity-drift"); held=launch_cycle(page)
            record(results,"incident-identity-safe-hold",held["terminal"]=="SAFE_HOLD",held["terminal"])
            record(results,"incident-identity-authority-none",held["docket"]["authority"]["external_authority"]=="NONE_GRANTED",held["docket"]["authority"])
            screenshot_view(page,"#mission-theatre",output/"04-adversarial-safe-hold-desktop.png")
            page.locator("#sme-reset").click(); page.locator("#sme-incident").select_option("rights-conflict"); dispute=launch_cycle(page)
            record(results,"incident-rights-dispute-open",dispute["terminal"]=="DISPUTE_OPEN",dispute["terminal"])
            page.locator("#sme-reset").click(); page.locator("#sme-incident").select_option("budget-rupture"); review=launch_cycle(page)
            record(results,"incident-budget-human-review",review["terminal"]=="HUMAN_REVIEW_REQUIRED",review["terminal"])

            page.set_content(architecture,wait_until="domcontentloaded"); wait_ready(page)
            record(results,"architecture-load",page.title()=="Sovereign Machine Economy Ω — Constitutional Architecture",page.title())
            record(results,"architecture-six-layers",page.locator("#sme-architecture-stack .sme-stack-layer").count()==6,page.locator("#sme-architecture-stack .sme-stack-layer").count())
            record(results,"architecture-twenty-one-gates",page.locator("#sme-architecture-gates > li").count()==21,page.locator("#sme-architecture-gates > li").count())
            record(results,"architecture-eight-rights",page.locator("#sme-rights-grid .sme-right-card").count()==8,page.locator("#sme-rights-grid .sme-right-card").count())
            record(results,"architecture-ten-threats",page.locator("#sme-threat-grid .sme-threat-card").count()==10,page.locator("#sme-threat-grid .sme-threat-card").count())
            record(results,"architecture-fifteen-fingerprints",page.locator("#sme-lineage-table .sme-lineage-row").count()==15,page.locator("#sme-lineage-table .sme-lineage-row").count())
            lineage_root=page.locator("#sme-lineage-root").inner_text(); record(results,"architecture-lineage-root",lineage_root.startswith("root ") and len(lineage_root.split()[-1])==64,lineage_root)
            arch_overflow=overflow(page); record(results,"architecture-desktop-no-overflow",not arch_overflow["overflow"],arch_overflow)
            page.screenshot(path=str(output/"05-three-engine-constitution-desktop.png"),full_page=False); screenshot_view(page,"#sme-threat-grid",output/"06-threat-constitution-desktop.png")

            page.set_content(ledger,wait_until="domcontentloaded"); wait_ready(page)
            record(results,"ledger-load",page.title()=="Sovereign Machine Economy Ω — Proof Chronicle",page.title())
            record(results,"ledger-fifteen-handoffs",page.locator("#sme-ledger-handoffs .sme-ledger-handoff").count()==15,page.locator("#sme-ledger-handoffs .sme-ledger-handoff").count())
            record(results,"ledger-forty-eight-artifacts",page.locator("#sme-artifact-ledger .sme-artifact-row").count()==48,page.locator("#sme-artifact-ledger .sme-artifact-row").count())
            page.locator("#sme-ledger-search").fill("NODE"); record(results,"ledger-search-node",0<page.locator("#sme-artifact-ledger .sme-artifact-row").count()<48,page.locator("#sme-artifact-ledger .sme-artifact-row").count()); page.locator("#sme-ledger-search").fill("")
            sample=json.loads(page.locator("#sme-sample-json").inner_text()); record(results,"ledger-sample-schema",sample.get("schema")=="goalos.sovereign_machine_economy.docket.v2",sample.get("schema"))
            ledger_overflow=overflow(page); record(results,"ledger-desktop-no-overflow",not ledger_overflow["overflow"],ledger_overflow)
            page.screenshot(path=str(output/"08-proof-chronicle-hero-desktop.png"),full_page=False); screenshot_view(page,"#sme-artifact-ledger",output/"09-forty-eight-artifact-chain-desktop.png")

            page.set_content(memory,wait_until="domcontentloaded"); wait_ready(page)
            record(results,"memory-load",page.title()=="Sovereign Machine Economy Ω — Recursive Capability Memory",page.title())
            record(results,"memory-six-cycle-steps",page.locator("#sme-memory-cycle .sme-memory-step").count()==6,page.locator("#sme-memory-cycle .sme-memory-step").count())
            record(results,"memory-nine-rules",page.locator("#sme-memory-rules .sme-memory-rule").count()==9,page.locator("#sme-memory-rules .sme-memory-rule").count())
            record(results,"memory-nine-tribunal-questions",page.locator("#sme-tribunal .sme-tribunal-card").count()==9,page.locator("#sme-tribunal .sme-tribunal-card").count())
            record(results,"memory-human-promotion-copy","HUMAN PROMOTION REQUIRED" in page.locator(".sme-terminal-banner").inner_text(),page.locator(".sme-terminal-banner").inner_text())
            memory_overflow=overflow(page); record(results,"memory-desktop-no-overflow",not memory_overflow["overflow"],memory_overflow)
            page.screenshot(path=str(output/"10-recursive-capability-memory-desktop.png"),full_page=False)

            page.set_content(observatory,wait_until="domcontentloaded"); wait_ready(page)
            record(results,"observatory-load",page.title()=="Sovereign Machine Economy Ω — Counterfactual Observatory",page.title())
            record(results,"observatory-three-universes",page.locator("#sme-universe-grid .sme-universe-result").count()==3,page.locator("#sme-universe-grid .sme-universe-result").count())
            record(results,"observatory-four-invariants",page.locator("#sme-invariant-grid .sme-invariant-card").count()==4,page.locator("#sme-invariant-grid .sme-invariant-card").count())
            record(results,"observatory-comparison-rows",page.locator("#sme-comparison-table .sme-comparison-row").count()==8,page.locator("#sme-comparison-table .sme-comparison-row").count())
            universes=page.evaluate("() => JSON.parse(JSON.stringify(window.__SME_UNIVERSES__))")
            record(results,"observatory-authority-invariant",len(universes)==3 and all(item["authority"]=="NONE_GRANTED" for item in universes),universes)
            obs_overflow=overflow(page);record(results,"observatory-desktop-no-overflow",not obs_overflow["overflow"],obs_overflow)
            page.screenshot(path=str(output/"11-counterfactual-observatory-desktop.png"),full_page=False)

            page.set_content(passport,wait_until="domcontentloaded"); wait_ready(page)
            record(results,"passport-load",page.title()=="Sovereign Machine Economy Ω — Mission Passport",page.title())
            record(results,"passport-256-pixels",page.locator("#sme-passport-glyph .sme-passport-pixel").count()==256,page.locator("#sme-passport-glyph .sme-passport-pixel").count())
            record(results,"passport-eight-fields",page.locator("#sme-passport-fields .sme-passport-field").count()==8,page.locator("#sme-passport-fields .sme-passport-field").count())
            record(results,"passport-three-engines",page.locator("#sme-passport-engines .sme-passport-engine").count()==3,page.locator("#sme-passport-engines .sme-passport-engine").count())
            record(results,"passport-five-chain-cards",page.locator("#sme-passport-chain .sme-passport-chain-card").count()==5,page.locator("#sme-passport-chain .sme-passport-chain-card").count())
            record(results,"passport-four-interpretations",page.locator("#sme-passport-interpretation .sme-interpretation-card").count()==4,page.locator("#sme-passport-interpretation .sme-interpretation-card").count())
            record(results,"passport-human-state",page.locator("#sme-passport-state").inner_text()=="HUMAN_SETTLEMENT_REVIEW",page.locator("#sme-passport-state").inner_text())
            passport_overflow=overflow(page);record(results,"passport-desktop-no-overflow",not passport_overflow["overflow"],passport_overflow)
            page.screenshot(path=str(output/"12-mission-passport-desktop.png"),full_page=False)

            page.set_content(homepage,wait_until="domcontentloaded")
            gateway=page.locator("#sovereign-machine-economy"); gateway.scroll_into_view_if_needed()
            record(results,"homepage-gateway-once",gateway.count()==1 and gateway.is_visible(),gateway.count())
            record(results,"homepage-nav-link-once",page.locator('header.top nav.nav a[href="sovereign-machine-economy.html"]',has_text="Machine Economy Ω").count()==1,page.locator('header.top nav.nav a[href="sovereign-machine-economy.html"]',has_text="Machine Economy Ω").count())
            record(results,"homepage-three-engines",gateway.locator(".sme-home-engine").count()==3,gateway.locator(".sme-home-engine").count())
            record(results,"homepage-copy","A mind that builds minds" in gateway.inner_text() and "accountable value" in gateway.inner_text(),gateway.inner_text()[:220])
            home_overflow=overflow(page); record(results,"homepage-desktop-no-overflow",not home_overflow["overflow"],home_overflow)
            gateway.screenshot(path=str(output/"13-main-website-machine-economy-gateway-desktop.png"))

            page.set_viewport_size({"width":1024,"height":1366}); page.set_content(experience,wait_until="domcontentloaded"); wait_ready(page)
            tablet=overflow(page); record(results,"experience-tablet-no-overflow",not tablet["overflow"],tablet); record(results,"experience-tablet-form-visible",page.locator("#sme-mission-form").is_visible(),""); page.screenshot(path=str(output/"14-sovereign-machine-economy-tablet.png"),full_page=False)
            page.set_viewport_size({"width":390,"height":844}); page.set_content(experience,wait_until="domcontentloaded"); wait_ready(page)
            mobile=overflow(page); record(results,"experience-mobile-no-overflow",not mobile["overflow"],mobile); record(results,"experience-mobile-hero-visible",page.locator("#sme-hero-title").is_visible(),""); record(results,"experience-mobile-form-visible",page.locator("#sme-mission-form").is_visible(),""); page.screenshot(path=str(output/"15-sovereign-machine-economy-mobile.png"),full_page=False)
            page.set_content(ledger,wait_until="domcontentloaded"); wait_ready(page); ledger_mobile=overflow(page); record(results,"ledger-mobile-no-overflow",not ledger_mobile["overflow"],ledger_mobile)
            page.set_content(memory,wait_until="domcontentloaded"); wait_ready(page); memory_mobile=overflow(page); record(results,"memory-mobile-no-overflow",not memory_mobile["overflow"],memory_mobile)
            page.set_content(observatory,wait_until="domcontentloaded"); wait_ready(page); observatory_mobile=overflow(page); record(results,"observatory-mobile-no-overflow",not observatory_mobile["overflow"],observatory_mobile)
            page.set_content(passport,wait_until="domcontentloaded"); wait_ready(page); passport_mobile=overflow(page); record(results,"passport-mobile-no-overflow",not passport_mobile["overflow"],passport_mobile)
            context.close()
        finally:
            browser.close()
    record(results,"console-errors-zero",not console_errors,console_errors)
    record(results,"external-requests-zero",not external_requests,external_requests)
    record(results,"failed-requests-zero",not failed_requests,failed_requests)
    failed=[item for item in results if item["status"]=="FAIL"]
    report={"schema":"goalos.sovereign_machine_economy.browser_qa.v2","release_title":RELEASE_TITLE,"status":"PASS" if not failed else "FAIL","checks_total":len(results),"checks_passed":len(results)-len(failed),"checks_failed":len(failed),"checks":results,"console_errors":console_errors,"external_requests":external_requests,"failed_requests":failed_requests}
    write_json(output/"browser-report.json",report); print(json.dumps({"status":report["status"],"checks_total":report["checks_total"],"checks_passed":report["checks_passed"],"checks_failed":report["checks_failed"],"output":str(output/"browser-report.json")},indent=2)); return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--site",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args(); report=run(args.site.resolve(),args.output.resolve()); return 0 if report["status"]=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
