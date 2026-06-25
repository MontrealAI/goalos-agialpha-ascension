#!/usr/bin/env python3
"""Browser-check the repository-aligned GoalOS Kernel v3 institutional publication."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGES = [
  "index.html",
  "sovereign-machine-economy-kernel-v3-paper.html",
  "sovereign-machine-economy-kernel-v3-use-cases.html",
  "sovereign-machine-economy-kernel-v3-publication-proof.html",
  "sovereign-machine-economy-kernel-v3.html",
]
VIEWPORTS = {
  "desktop": {"width": 1440, "height": 1100},
  "tablet": {"width": 900, "height": 1000},
  "mobile": {"width": 390, "height": 844},
}


class QuietHandler(SimpleHTTPRequestHandler):
  def log_message(self, format: str, *args: object) -> None:
    return


@contextlib.contextmanager
def serve(directory: Path):
  handler = partial(QuietHandler, directory=str(directory))
  server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  try:
    yield f"http://127.0.0.1:{server.server_port}"
  finally:
    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


def feature_contract(page, relative: str) -> bool:
  if relative == "index.html":
    return page.locator('[data-goalos-feature="sme-kernel-v3-institutional-publication"]').count() == 1 and page.locator('a[href="sovereign-machine-economy-kernel-v3-paper.html"]').count() >= 1
  if relative == "sovereign-machine-economy-kernel-v3-paper.html":
    return page.locator("[data-alignment-phase]").count() == 6 and page.locator(".pub-artifact").count() == 4 and page.locator(".pub-alignment-strip").count() == 1
  if relative == "sovereign-machine-economy-kernel-v3-use-cases.html":
    buttons = page.locator("[data-pub-filter]")
    cards = page.locator("[data-use-category]")
    if buttons.count() < 2 or cards.count() != 10:
      return False
    buttons.nth(1).click()
    hidden = page.locator("[data-use-category][hidden]").count()
    return 0 < hidden < cards.count()
  if relative == "sovereign-machine-economy-kernel-v3-publication-proof.html":
    return page.locator("#repository-alignment").count() == 1 and page.locator("#publication-citation").count() == 1 and page.locator("[data-copy-citation]").count() == 1
  return page.locator("[data-goalos-kernel-publication-link]").count() == 1 and page.locator("[data-goalos-kernel-publication-cta]").count() == 1 and page.locator(".kv3-autonomy-map [data-phase]").count() == 6


def main() -> int:
  root = Path(__file__).resolve().parents[2]
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--site", type=Path, default=root / "site")
  parser.add_argument("--output", type=Path, default=root / "site/qa/sme-kernel-v3-publication-browser")
  args = parser.parse_args()
  site = args.site.resolve()
  output = args.output.resolve()
  if not site.is_dir():
    raise SystemExit(f"Missing generated site: {site}")
  from playwright.sync_api import sync_playwright

  output.mkdir(parents=True, exist_ok=True)
  checks: list[dict] = []
  failures: list[str] = []
  environment_errors: list[str] = []
  file_mode = os.environ.get("GOALOS_BROWSER_FILE_MODE") == "1"
  try:
    with serve(site) as base_url, sync_playwright() as playwright:
      executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
      if not executable and Path("/usr/bin/chromium").is_file():
        executable = "/usr/bin/chromium"
      launch_options = {"executable_path": executable} if executable else {}
      browser = playwright.chromium.launch(**launch_options)
      try:
        for viewport_name, viewport in VIEWPORTS.items():
          context = browser.new_context(viewport=viewport, device_scale_factor=1, reduced_motion="reduce")
          try:
            for relative in PAGES:
              page = context.new_page()
              runtime_errors: list[str] = []
              page.on("console", lambda message, errors=runtime_errors: errors.append(f"console:{message.type}:{message.text}") if message.type == "error" else None)
              page.on("pageerror", lambda error, errors=runtime_errors: errors.append(f"pageerror:{error}"))
              label = f"{viewport_name}:{relative}"
              target = (site / relative).as_uri() if file_mode else f"{base_url}/{relative}"
              try:
                response = page.goto(target, wait_until="networkidle", timeout=30000)
                page.evaluate("document.fonts && document.fonts.ready")
                status = response.status if response else (200 if file_mode else 0)
                h1_visible = page.locator("h1").count() == 1 and page.locator("h1").is_visible()
                main_visible = page.locator("main").count() == 1 and page.locator("main").is_visible()
                overflow = page.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth")
                broken_images = page.evaluate("[...document.images].filter(img => !img.complete || img.naturalWidth === 0).map(img => img.getAttribute('src'))")
                feature_ok = feature_contract(page, relative)
                passed = status == 200 and h1_visible and main_visible and overflow <= 1 and not broken_images and not runtime_errors and feature_ok
                check = {
                  "check": label,
                  "status": "PASS" if passed else "FAIL",
                  "target": target,
                  "http_status": status,
                  "h1_visible": h1_visible,
                  "main_visible": main_visible,
                  "horizontal_overflow_px": overflow,
                  "broken_images": broken_images,
                  "runtime_errors": runtime_errors,
                  "feature_contract": feature_ok,
                }
              except Exception as error:
                passed = False
                check = {
                  "check": label,
                  "status": "FAIL",
                  "target": target,
                  "error_type": type(error).__name__,
                  "error": str(error),
                  "runtime_errors": runtime_errors,
                }
              checks.append(check)
              if not passed:
                failures.append(label)
              try:
                page.screenshot(path=str(output / f"{Path(relative).stem}-{viewport_name}.png"), full_page=True)
              except Exception as error:
                check["screenshot_error"] = f"{type(error).__name__}: {error}"
              finally:
                page.close()
          finally:
            context.close()
      finally:
        browser.close()
  except Exception as error:
    environment_errors.append(f"{type(error).__name__}: {error}")
    failures.append("browser-environment")
  report = {
    "schema": "goalos.sme_kernel_v3.institutional_publication.browser_report.v2",
    "status": "PASS" if not failures else "FAIL",
    "integration_revision": "r2",
    "pages": PAGES,
    "viewports": VIEWPORTS,
    "checks_passed": sum(1 for check in checks if check.get("status") == "PASS"),
    "checks_total": len(checks),
    "checks": checks,
    "environment_errors": environment_errors,
    "failures": failures,
  }
  report_path = output / "browser-report.json"
  report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  print(json.dumps(report, ensure_ascii=False, indent=2))
  return 0 if not failures else 1


if __name__ == "__main__":
  raise SystemExit(main())
