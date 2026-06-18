#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys, asyncio, os
from urllib.parse import urljoin

VIEWPORTS = [(320,800),(375,812),(768,1024),(1024,768),(1440,1000)]
SELECTORS = [".figure-frame",".diagram-frame",".visual-shell",".proof-card-visual",".card",".panel","figure","img","svg","canvas",".v86-scroll-table"]
IMPORTANT = ["index.html","mission-os.html","proof-cards.html","proof-card-001.html","proof-card-023.html","proof-card-028.html","proof-card-031.html","whitepaper.html","resources.html","sovereign-rsi-control-plane.html"]

async def main_async(site: Path, screenshots: bool):
    try:
        from playwright.async_api import async_playwright
    except Exception as e:
        print("ERROR: playwright is not installed. Install with: python -m pip install playwright && python -m playwright install chromium", file=sys.stderr)
        return 2
    htmls = sorted(p.name for p in site.glob("*.html"))
    # test all pages if feasible; priority pages first
    pages = []
    for n in IMPORTANT:
        if (site/n).exists() and n not in pages: pages.append(n)
    for n in htmls:
        if n not in pages: pages.append(n)
    errors=[]
    tests=0
    qadir=site/"qa"
    qadir.mkdir(exist_ok=True)
    shot_dir=qadir/"screenshots"
    if screenshots:
        shot_dir.mkdir(exist_ok=True)
    async with async_playwright() as p:
        import shutil
        executable = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chromium-browser")
        browser = await p.chromium.launch(headless=True, executable_path=executable, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        for w,h in VIEWPORTS:
            ctx = await browser.new_context(viewport={"width":w,"height":h}, device_scale_factor=1)
            for name in pages:
                tests += 1
                page = await ctx.new_page()
                url = (site/name).resolve().as_uri()
                try:
                    await page.goto(url, wait_until="load", timeout=30000)
                    await page.wait_for_timeout(250)
                    data = await page.evaluate("""(selectors) => {
                      const de = document.documentElement;
                      const body = document.body;
                      const err = [];
                      const sw = Math.max(de.scrollWidth, body ? body.scrollWidth : 0);
                      const vw = window.innerWidth;
                      if (sw > vw + 2) err.push(`horizontal-scroll ${sw} > ${vw}`);
                      const navs = [...document.querySelectorAll('header, nav, .top, .topin')];
                      for (const n of navs) {
                        const r = n.getBoundingClientRect();
                        if (r.width > vw + 2) err.push(`nav-overflow ${Math.round(r.width)} > ${vw}`);
                      }
                      for (const sel of selectors) {
                        for (const el of document.querySelectorAll(sel)) {
                          const r = el.getBoundingClientRect();
                          if (!r.width || !r.height) continue;
                          if (r.right > vw + 2 || r.left < -2) err.push(`${sel} viewport escape left=${Math.round(r.left)} right=${Math.round(r.right)} vw=${vw}`);
                          const parent = el.parentElement;
                          if(parent){
                            const pr = parent.getBoundingClientRect();
                            if(r.right > pr.right + 3 && pr.width > 0 && r.width > 20) err.push(`${sel} escapes parent by ${Math.round(r.right-pr.right)}px`);
                          }
                        }
                      }
                      for (const img of document.querySelectorAll('img')) {
                        if (!img.getAttribute('alt') && img.getAttribute('aria-hidden') !== 'true') err.push('image missing alt');
                      }
                      const ctas = document.querySelectorAll('a,button');
                      let clickable = 0;
                      for (const a of ctas){ const r=a.getBoundingClientRect(); if(r.width>8 && r.height>8) clickable++; }
                      if(clickable < 3) err.push(`too few visible clickable controls: ${clickable}`);
                      const canvas = document.querySelector('.v86-ai-canvas');
                      const hasDynamicAI = !!canvas || !!document.querySelector('[class*="aura"], [class*="orbit"], [class*="rsi"]');
                      return {errors: err.slice(0,40), scrollWidth: sw, viewport: vw, height: de.scrollHeight, hasDynamicAI};
                    }""", SELECTORS)
                    if data["errors"]:
                        for e in data["errors"]:
                            errors.append(f"{name}@{w}x{h}: {e}")
                    if name == "index.html" and not data.get("hasDynamicAI"):
                        errors.append(f"{name}@{w}x{h}: Dynamic AI visual signal not detected")
                    if screenshots and name in IMPORTANT and w in (375,1440):
                        await page.screenshot(path=str(shot_dir/f"{name.replace('.html','')}-{w}x{h}.png"), full_page=False)
                except Exception as e:
                    errors.append(f"{name}@{w}x{h}: {type(e).__name__}: {e}")
                finally:
                    await page.close()
            await ctx.close()
        await browser.close()
    report = {"status":"PASS" if not errors else "FAIL", "tests":tests, "viewports":VIEWPORTS, "errors":errors[:500]}
    (qadir/"layout-report-v86.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md=["# GoalOS v86 Browser Layout QA","",f"Status: **{report['status']}**","",f"Tests: {tests}","",f"Viewports: {VIEWPORTS}","", "## Errors"]
    md += [f"- {e}" for e in errors[:500]] or ["- None"]
    (qadir/"layout-report-v86.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    ap.add_argument("--screenshots", action="store_true")
    args=ap.parse_args()
    return asyncio.run(main_async(Path(args.site), args.screenshots))
if __name__=="__main__":
    raise SystemExit(main())
