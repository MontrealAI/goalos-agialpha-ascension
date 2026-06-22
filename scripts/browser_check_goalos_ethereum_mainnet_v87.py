#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import html as html_module
import json
import re
import shutil
from pathlib import Path

VIEWPORTS = [(375, 812), (1440, 1000)]
MIN_CONTRAST = 4.5
MIN_CONTROL_HEIGHT = 44


COLOR_AUDIT = r"""
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
    const values = rgb.slice(0, 3).map(value => {
      const normalized = value / 255;
      return normalized <= 0.03928 ? normalized / 12.92 : Math.pow((normalized + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2];
  };
  const contrast = (foreground, background) => {
    const fg = parseColor(foreground);
    if (!fg) return 0;
    const opaqueForeground = blend(fg, background);
    const a = luminance(opaqueForeground);
    const b = luminance(background);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  };
  const inspect = selector => [...document.querySelectorAll(selector)].map(element => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    const ownBackground = parseColor(style.backgroundColor);
    const background = ownBackground && ownBackground[3] > 0.98 ? ownBackground : effectiveBackground(element);
    return {
      text: (element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100),
      className: element.className,
      variant: element.dataset.variant || '',
      color: style.color,
      backgroundColor: style.backgroundColor,
      backgroundImage: style.backgroundImage,
      contrast: contrast(style.color, background),
      width: rect.width,
      height: rect.height,
      visible: rect.width > 1 && rect.height > 1 && style.visibility !== 'hidden' && style.display !== 'none',
    };
  });
  const hero = document.querySelector('.mn-hero .mn-container')?.getBoundingClientRect();
  return {
    version: document.body.dataset.designVersion || '',
    overflow: document.documentElement.scrollWidth - window.innerWidth,
    h1Visible: !!document.querySelector('h1') && document.querySelector('h1').getBoundingClientRect().height > 50,
    centered: !!hero && Math.abs((hero.left + hero.right) / 2 - window.innerWidth / 2) < 8,
    font: getComputedStyle(document.body).fontFamily,
    groups: document.querySelectorAll('details.mn-group').length,
    contracts: document.querySelectorAll('[data-mainnet-contract="true"]').length,
    forms: document.querySelectorAll('form').length,
    headerHeight: document.querySelector('header.top')?.getBoundingClientRect().height || 0,
    proofGradientLink: !!document.querySelector('a[href="proof-gradient-challenge.html"]'),
    buttons: inspect('.mn-btn'),
  };
}
"""


HOME_AUDIT = r"""
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
    const values = rgb.slice(0, 3).map(value => {
      const normalized = value / 255;
      return normalized <= 0.03928 ? normalized / 12.92 : Math.pow((normalized + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2];
  };
  const contrast = (foreground, background) => {
    const fg = parseColor(foreground);
    if (!fg) return 0;
    const opaqueForeground = blend(fg, background);
    const a = luminance(opaqueForeground);
    const b = luminance(background);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  };
  const shell = document.querySelector('#ethereum-mainnet-record .mn-home-shell');
  const rect = shell?.getBoundingClientRect();
  const buttons = [...document.querySelectorAll('#ethereum-mainnet-record .mn-home-btn')].map(element => {
    const style = getComputedStyle(element);
    const box = element.getBoundingClientRect();
    const ownBackground = parseColor(style.backgroundColor);
    const background = ownBackground && ownBackground[3] > 0.98 ? ownBackground : effectiveBackground(element);
    return {
      text: (element.textContent || '').trim().replace(/\s+/g, ' '),
      variant: element.dataset.variant || '',
      color: style.color,
      backgroundColor: style.backgroundColor,
      contrast: contrast(style.color, background),
      height: box.height,
      visible: box.width > 1 && box.height > 1,
    };
  });
  return {
    ok: !!shell,
    width: rect?.width || 0,
    centered: !!rect && Math.abs((rect.left + rect.right) / 2 - window.innerWidth / 2) < 8,
    buttons,
  };
}
"""


def inline_local_assets(site: Path, filename: str) -> str:
    """Inline local CSS/JS so browser QA never depends on an HTTP server."""
    path = site / filename
    if not path.is_file():
        raise FileNotFoundError(path)
    document = path.read_text(encoding="utf-8", errors="ignore")

    link_pattern = re.compile(
        r"<link\b(?=[^>]*\brel=(?:['\"])?stylesheet(?:['\"])?)(?=[^>]*\bhref=['\"]([^'\"]+)['\"])[^>]*>",
        re.IGNORECASE,
    )

    def replace_link(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "//", "data:")):
            return match.group(0)
        asset = site / href.split("?", 1)[0].split("#", 1)[0]
        if not asset.is_file() or asset.suffix.lower() != ".css":
            return match.group(0)
        css = asset.read_text(encoding="utf-8", errors="ignore")
        return f"<style data-inlined-from='{html_module.escape(href, quote=True)}'>\n{css}\n</style>"

    document = link_pattern.sub(replace_link, document)

    script_pattern = re.compile(
        r"<script\b(?=[^>]*\bsrc=['\"]([^'\"]+)['\"])[^>]*>\s*</script>",
        re.IGNORECASE,
    )

    def replace_script(match: re.Match[str]) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "//", "data:")):
            return ""
        asset = site / src.split("?", 1)[0].split("#", 1)[0]
        if not asset.is_file() or asset.suffix.lower() != ".js":
            return ""
        script = asset.read_text(encoding="utf-8", errors="ignore").replace("</script", "<\\/script")
        return f"<script data-inlined-from='{html_module.escape(src, quote=True)}'>\n{script}\n</script>"

    return script_pattern.sub(replace_script, document)


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
    shots = qa / "mainnet-v87-screenshots"
    if screenshots:
        shots.mkdir(exist_ok=True)

    try:
        mainnet_document = inline_local_assets(site, "ethereum-mainnet.html")
        homepage_document = inline_local_assets(site, "index.html")
    except OSError as exc:
        return [f"Could not prepare inline browser document: {exc}"], warnings, tests

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
            tests += 2
            try:
                await page.set_content(mainnet_document, wait_until="load", timeout=45000)
                await page.wait_for_timeout(250)
                audit = await page.evaluate(COLOR_AUDIT)
                prefix = f"mainnet@{width}x{height}"
                if audit["version"] != "v88-institutional":
                    errors.append(f"{prefix}: design marker missing")
                if audit["overflow"] > 8:
                    errors.append(f"{prefix}: horizontal overflow {audit['overflow']}px")
                if not audit["h1Visible"] or not audit["centered"]:
                    errors.append(f"{prefix}: hero visibility/alignment failed")
                if "sans-serif" not in audit["font"].lower():
                    errors.append(f"{prefix}: sans-serif system font missing")
                if audit["groups"] != 5 or audit["contracts"] != 49:
                    errors.append(f"{prefix}: registry count mismatch")
                if audit["forms"]:
                    errors.append(f"{prefix}: form detected")
                if audit["headerHeight"] < 54:
                    errors.append(f"{prefix}: header collapsed")
                if not audit["proofGradientLink"]:
                    errors.append(f"{prefix}: Proof Gradient navigation link missing")
                if len(audit["buttons"]) != 3:
                    errors.append(f"{prefix}: expected three hero buttons, found {len(audit['buttons'])}")
                variants = {button.get("variant") for button in audit["buttons"]}
                if variants != {"primary", "secondary", "ghost"}:
                    errors.append(f"{prefix}: unexpected hero button variants: {sorted(variants)}")
                for button in audit["buttons"]:
                    if not button["visible"] or button["height"] < MIN_CONTROL_HEIGHT:
                        errors.append(f"{prefix}: button hidden/small: {button['text']}")
                    if button["contrast"] < MIN_CONTRAST:
                        errors.append(
                            f"{prefix}: button contrast {button['contrast']:.2f}: {button['text']} "
                            f"(variant={button.get('variant')}, color={button['color']}, background={button['backgroundColor']})"
                        )
                if screenshots:
                    await page.screenshot(path=str(shots / f"ethereum-mainnet-{width}x{height}.png"), full_page=True)

                await page.set_content(homepage_document, wait_until="load", timeout=45000)
                await page.wait_for_timeout(180)
                home = await page.evaluate(HOME_AUDIT)
                home_prefix = f"home@{width}x{height}"
                if not home["ok"] or home["width"] < 200 or not home["centered"]:
                    errors.append(f"{home_prefix}: Mainnet feature missing/misaligned")
                if len(home["buttons"]) != 2:
                    errors.append(f"{home_prefix}: expected two Mainnet feature buttons")
                home_variants = {button.get("variant") for button in home["buttons"]}
                if home_variants != {"primary", "secondary"}:
                    errors.append(f"{home_prefix}: unexpected button variants: {sorted(home_variants)}")
                for button in home["buttons"]:
                    if not button["visible"] or button["height"] < MIN_CONTROL_HEIGHT:
                        errors.append(f"{home_prefix}: button hidden/small: {button['text']}")
                    if button["contrast"] < MIN_CONTRAST:
                        errors.append(
                            f"{home_prefix}: button contrast {button['contrast']:.2f}: {button['text']} "
                            f"(variant={button.get('variant')}, color={button.get('color')}, background={button.get('backgroundColor')})"
                        )
                if screenshots:
                    await page.locator("#ethereum-mainnet-record").screenshot(
                        path=str(shots / f"homepage-mainnet-feature-{width}x{height}.png")
                    )
            except Exception as exc:
                errors.append(f"browser QA@{width}x{height}: {type(exc).__name__}: {exc}")
            finally:
                await page.close()
                await context.close()
        await browser.close()
    return errors, warnings, tests


async def main_async(args: argparse.Namespace) -> int:
    site = Path(args.site)
    errors, warnings, tests = await run(site, args.screenshots)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "tests": tests,
        "viewports": VIEWPORTS,
        "errors": errors,
        "warnings": warnings,
        "design": "v88-institutional",
        "minimumButtonContrast": MIN_CONTRAST,
        "minimumControlHeight": MIN_CONTROL_HEIGHT,
        "browserMode": "self-contained-inline-assets",
    }
    qa = site / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "mainnet-page-browser-verify-v87.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = ["# GoalOS Ethereum Mainnet Browser QA", "", f"Status: **{report['status']}**", "", f"Tests: {tests}", "", "## Errors"]
    md += [f"- {error}" for error in errors] or ["- None"]
    md += ["", "## Warnings"]
    md += [f"- {warning}" for warning in warnings] or ["- None"]
    (qa / "mainnet-page-browser-verify-v87.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-contained browser QA for the generated GoalOS Ethereum Mainnet experience")
    parser.add_argument("--site", default="site")
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
