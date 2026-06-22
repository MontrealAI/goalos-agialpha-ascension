#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, contextlib, http.server, json, shutil, socket, socketserver, threading
from pathlib import Path
VIEWPORTS=[(375,812),(1440,1000)]
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,fmt,*args): pass
def pick_port():
    sock=socket.socket();sock.bind(("127.0.0.1",0));port=sock.getsockname()[1];sock.close();return port
@contextlib.contextmanager
def serve_dir(site):
    port=pick_port();handler=lambda *a,**kw:QuietHandler(*a,directory=str(site),**kw)
    server=socketserver.TCPServer(("127.0.0.1",port),handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try: yield f"http://127.0.0.1:{port}"
    finally: server.shutdown();server.server_close()
AUDIT="""() => {
 const parse=v=>{const m=String(v||'').match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);return m?[+m[1],+m[2],+m[3]]:null};
 const lum=rgb=>{const c=rgb.map(v=>{const s=v/255;return s<=.03928?s/12.92:Math.pow((s+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]};
 const ratio=(fg,bg)=>{const a=parse(fg),b=parse(bg);if(!a||!b)return 0;const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
 const inspect=sel=>[...document.querySelectorAll(sel)].map(el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return{text:(el.textContent||'').trim().slice(0,80),contrast:ratio(s.color,s.backgroundColor),width:r.width,height:r.height,visible:r.width>1&&r.height>1}});
 const hero=document.querySelector('.mn-hero .mn-container')?.getBoundingClientRect();
 return {version:document.body.dataset.designVersion||'',overflow:document.documentElement.scrollWidth-window.innerWidth,
 h1:!!document.querySelector('h1')&&document.querySelector('h1').getBoundingClientRect().height>50,
 centered:!!hero&&Math.abs((hero.left+hero.right)/2-window.innerWidth/2)<8,font:getComputedStyle(document.body).fontFamily,
 groups:document.querySelectorAll('details.mn-group').length,contracts:document.querySelectorAll('[data-mainnet-contract="true"]').length,
 forms:document.querySelectorAll('form').length,header:document.querySelector('header.top')?.getBoundingClientRect().height||0,
 buttons:inspect('.mn-btn'),cards:inspect('.mn-card,.mn-boundary,.mn-metric').slice(0,12)};
}"""
HOME="""() => {
 const parse=v=>{const m=String(v||'').match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);return m?[+m[1],+m[2],+m[3]]:null};
 const lum=rgb=>{const c=rgb.map(v=>{const s=v/255;return s<=.03928?s/12.92:Math.pow((s+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]};
 const ratio=(fg,bg)=>{const a=parse(fg),b=parse(bg);if(!a||!b)return 0;const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
 const shell=document.querySelector('#ethereum-mainnet-record .mn-home-shell'),r=shell?.getBoundingClientRect();
 const buttons=[...document.querySelectorAll('#ethereum-mainnet-record .mn-home-btn')].map(el=>{const s=getComputedStyle(el),q=el.getBoundingClientRect();return{text:(el.textContent||'').trim(),contrast:ratio(s.color,s.backgroundColor),height:q.height,visible:q.width>1&&q.height>1}});
 return {ok:!!shell,width:r?.width||0,centered:!!r&&Math.abs((r.left+r.right)/2-window.innerWidth/2)<8,buttons};
}"""
async def run(site,screenshots):
    try: from playwright.async_api import async_playwright
    except Exception:return ["Playwright is not installed"],[],0
    errors=[];warnings=[];tests=0;qa=site/"qa";qa.mkdir(exist_ok=True);shots=qa/"mainnet-v87-screenshots"
    if screenshots:shots.mkdir(exist_ok=True)
    with serve_dir(site) as base:
      async with async_playwright() as p:
       exe=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chromium-browser")
       browser=await p.chromium.launch(headless=True,executable_path=exe,args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
       for width,height in VIEWPORTS:
        ctx=await browser.new_context(viewport={"width":width,"height":height});page=await ctx.new_page();tests+=2
        try:
         await page.goto(f"{base}/ethereum-mainnet.html",wait_until="load",timeout=45000);await page.wait_for_timeout(200);a=await page.evaluate(AUDIT)
         if a["version"]!="v88-institutional":errors.append(f"mainnet@{width}: design marker missing")
         if a["overflow"]>8:errors.append(f"mainnet@{width}: horizontal overflow")
         if not a["h1"] or not a["centered"]:errors.append(f"mainnet@{width}: hero visibility/alignment failed")
         if "sans-serif" not in a["font"].lower():errors.append(f"mainnet@{width}: sans-serif system font missing")
         if a["groups"]!=5 or a["contracts"]!=49:errors.append(f"mainnet@{width}: registry count mismatch")
         if a["forms"]:errors.append(f"mainnet@{width}: form detected")
         if a["header"]<54:errors.append(f"mainnet@{width}: header collapsed")
         for b in a["buttons"]:
          if not b["visible"] or b["height"]<44:errors.append(f"mainnet@{width}: button hidden/small: {b['text']}")
          if b["contrast"]<4.5:errors.append(f"mainnet@{width}: button contrast {b['contrast']:.2f}: {b['text']}")
         if screenshots:await page.screenshot(path=str(shots/f"ethereum-mainnet-{width}x{height}.png"),full_page=True)
         await page.goto(f"{base}/index.html",wait_until="load",timeout=45000);await page.wait_for_timeout(150);h=await page.evaluate(HOME)
         if not h["ok"] or h["width"]<200 or not h["centered"]:errors.append(f"home@{width}: feature missing/misaligned")
         if len(h["buttons"])!=2:errors.append(f"home@{width}: expected 2 buttons")
         for b in h["buttons"]:
          if not b["visible"] or b["height"]<44:errors.append(f"home@{width}: button hidden/small: {b['text']}")
          if b["contrast"]<4.5:errors.append(f"home@{width}: button contrast {b['contrast']:.2f}: {b['text']}")
         if screenshots:await page.locator("#ethereum-mainnet-record").screenshot(path=str(shots/f"homepage-mainnet-{width}x{height}.png"))
        except Exception as e:errors.append(f"browser QA@{width}: {type(e).__name__}: {e}")
        finally:await page.close();await ctx.close()
       await browser.close()
    return errors,warnings,tests
async def main_async(args):
    errors,warnings,tests=await run(Path(args.site),args.screenshots)
    report={"status":"PASS" if not errors else "FAIL","tests":tests,"viewports":VIEWPORTS,"errors":errors,"warnings":warnings,"design":"v88-institutional","minimumButtonContrast":4.5}
    qa=Path(args.site)/"qa";qa.mkdir(exist_ok=True);(qa/"mainnet-page-browser-verify-v87.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2));return 0 if not errors else 1
def main():
    p=argparse.ArgumentParser();p.add_argument("--site",default="site");p.add_argument("--screenshots",action="store_true");return asyncio.run(main_async(p.parse_args()))
if __name__=="__main__":raise SystemExit(main())
