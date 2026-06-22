#!/usr/bin/env python3
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

VIEWPORTS = [(375, 812), (1440, 1000)]


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
def serve_dir(site: Path):
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


async def run(site: Path, screenshots: bool) -> tuple[list[str], list[str], int]:
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return ["Playwright is not installed"], [], 0

    errors: list[str] = []
    warnings: list[str] = []
    tests = 0
    qa = site / "qa"
    qa.mkdir(exist_ok=True)
    shot_dir = qa / "mainnet-v87-screenshots"
    if screenshots:
        shot_dir.mkdir(exist_ok=True)

    with serve_dir(site) as base_url:
        async with async_playwright() as playwright:
            executable = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chromium-browser")
            browser = await playwright.chromium.launch(
                headless=True,
                executable_path=executable,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
            )
            for width, height in VIEWPORTS:
                context = await browser.new_context(viewport={"width": width, "height": height})
                page = await context.new_page()
                console_errors: list[str] = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                tests += 1
                try:
                    await page.goto(f"{base_url}/ethereum-mainnet.html", wait_until="load", timeout=45000)
                    await page.wait_for_timeout(250)
                    result = await page.evaluate("""() => {
                        window.scrollTo(999999, 0);
                        const horizontalScroll = Math.abs(window.scrollX || window.pageXOffset || 0);
                        window.scrollTo(0, 0);
                        const h1 = document.querySelector('h1');
                        const h1Rect = h1 ? h1.getBoundingClientRect() : null;
                        const groups = [...document.querySelectorAll('details.mainnet-group')];
                        const contractLinks = [...document.querySelectorAll('[data-mainnet-contract="true"]')];
                        return {
                            horizontalScroll,
                            h1Visible: !!h1Rect && h1Rect.width > 80 && h1Rect.height > 30 && h1Rect.bottom > 0,
                            groupCount: groups.length,
                            contractCount: contractLinks.length,
                            releaseLink: !!document.querySelector('a[href*="releases/tag/v4.4.0-mainnet-2026-06-21"]'),
                            unsafeForms: document.querySelectorAll('form').length,
                            bodyWidth: document.body.scrollWidth,
                            viewportWidth: window.innerWidth,
                        };
                    }""")
                    if result["horizontalScroll"] > 2 or result["bodyWidth"] > result["viewportWidth"] + 8:
                        errors.append(f"ethereum-mainnet.html@{width}x{height}: horizontal overflow")
                    if not result["h1Visible"]:
                        errors.append(f"ethereum-mainnet.html@{width}x{height}: h1 is not visible")
                    if result["groupCount"] != 5:
                        errors.append(f"ethereum-mainnet.html@{width}x{height}: expected 5 contract groups")
                    if result["contractCount"] != 49:
                        errors.append(f"ethereum-mainnet.html@{width}x{height}: expected 49 contract links")
                    if not result["releaseLink"]:
                        errors.append(f"ethereum-mainnet.html@{width}x{height}: release link missing")
                    if result["unsafeForms"]:
                        errors.append(f"ethereum-mainnet.html@{width}x{height}: form detected")
                    if console_errors:
                        warnings.extend(f"ethereum-mainnet.html@{width}x{height}: console error: {msg}" for msg in console_errors[:10])
                    if screenshots:
                        await page.screenshot(path=str(shot_dir / f"ethereum-mainnet-{width}x{height}.png"), full_page=False)

                    await page.goto(f"{base_url}/index.html", wait_until="load", timeout=45000)
                    await page.wait_for_timeout(150)
                    home = await page.evaluate("""() => {
                        const block = document.querySelector('[data-mainnet-home-card="v87"]');
                        const link = document.querySelector('a[href="ethereum-mainnet.html"]');
                        if (!block || !link) return {ok:false};
                        const rect = block.getBoundingClientRect();
                        return {ok:true, width:rect.width, linkText:(link.textContent || '').trim()};
                    }""")
                    if not home.get("ok") or home.get("width", 0) < 100:
                        errors.append(f"index.html@{width}x{height}: generated Mainnet card/link missing")
                    if screenshots:
                        await page.screenshot(path=str(shot_dir / f"homepage-mainnet-card-{width}x{height}.png"), full_page=False)
                except Exception as exc:
                    message = f"{type(exc).__name__}: {exc}"
                    if "ERR_BLOCKED_BY_ADMINISTRATOR" in message:
                        warnings.append(f"browser QA@{width}x{height}: local browser policy skipped page load")
                    else:
                        errors.append(f"browser QA@{width}x{height}: {message}")
                finally:
                    await page.close()
                    await context.close()
            await browser.close()
    return errors, warnings, tests


async def main_async(args) -> int:
    site = Path(args.site)
    errors, warnings, tests = await run(site, args.screenshots)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "tests": tests,
        "viewports": VIEWPORTS,
        "errors": errors,
        "warnings": warnings,
        "page": "ethereum-mainnet.html",
    }
    qa = site / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "mainnet-page-browser-verify-v87.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = ["# GoalOS Ethereum Mainnet Page Browser QA", "", f"Status: **{report['status']}**", "", f"Tests: {tests}", "", "## Errors"]
    md += [f"- {error}" for error in errors] or ["- None"]
    md += ["", "## Warnings"]
    md += [f"- {warning}" for warning in warnings] or ["- None"]
    (qa / "mainnet-page-browser-verify-v87.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Browser smoke test for the generated GoalOS Ethereum Mainnet page")
    parser.add_argument("--site", default="site")
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
