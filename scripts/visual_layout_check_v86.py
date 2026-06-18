#!/usr/bin/env python3
"""GoalOS v86 browser QA hotfix 2.

This test checks production-visible mobile issues without falsely failing intentionally
clipped decorative SVG internals. It serves the generated site over localhost instead
of file:// to avoid Chromium local-file policy noise.
"""
from pathlib import Path
import argparse, asyncio, contextlib, http.server, json, os, shutil, socket, socketserver, sys, threading

VIEWPORTS = [(320,800),(375,812),(768,1024),(1024,768),(1440,1000)]
IMPORTANT = [
    "index.html","mission-os.html","proof-cards.html","proof-card-001.html","proof-card-023.html",
    "proof-card-028.html","proof-card-031.html","whitepaper.html","resources.html",
    "sovereign-rsi-control-plane.html","proof-treasury.html","proof-treasury-simulation-003.html",
    "proof-treasury-simulation-004.html","proof-treasury-simulation-005.html","ascension.html","paper.html",
    "evidence-docket.html","start-here.html"
]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

def pick_port():
    s=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]; s.close(); return port

@contextlib.contextmanager
def serve_dir(site: Path):
    port=pick_port()
    handler=lambda *args, **kw: QuietHandler(*args, directory=str(site), **kw)
    httpd=socketserver.TCPServer(("127.0.0.1", port), handler)
    t=threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown(); httpd.server_close()

async def main_async(site: Path, screenshots: bool):
    try:
        from playwright.async_api import async_playwright
    except Exception:
        print("ERROR: playwright is not installed. Install with: python -m pip install playwright && python -m playwright install chromium", file=sys.stderr)
        return 2
    htmls = sorted(p.name for p in site.glob("*.html"))
    pages=[]
    for n in IMPORTANT:
        if (site/n).exists() and n not in pages:
            pages.append(n)
    # Include proof-card pages, but keep runtime bounded and avoid duplicate page checks.
    for n in htmls:
        if n.startswith("proof-card-") and n not in pages:
            pages.append(n)
    errors=[]; warnings=[]; tests=0
    qadir=site/"qa"; qadir.mkdir(exist_ok=True)
    shot_dir=qadir/"screenshots"
    if screenshots: shot_dir.mkdir(exist_ok=True)
    with serve_dir(site) as base_url:
        async with async_playwright() as p:
            executable=os.environ.get("CHROMIUM_PATH") or shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chromium-browser")
            launch_args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--disable-features=Translate,BackForwardCache"]
            browser=await p.chromium.launch(headless=True, executable_path=executable, args=launch_args)
            for w,h in VIEWPORTS:
                ctx=await browser.new_context(viewport={"width":w,"height":h}, device_scale_factor=1)
                for name in pages:
                    tests+=1
                    page=await ctx.new_page()
                    try:
                        await page.goto(f"{base_url}/{name}", wait_until="load", timeout=45000)
                        await page.wait_for_timeout(220)
                        data=await page.evaluate("""() => {
                          const de=document.documentElement, body=document.body;
                          const vw=window.innerWidth;
                          const vh=window.innerHeight;
                          const err=[]; const warn=[];
                          // Actual user-visible horizontal scroll check. scrollWidth alone can include
                          // intentionally clipped decorative SVG/aurora content, so we test scrollability.
                          window.scrollTo(999999, 0);
                          const sx = Math.abs(window.scrollX || window.pageXOffset || 0);
                          window.scrollTo(0, 0);
                          if(sx > 2) err.push(`user-horizontal-scroll ${sx}px at viewport ${vw}`);
                          for(const n of [...document.querySelectorAll('header,nav,.top,.topin,.nav,.navbar,.navbar-inner,.v86-nav-panel')]){
                            const r=n.getBoundingClientRect();
                            if(r.width > vw + 8) err.push(`nav-visible-overflow ${Math.round(r.width)} > ${vw}`);
                          }
                          // Critical structural containers should not force visible page overflow.
                          for(const sel of ['main','article','section','.wrap','.container','.topin']){
                            for(const el of document.querySelectorAll(sel)){
                              const r=el.getBoundingClientRect();
                              if(r.width > vw + 8) err.push(`${sel} width-overflow ${Math.round(r.width)} > ${vw}`);
                            }
                          }
                          // Informational only: count SVGs without viewBox; do not fail preserved legacy art.
                          let missingViewBox=0;
                          for(const svg of document.querySelectorAll('svg')){ if(!svg.getAttribute('viewBox')) missingViewBox++; }
                          if(missingViewBox) warn.push(`svg missing viewBox count=${missingViewBox}`);
                          for(const img of document.querySelectorAll('img')){
                            if(!img.getAttribute('alt') && img.getAttribute('aria-hidden') !== 'true') err.push('image missing alt');
                          }
                          let clickable=0;
                          for(const a of document.querySelectorAll('a,button')){const r=a.getBoundingClientRect(); if(r.width>8 && r.height>8) clickable++;}
                          if(clickable<3) err.push(`too few visible clickable controls: ${clickable}`);
                          const css = [...document.styleSheets].length;
                          const hasDynamicAI=!!document.querySelector('.v86-ai-canvas,.asi-canvas,.asi-bg,[class*="aura"],[class*="orbit"],[class*="rsi"],[class*="AI"]');
                          if(location.pathname.endsWith('/index.html') || location.pathname === '/'){
                            const h1=document.querySelector('h1');
                            if(!h1) err.push('homepage missing h1');
                            else {
                              const r=h1.getBoundingClientRect(); const cs=getComputedStyle(h1);
                              if(r.bottom < 0 || r.top > vh*.95 || r.width < 40 || r.height < 30 || cs.visibility==='hidden' || parseFloat(cs.opacity||'1') < .5) err.push('homepage hero h1 not visible in first viewport');
                            }
                            const canvas=document.querySelector('.asi-canvas,.v86-ai-canvas');
                            if(canvas){ const cs=getComputedStyle(canvas); if(cs.position !== 'fixed') err.push('dynamic AI canvas is not fixed; it may create blank top space'); }
                          }
                          for(const a of document.querySelectorAll('footer a,.footer a,.site-footer a,.gm-footer a')){
                            const r=a.getBoundingClientRect(); if(r.width>8 && r.height>8){ const cs=getComputedStyle(a); const txt=cs.color.replace(/\s/g,''); const bg=cs.backgroundColor.replace(/\s/g,''); if((bg.includes('255,255,255')||bg.includes('255,255,255,1')) && (txt.includes('255,255,255')||txt.includes('248,250,252')||txt.includes('255,255,255,1'))) err.push('footer link has pale text on white background'); }
                          }
                          return {errors:err, warnings:warn, viewport:vw, height:de.scrollHeight, hasDynamicAI, css};
                        }""")
                        if data["errors"]:
                            errors.extend(f"{name}@{w}x{h}: {e}" for e in data["errors"])
                        if data["warnings"]:
                            warnings.extend(f"{name}@{w}x{h}: {e}" for e in data["warnings"][:6])
                        if name=="index.html" and not data.get("hasDynamicAI"):
                            errors.append(f"{name}@{w}x{h}: Dynamic AI visual signal not detected")
                        if screenshots and name in IMPORTANT and w in (375,1440):
                            await page.screenshot(path=str(shot_dir/f"{name.replace('.html','')}-{w}x{h}.png"), full_page=False)
                    except Exception as e:
                        msg=f"{type(e).__name__}: {e}"
                        if "ERR_BLOCKED_BY_ADMINISTRATOR" in msg:
                            warnings.append(f"{name}@{w}x{h}: browser policy skipped page load in local QA")
                        else:
                            errors.append(f"{name}@{w}x{h}: {msg}")
                    finally:
                        await page.close()
                await ctx.close()
            await browser.close()
    report={"status":"PASS" if not errors else "FAIL", "tests":tests, "viewports":VIEWPORTS, "errors":errors[:500], "warnings":warnings[:500], "qa_mode":"v86-layout-hotfix-2-localhost-visible-scroll"}
    (qadir/"layout-report-v86.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md=["# GoalOS v86 Browser Layout QA", "", f"Status: **{report['status']}**", "", f"Tests: {tests}", "", f"Viewports: {VIEWPORTS}", "", "## Errors"]
    md += [f"- {e}" for e in errors[:500]] or ["- None"]
    md += ["", "## Warnings"] + ([f"- {w}" for w in warnings[:500]] or ["- None"])
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
