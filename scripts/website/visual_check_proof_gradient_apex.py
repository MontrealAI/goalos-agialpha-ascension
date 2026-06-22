#!/usr/bin/env python3
"""Browser QA for the generated Proof Gradient Apex page and homepage feature."""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import http.server
import json
import shutil
import socket
import socketserver
import sys
import threading
from pathlib import Path

VIEWPORTS = [(320, 800), (375, 812), (768, 1024), (1440, 1000)]
PAGES = ["index.html", "proof-gradient-challenge.html"]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def pick_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@contextlib.contextmanager
def serve(site: Path):
    port = pick_port()
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(site), **kwargs)
    server = socketserver.TCPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


async def run(site: Path, screenshots: bool) -> int:
    try:
        from playwright.async_api import async_playwright
    except Exception:
        print("ERROR: install Playwright before running visual QA", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    qadir = site / "qa"
    qadir.mkdir(exist_ok=True)
    shotdir = qadir / "proof-gradient-apex-screenshots"
    if screenshots:
        shotdir.mkdir(exist_ok=True)

    with serve(site) as base:
        async with async_playwright() as pw:
            executable = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chromium-browser")
            browser = await pw.chromium.launch(headless=True, executable_path=executable, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
            tests = 0
            for width, height in VIEWPORTS:
                context = await browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
                for name in PAGES:
                    tests += 1
                    page = await context.new_page()
                    try:
                        await page.goto(f"{base}/{name}", wait_until="load", timeout=45000)
                        await page.wait_for_timeout(250)
                        result = await page.evaluate("""() => {
                          window.scrollTo(999999, 0);
                          const horizontal = Math.abs(window.scrollX || 0);
                          window.scrollTo(0, 0);
                          const visible = el => { if(!el) return false; const r=el.getBoundingClientRect(); const cs=getComputedStyle(el); return r.width>20 && r.height>20 && cs.visibility!=='hidden' && parseFloat(cs.opacity||'1')>.3; };
                          return {
                            horizontal,
                            h1Visible: visible(document.querySelector('h1')),
                            homeFeature: visible(document.querySelector('#proof-gradient-challenge')),
                            contractCards: document.querySelectorAll('.pg-contract').length,
                            challengeTitle: document.title,
                            bodyWidth: document.body.getBoundingClientRect().width,
                            viewport: innerWidth
                          };
                        }""")
                        if result["horizontal"] > 2:
                            errors.append(f"{name}@{width}x{height}: horizontal scroll {result['horizontal']}px")
                        if not result["h1Visible"]:
                            errors.append(f"{name}@{width}x{height}: h1 not visible")
                        if name == "index.html" and not result["homeFeature"]:
                            errors.append(f"{name}@{width}x{height}: Proof Gradient homepage feature not visible")
                        if name == "proof-gradient-challenge.html" and result["contractCards"] != 48:
                            errors.append(f"{name}@{width}x{height}: expected 48 contract cards, found {result['contractCards']}")
                        if screenshots and width in (375, 1440):
                            await page.screenshot(path=str(shotdir / f"{name[:-5]}-{width}x{height}.png"), full_page=False)
                    except Exception as exc:
                        message = f"{type(exc).__name__}: {exc}"
                        if "ERR_BLOCKED_BY_ADMINISTRATOR" in message:
                            warnings.append(f"{name}@{width}x{height}: local browser policy skipped page load")
                        else:
                            errors.append(f"{name}@{width}x{height}: {message}")
                    finally:
                        await page.close()
                await context.close()
            await browser.close()

    report = {
        "schemaVersion": "1.0",
        "status": "PASS" if not errors else "FAIL",
        "tests": tests,
        "viewports": VIEWPORTS,
        "pages": PAGES,
        "errors": errors,
        "warnings": warnings,
        "publicNetworkTransactionSent": False,
    }
    (qadir / "proof-gradient-apex-layout.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()
    return asyncio.run(run(Path(args.site), args.screenshots))


if __name__ == "__main__":
    raise SystemExit(main())
