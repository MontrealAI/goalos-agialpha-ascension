#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
from pathlib import Path

VIEWPORTS = [(320, 800), (360, 800), (375, 812), (390, 844), (1440, 1000)]
REQUIRED = ["ethereum-mainnet.html", "index.html", "proof-mission-008.html", "proof-missions.html"]

AUDIT = r"""() => {
  const parse=v=>{const m=String(v||'').match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);return m?[+m[1],+m[2],+m[3]]:null};
  const lum=rgb=>{const c=rgb.map(v=>{const s=v/255;return s<=.03928?s/12.92:Math.pow((s+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]};
  const ratio=(fg,bg)=>{const a=parse(fg),b=parse(bg);if(!a||!b)return 0;const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
  const hero = document.querySelector('.mn-hero .mn-container')?.getBoundingClientRect();
  const buttons = [...document.querySelectorAll('.mn-btn')].map(el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return {text:(el.textContent||'').trim(), width:r.width, height:r.height, visible:r.width>1&&r.height>1, color:s.color, background:s.backgroundColor, contrast:ratio(s.color,s.backgroundColor)};
  });
  const overflowElements = [...document.querySelectorAll('body *')].map((el, index) => {
    const r = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return {
      index,
      tag: el.tagName.toLowerCase(),
      id: el.id || '',
      className: typeof el.className === 'string' ? el.className : '',
      text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80),
      left: Math.round(r.left),
      right: Math.round(r.right),
      width: Math.round(r.width),
      overflowX: style.overflowX,
      whiteSpace: style.whiteSpace
    };
  }).filter(item => item.right > window.innerWidth + 1 || item.left < -1)
    .sort((a, b) => (b.right-window.innerWidth) - (a.right-window.innerWidth))
    .slice(0, 8);
  return {
    version: document.body.dataset.designVersion || '',
    overflow: document.documentElement.scrollWidth-window.innerWidth,
    overflowElements,
    title: (document.querySelector('h1')?.textContent||'').trim(),
    centered: !!hero && Math.abs((hero.left+hero.right)/2-window.innerWidth/2)<8,
    groups: document.querySelectorAll('details.mn-group').length,
    contracts: document.querySelectorAll('[data-mainnet-contract="true"]').length,
    forms: document.querySelectorAll('form').length,
    buttons,
    releaseLink: !!document.querySelector('a[href*="v4.4.0-mainnet-2026-06-21"]'),
    productionBoundary: document.body.innerText.includes('Production activation: NO')
  };
}"""

HOME = r"""() => {
  const shell=document.querySelector('#ethereum-mainnet-record .mn-home-shell');
  const r=shell?.getBoundingClientRect();
  const buttons=[...document.querySelectorAll('#ethereum-mainnet-record .mn-home-btn')].map(el=>{const q=el.getBoundingClientRect();return{text:(el.textContent||'').trim(),height:q.height,visible:q.width>1&&q.height>1,href:el.getAttribute('href')}});
  return {
    ok:!!shell,
    width:r?.width||0,
    centered:!!r&&Math.abs((r.left+r.right)/2-window.innerWidth/2)<8,
    overflow:document.documentElement.scrollWidth-window.innerWidth,
    buttons,
    mainnetLink:!!document.querySelector('a[href="ethereum-mainnet.html"]'),
    mission008:!!document.querySelector('[data-proof-mission="008"]')
  };
}"""


def launch_browser(playwright):
    try:
        return awaitable(playwright.chromium.launch(headless=True))
    except Exception:
        executable = (
            shutil.which("chromium")
            or shutil.which("google-chrome")
            or shutil.which("chromium-browser")
            or shutil.which("google-chrome-stable")
        )
        if not executable:
            raise
        return awaitable(
            playwright.chromium.launch(
                headless=True,
                executable_path=executable,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
            )
        )


def awaitable(value):
    return value


async def run(site: Path, screenshots: bool):
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return ["Playwright is not installed"], [], 0

    missing = [name for name in REQUIRED if not (site / name).is_file() or (site / name).stat().st_size == 0]
    if missing:
        return ["Generated page preflight failed. Missing or empty: " + ", ".join(missing)], [], 0

    errors: list[str] = []
    warnings: list[str] = []
    tests = 0
    qa = site / "qa"
    qa.mkdir(exist_ok=True)
    shots = qa / "mainnet-v87-screenshots"
    if screenshots:
        shots.mkdir(exist_ok=True)

    mainnet_html = (site / "ethereum-mainnet.html").read_text(encoding="utf-8")
    homepage_html = (site / "index.html").read_text(encoding="utf-8")

    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(headless=True)
        except Exception:
            executable = (
                shutil.which("chromium")
                or shutil.which("google-chrome")
                or shutil.which("chromium-browser")
                or shutil.which("google-chrome-stable")
            )
            if not executable:
                raise
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
                await page.set_content(mainnet_html, wait_until="domcontentloaded", timeout=30_000)
                await page.wait_for_selector(".mn-hero h1", state="visible", timeout=10_000)
                audit = await page.evaluate(AUDIT)
                if audit["version"] != "v88-institutional":
                    errors.append(f"mainnet@{width}: design marker missing")
                if audit["overflow"] > 1:
                    details = "; ".join(
                        f"{item['tag']}#{item['id']}.{item['className']} right={item['right']} text={item['text']!r}"
                        for item in audit.get("overflowElements", [])[:4]
                    )
                    errors.append(
                        f"mainnet@{width}: horizontal overflow {audit['overflow']}px"
                        + (f"; offenders: {details}" if details else "")
                    )
                normalized_title = audit["title"].replace("\u00a0", " ").lower()
                if "chain 1" not in normalized_title or not audit["centered"]:
                    errors.append(f"mainnet@{width}: hero visibility/alignment failed")
                if audit["groups"] != 5 or audit["contracts"] != 49:
                    errors.append(f"mainnet@{width}: registry count mismatch")
                if audit["forms"]:
                    errors.append(f"mainnet@{width}: form detected")
                if not audit["releaseLink"] or not audit["productionBoundary"]:
                    errors.append(f"mainnet@{width}: release or production-boundary content missing")
                for button in audit["buttons"]:
                    if not button["visible"] or button["height"] < 44:
                        errors.append(f"mainnet@{width}: button hidden/small: {button['text']}")
                    if not button["text"]:
                        errors.append(f"mainnet@{width}: button label is empty")
                    if button["contrast"] < 4.5:
                        errors.append(f"mainnet@{width}: button contrast {button['contrast']:.2f}: {button['text']}")
                if screenshots:
                    await page.screenshot(path=str(shots / f"ethereum-mainnet-{width}x{height}.png"), full_page=True)

                await page.set_content(homepage_html, wait_until="domcontentloaded", timeout=30_000)
                await page.wait_for_selector("#ethereum-mainnet-record", state="visible", timeout=10_000)
                home = await page.evaluate(HOME)
                if not home["ok"] or home["width"] < 200 or not home["centered"]:
                    errors.append(f"home@{width}: Mainnet feature missing/misaligned")
                if len(home["buttons"]) != 2 or not home["mainnetLink"]:
                    errors.append(f"home@{width}: Mainnet actions are incomplete")
                if not home["mission008"]:
                    errors.append(f"home@{width}: Mission 008 panel was not preserved")
                for button in home["buttons"]:
                    if not button["visible"] or button["height"] < 44:
                        errors.append(f"home@{width}: button hidden/small: {button['text']}")
                if screenshots:
                    await page.locator("#ethereum-mainnet-record").screenshot(
                        path=str(shots / f"homepage-mainnet-{width}x{height}.png")
                    )
            except Exception as exc:
                errors.append(f"browser QA@{width}: {type(exc).__name__}: {exc}")
            finally:
                await page.close()
                await context.close()
        await browser.close()

    return errors, warnings, tests


async def main_async(args) -> int:
    errors, warnings, tests = await run(Path(args.site), args.screenshots)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "tests": tests,
        "viewports": VIEWPORTS,
        "errors": errors,
        "warnings": warnings,
        "design": "v88-institutional",
        "renderMode": "direct-generated-html-no-localhost",
        "proofMissionsPreserved": 8,
    }
    qa = Path(args.site) / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "mainnet-page-browser-verify-v87.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--screenshots", action="store_true")
    return asyncio.run(main_async(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
