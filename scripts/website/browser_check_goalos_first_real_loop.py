#!/usr/bin/env python3
from __future__ import annotations
import argparse, contextlib, json, os, socket, threading, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PAGES = ["first-real-loop.html", "first-real-loop-architecture.html", "first-real-loop-docket.html"]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format, *_args):
        pass
    def do_GET(self):
        if self.path.split("?", 1)[0] == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()

def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def main():
    ap = argparse.ArgumentParser(description="Browser QA for GoalOS AGIALPHA Ascension First Real Loop")
    ap.add_argument("--site", default="site")
    ap.add_argument("--output", default="")
    ap.add_argument("--browser-executable", default=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE", ""))
    args = ap.parse_args()
    site = Path(args.site).resolve()
    qa = Path(args.output).resolve() if args.output else site / "qa" / "first-real-loop"
    qa.mkdir(parents=True, exist_ok=True)
    missing = [p for p in [site / "index.html", *(site / x for x in PAGES)] if not p.is_file()]
    if missing:
        raise SystemExit("Missing generated pages: " + ", ".join(map(str, missing)))

    checks, failures, console_errors, page_errors, request_failures, external_requests = [], [], [], [], [], []
    def check(condition, label, detail=""):
        row = {"label": label, "status": "PASS" if condition else "FAIL"}
        if detail:
            row["detail"] = detail
        checks.append(row)
        if not condition:
            failures.append(label + (f": {detail}" if detail else ""))

    port = free_port()
    handler = lambda *a, **kw: QuietHandler(*a, directory=str(site), **kw)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"

    try:
        with sync_playwright() as pw:
            launch = {"headless": True}
            if args.browser_executable:
                launch["executable_path"] = args.browser_executable
            browser = pw.chromium.launch(**launch)

            def context(width, height):
                ctx = browser.new_context(viewport={"width": width, "height": height}, accept_downloads=True)
                page = ctx.new_page()
                page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
                page.on("pageerror", lambda err: page_errors.append(str(err)))
                page.on("requestfailed", lambda req: request_failures.append(f"{req.method} {req.url}: {req.failure}"))
                def inspect_request(req):
                    parsed = urlparse(req.url)
                    if parsed.scheme in {"http", "https", "ws", "wss"} and parsed.hostname not in {"127.0.0.1", "localhost"}:
                        external_requests.append(req.url)
                page.on("request", inspect_request)
                return ctx, page

            ctx, page = context(1440, 1000)
            page.goto(base + "/first-real-loop.html", wait_until="networkidle")
            check(page.title() == "GoalOS AGIALPHA Ascension First Real Loop ✨", "Flagship title is exact", page.title())
            check(page.locator("h1").count() == 1, "Experience has one primary heading")
            check(page.locator("text=Where intelligence earns memory.").count() >= 1, "Flagship doctrine is visible")
            check(page.locator("#frl-run").is_visible(), "Governed-loop control is visible")
            check(page.locator(".frl-phase").count() == 8, "Eight proof phases render")
            check(page.locator("text=External actions 0").count() >= 1, "Zero-action boundary is visible")
            overflow = page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
            check(overflow, "Desktop experience has no horizontal overflow")
            page.screenshot(path=str(qa / "01-hero-desktop.png"), full_page=False)

            page.locator("#frl-run").click()
            page.wait_for_function("document.body.dataset.runState === 'complete'", timeout=15000)
            check(page.locator("#frl-runtime-state").inner_text() == "HUMAN_REVIEW_REQUIRED", "Runtime terminates at human review")
            check(page.locator(".frl-phase.is-complete").count() == 8, "All eight phases complete visibly")
            check(page.locator(".frl-event").count() >= 9, "Proof event stream records the cycle")
            check(page.locator("#frl-result").evaluate("e => e.classList.contains('is-visible')"), "Evidence-package result is revealed")
            check(page.locator("#frl-result-lift").inner_text() == "66.67%", "Bounded reuse lift is reported exactly")
            check(page.locator("#frl-result-artifacts").inner_text() == "12", "Twelve artifacts are reported")
            check("vNext" in page.locator("#frl-stage-evidence").inner_text() and "66.67%" in page.locator("#frl-stage-evidence").inner_text(), "vNext inspector presents intact evidence labels")
            runtime_id = page.locator("#frl-runtime-id").inner_text()
            check(runtime_id.startswith("RUN ") and len(runtime_id) == 16, "Deterministic runtime identifier is emitted", runtime_id)
            page.locator("#frl-result").scroll_into_view_if_needed()
            page.screenshot(path=str(qa / "02-proof-cycle-complete-desktop.png"), full_page=False)

            with page.expect_download() as dl_info:
                page.locator("#frl-download-json").click()
            download = dl_info.value
            download_path = qa / "browser-evidence-docket.json"
            download.save_as(download_path)
            downloaded = json.loads(download_path.read_text(encoding="utf-8"))
            check(downloaded["terminal"]["state"] == "HUMAN_REVIEW_REQUIRED", "Downloaded docket preserves terminal state")
            check(downloaded["terminal"]["authority"] == "NONE_GRANTED", "Downloaded docket grants no authority")
            check(downloaded["terminal"]["externalActions"] == 0, "Downloaded docket records zero external actions")
            check(downloaded["evidence"]["artifacts"] == 12, "Downloaded docket records twelve artifacts")
            check(downloaded["vNext"]["reuseLiftPercent"] == 66.67, "Downloaded docket records bounded reuse lift")

            comparison = page.locator(".frl-comparison")
            comparison.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            check(comparison.is_visible(), "Treatment/control chamber is visible")
            check(page.locator(".frl-lift strong").inner_text() == "+66.67%", "Treatment/control visual matches the docket")
            comparison.screenshot(path=str(qa / "03-treatment-control-desktop.png"))
            ctx.close()

            ctx, page = context(1440, 1000)
            page.goto(base + "/first-real-loop-architecture.html", wait_until="networkidle")
            check(page.locator("h1").count() == 1, "Architecture has one primary heading")
            check(page.locator(".frl-architecture").is_visible(), "Constitutional architecture renders")
            check(page.locator(".frl-layer").count() == 9, "Nine separated constitutional layers render")
            check(page.get_by_text("Human Promotion Boundary", exact=True).count() >= 1, "Human authority principle is explicit")
            check(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"), "Desktop architecture has no horizontal overflow")
            page.locator(".frl-reveal").evaluate_all("els => els.forEach(e => e.classList.add('is-visible'))")
            page.screenshot(path=str(qa / "04-architecture-desktop.png"), full_page=True)
            ctx.close()

            ctx, page = context(1440, 1000)
            page.goto(base + "/first-real-loop-docket.html", wait_until="networkidle")
            check(page.locator(".frl-ledger-row").count() == 12, "Evidence Docket renders twelve ledger rows")
            commitment_text = page.locator("#frl-docket-commitment").text_content().strip()
            check(commitment_text == "3d1fee22e57444bbca2cdf779b3089a265a9dc2b99539c660d21759a84a13034", "Canonical commitment renders exactly", commitment_text)
            page.locator("#frl-ledger-search").fill("falsification")
            page.wait_for_timeout(100)
            visible_rows = page.locator(".frl-ledger-row:visible").count()
            check(visible_rows == 1, "Ledger search filters deterministically", str(visible_rows))
            check(page.locator("#frl-ledger-count").inner_text() == "1 / 12 artifacts", "Ledger count updates with search")
            page.locator("#frl-ledger-search").fill("")
            page.locator(".frl-reveal").evaluate_all("els => els.forEach(e => e.classList.add('is-visible'))")
            page.screenshot(path=str(qa / "05-evidence-docket-desktop.png"), full_page=True)
            check(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"), "Desktop docket has no horizontal overflow")
            ctx.close()

            ctx, page = context(1440, 1000)
            page.goto(base + "/index.html#first-real-loop", wait_until="networkidle")
            gateway = page.locator("#first-real-loop")
            gateway.scroll_into_view_if_needed()
            page.wait_for_timeout(350)
            check(gateway.is_visible(), "Homepage gateway is visible")
            check(page.locator("#first-real-loop a[href='first-real-loop.html']").count() == 1, "Homepage gateway links to the flagship")
            check(page.locator("#first-real-loop").inner_text().count("66.67") >= 1, "Homepage gateway displays bounded lift")
            gateway.screenshot(path=str(qa / "06-homepage-gateway-desktop.png"))
            ctx.close()

            ctx, page = context(390, 844)
            page.goto(base + "/first-real-loop.html", wait_until="networkidle")
            check(page.locator("#frl-run").is_visible(), "Mobile command control is visible")
            check(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"), "Mobile experience has no horizontal overflow")
            check(page.locator(".frl-phase").count() == 8, "Mobile retains all proof phases")
            page.screenshot(path=str(qa / "07-hero-mobile.png"), full_page=False)
            page.locator("#frl-run").click()
            page.wait_for_function("document.body.dataset.runState === 'complete'", timeout=15000)
            check(page.locator("#frl-runtime-state").inner_text() == "HUMAN_REVIEW_REQUIRED", "Mobile cycle reaches human review")
            check(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"), "Mobile runtime remains overflow-free")
            page.locator("#frl-result").scroll_into_view_if_needed()
            page.screenshot(path=str(qa / "08-proof-cycle-mobile.png"), full_page=False)
            ctx.close()

            ctx, page = context(834, 1112)
            page.goto(base + "/first-real-loop-architecture.html", wait_until="networkidle")
            check(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"), "Tablet architecture has no horizontal overflow")
            check(page.locator(".frl-layer").count() == 9, "Tablet retains all constitutional layers")
            ctx.close()

            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    check(len(console_errors) == 0, "Browser console is clean", " | ".join(console_errors[:4]))
    check(len(page_errors) == 0, "No page exceptions occur", " | ".join(page_errors[:4]))
    check(len(request_failures) == 0, "No browser requests fail", " | ".join(request_failures[:4]))
    check(len(external_requests) == 0, "No external runtime requests occur", " | ".join(external_requests[:4]))

    report = {
        "status": "PASS" if not failures else "FAIL",
        "releaseId": "GOALOS-AGIALPHA-FIRST-REAL-LOOP-001",
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checks": len(checks),
        "passed": sum(x["status"] == "PASS" for x in checks),
        "failed": len(failures),
        "failures": failures,
        "consoleErrors": console_errors,
        "pageErrors": page_errors,
        "requestFailures": request_failures,
        "externalRequests": external_requests,
        "viewports": ["1440x1000", "834x1112", "390x844"],
        "screenshots": sorted(p.name for p in qa.glob("*.png")),
        "results": checks,
    }
    (qa / "browser-qa.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# GoalOS First Real Loop — Browser QA", "", f"**Status:** {report['status']}", f"**Checks:** {report['passed']}/{report['checks']} passed", "", "## Results", ""]
    lines += [f"- **{x['status']}** — {x['label']}" + (f": {x['detail']}" if x.get("detail") else "") for x in checks]
    (qa / "browser-qa.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "checks", "passed", "failed", "screenshots"]}, indent=2))
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
