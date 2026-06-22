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
MIN_CONTRAST = 4.5
MIN_CONTROL_HEIGHT = 44


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


AUDIT = r"""
() => {
  const parseColor = value => {
    const match = String(value || '').match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,\/]\s*([\d.]+))?\s*\)/i);
    if (!match) return null;
    return [Number(match[1]), Number(match[2]), Number(match[3]), match[4] === undefined ? 1 : Number(match[4])];
  };
  const blend = (front, back) => {
    const alpha = front[3] + back[3] * (1 - front[3]);
    if (alpha <= 0) return [255, 255, 255, 1];
    return [
      (front[0] * front[3] + back[0] * back[3] * (1 - front[3])) / alpha,
      (front[1] * front[3] + back[1] * back[3] * (1 - front[3])) / alpha,
      (front[2] * front[3] + back[2] * back[3] * (1 - front[3])) / alpha,
      alpha,
    ];
  };
  const effectiveBackground = element => {
    const layers = [];
    let current = element;
    while (current) {
      const parsed = parseColor(getComputedStyle(current).backgroundColor);
      if (parsed && parsed[3] > 0) layers.push(parsed);
      current = current.parentElement;
    }
    let result = [255, 255, 255, 1];
    for (let index = layers.length - 1; index >= 0; index -= 1) result = blend(layers[index], result);
    return result;
  };
  const luminance = rgb => {
    const channels = rgb.slice(0, 3).map(value => {
      const normalized = value / 255;
      return normalized <= 0.03928 ? normalized / 12.92 : Math.pow((normalized + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
  };
  const contrast = (foreground, background) => {
    const parsed = parseColor(foreground);
    if (!parsed) return 0;
    const opaqueForeground = blend(parsed, background);
    const a = luminance(opaqueForeground);
    const b = luminance(background);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  };
  const inspectControls = selector => [...document.querySelectorAll(selector)].map(element => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return {
      text: (element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100),
      contrast: contrast(style.color, effectiveBackground(element)),
      color: style.color,
      backgroundColor: style.backgroundColor,
      height: rect.height,
      visible: rect.width > 1 && rect.height > 1 && style.visibility !== 'hidden' && style.display !== 'none',
    };
  });
  window.scrollTo(999999, 0);
  const horizontal = Math.abs(window.scrollX || 0);
  window.scrollTo(0, 0);
  const visible = element => {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return rect.width > 20 && rect.height > 20 && style.visibility !== 'hidden' && parseFloat(style.opacity || '1') > 0.3;
  };
  return {
    horizontal,
    h1Visible: visible(document.querySelector('h1')),
    homeFeature: visible(document.querySelector('#proof-gradient-challenge')),
    contractCards: document.querySelectorAll('.pg-contract').length,
    mainnetLink: !!document.querySelector('a[href="ethereum-mainnet.html"]'),
    activeProofLink: !!document.querySelector('a[href="proof-gradient-challenge.html"][aria-current="page"]'),
    pageButtons: inspectControls('.pg-btn'),
    homeButtons: inspectControls('#proof-gradient-challenge .pg-home-button'),
    forms: document.querySelectorAll('form').length,
  };
}
"""


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
        async with async_playwright() as playwright:
            executable = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chromium-browser")
            browser = await playwright.chromium.launch(
                headless=True,
                executable_path=executable,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
            )
            tests = 0
            for width, height in VIEWPORTS:
                context = await browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
                for name in PAGES:
                    tests += 1
                    page = await context.new_page()
                    try:
                        await page.goto(f"{base}/{name}", wait_until="load", timeout=45000)
                        await page.wait_for_timeout(250)
                        result = await page.evaluate(AUDIT)
                        prefix = f"{name}@{width}x{height}"
                        if result["horizontal"] > 2:
                            errors.append(f"{prefix}: horizontal scroll {result['horizontal']}px")
                        if not result["h1Visible"]:
                            errors.append(f"{prefix}: h1 not visible")
                        if name == "index.html":
                            if not result["homeFeature"]:
                                errors.append(f"{prefix}: Proof Gradient homepage feature not visible")
                            if len(result["homeButtons"]) != 3:
                                errors.append(f"{prefix}: expected three Proof Gradient homepage buttons")
                            for button in result["homeButtons"]:
                                if not button["visible"] or button["height"] < MIN_CONTROL_HEIGHT:
                                    errors.append(f"{prefix}: home control hidden/small: {button['text']}")
                                if button["contrast"] < MIN_CONTRAST:
                                    errors.append(
                                        f"{prefix}: home control contrast {button['contrast']:.2f}: {button['text']} "
                                        f"(color={button['color']}, background={button['backgroundColor']})"
                                    )
                        else:
                            if result["contractCards"] != 48:
                                errors.append(f"{prefix}: expected 48 contract cards, found {result['contractCards']}")
                            if not result["mainnetLink"]:
                                errors.append(f"{prefix}: Mainnet navigation link missing")
                            if not result["activeProofLink"]:
                                errors.append(f"{prefix}: active Proof Gradient navigation state missing")
                            if result["forms"]:
                                errors.append(f"{prefix}: unexpected form detected")
                            if len(result["pageButtons"]) != 3:
                                errors.append(f"{prefix}: expected three hero buttons")
                            for button in result["pageButtons"]:
                                if not button["visible"] or button["height"] < MIN_CONTROL_HEIGHT:
                                    errors.append(f"{prefix}: page control hidden/small: {button['text']}")
                                if button["contrast"] < MIN_CONTRAST:
                                    errors.append(
                                        f"{prefix}: page control contrast {button['contrast']:.2f}: {button['text']} "
                                        f"(color={button['color']}, background={button['backgroundColor']})"
                                    )
                        if screenshots and width in (375, 1440):
                            await page.screenshot(path=str(shotdir / f"{name[:-5]}-{width}x{height}.png"), full_page=False)
                    except Exception as exc:
                        message = f"{type(exc).__name__}: {exc}"
                        if "ERR_BLOCKED_BY_ADMINISTRATOR" in message:
                            warnings.append(f"{prefix}: local browser policy skipped page load")
                        else:
                            errors.append(f"{prefix}: {message}")
                    finally:
                        await page.close()
                await context.close()
            await browser.close()

    report = {
        "schemaVersion": "2.0",
        "status": "PASS" if not errors else "FAIL",
        "tests": tests,
        "viewports": VIEWPORTS,
        "pages": PAGES,
        "minimumContrast": MIN_CONTRAST,
        "minimumControlHeight": MIN_CONTROL_HEIGHT,
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
