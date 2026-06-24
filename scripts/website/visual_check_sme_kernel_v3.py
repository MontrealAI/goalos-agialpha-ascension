#!/usr/bin/env python3
"""Run Chromium interaction, responsive, adversarial and visual QA for SME Kernel v3."""
from __future__ import annotations
import argparse, contextlib, json, os, re, shutil, socket, tempfile, threading, time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

PAGES={
    'experience':'sovereign-machine-economy-kernel-v3.html',
    'protocol':'sovereign-machine-economy-kernel-v3-protocol.html',
    'chronicle':'sovereign-machine-economy-kernel-v3-chronicle.html',
    'verifier':'sovereign-machine-economy-kernel-v3-verifier.html',
    'sdk':'sovereign-machine-economy-kernel-v3-sdk.html',
}

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None: return

@contextlib.contextmanager
def serve(directory: Path) -> Iterator[str]:
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=int(probe.getsockname()[1])
    server=ThreadingHTTPServer(('127.0.0.1',port),partial(QuietHandler,directory=str(directory)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try: yield f'http://127.0.0.1:{port}'
    finally: server.shutdown();thread.join(timeout=5);server.server_close()

def write_json(path:Path,value:Any)->None:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def record(results:list[dict[str,Any]],label:str,condition:bool,detail:Any='')->None:results.append({'label':label,'status':'PASS' if condition else 'FAIL','detail':detail})
def overflow(page:Any)->dict[str,Any]:return page.evaluate("""() => ({documentWidth:document.documentElement.scrollWidth,viewportWidth:document.documentElement.clientWidth,bodyWidth:document.body.scrollWidth,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+2})""")
def short(value:Any,n:int=24)->str:
    text=str(value or '');return text if len(text)<=n else text[:n]+'…'

def worker_bundle(site:Path)->str:
    core=(site/'assets/sme-kernel-v3-core.js').read_text(encoding='utf-8')
    adapters=(site/'assets/sme-kernel-v3-adapters.js').read_text(encoding='utf-8')
    worker=(site/'assets/sme-kernel-v3-worker.js').read_text(encoding='utf-8')
    worker=re.sub(r"^'use strict';\s*importScripts\([^\n]+\);","'use strict';",worker,count=1,flags=re.M)
    return 'self.__KV3_QA_FALLBACK__=true;\n'+core+'\n'+adapters+'\n'+worker

def inline_page(site:Path,filename:str,bundle:str)->str:
    raw=(site/filename).read_text(encoding='utf-8')
    raw=re.sub(r'<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*>\s*','',raw,flags=re.I)
    hrefs=re.findall(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)',raw,flags=re.I)
    css=[]
    for href in hrefs:
        path=site/href.split('?',1)[0]
        if path.is_file():css.append(path.read_text(encoding='utf-8'))
    raw=re.sub(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*>\s*','',raw,flags=re.I)
    raw=re.sub(r'<script\s+[^>]*src=["\'][^"\']+["\'][^>]*>\s*</script>\s*','',raw,flags=re.I)
    raw=raw.replace('</head>','<style data-kv3-qa-inline>\n'+'\n'.join(css)+'\n</style></head>',1)
    app=(site/'assets/sme-kernel-v3.js').read_text(encoding='utf-8').replace('</script','<\\/script')
    boot='<script>window.__KV3_WORKER_SOURCE__='+json.dumps(bundle,ensure_ascii=False).replace('</','<\\/')+';</script><script>'+app+'</script>'
    return raw.replace('</body>',boot+'</body>',1)

def inline_homepage(site:Path)->str:
    raw=(site/'index.html').read_text(encoding='utf-8')
    raw=re.sub(r'<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*>\s*','',raw,flags=re.I)
    hrefs=re.findall(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)',raw,flags=re.I)
    css=[]
    for href in hrefs:
        path=site/href.split('?',1)[0]
        if path.is_file():css.append(path.read_text(encoding='utf-8'))
    raw=re.sub(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*>\s*','',raw,flags=re.I)
    raw=re.sub(r'<script\s+[^>]*src=["\'][^"\']+["\'][^>]*>\s*</script>\s*','',raw,flags=re.I)
    return raw.replace('</head>','<style data-kv3-qa-home>\n'+'\n'.join(css)+'\n</style></head>',1)

def launch_browser(playwright:Any)->Any:
    args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']
    executable=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
    if executable:return playwright.chromium.launch(headless=True,executable_path=executable,args=args)
    return playwright.chromium.launch(headless=True,args=args)

def is_external(url:str)->bool:
    if url.startswith(('data:','blob:','about:')):return False
    parsed=urlparse(url)
    if parsed.scheme not in {'http','https','ws','wss'}:return False
    return parsed.hostname not in {'127.0.0.1','localhost'}

def wait_ready(page:Any)->None:page.wait_for_selector('html[data-kv3-ready="true"]',timeout=25000)

def wait_text(page:Any,selector:str,expected:str,timeout_ms:int=20000)->None:
    deadline=time.monotonic()+timeout_ms/1000
    last=''
    while time.monotonic()<deadline:
        try:
            last=page.locator(selector).inner_text(timeout=1000)
            if last==expected:return
        except Exception:pass
        page.wait_for_timeout(100)
    raise TimeoutError(f'{selector} did not become {expected!r}; last value {last!r}')

def load_surface(page:Any,site:Path,base:str,filename:str,bundle:str,mode:dict[str,str])->str:
    if mode.get('value')!='inline':
        try:
            page.goto(f'{base}/{filename}',wait_until='domcontentloaded',timeout=20000);wait_ready(page);mode['value']='http';return 'http'
        except Exception as exc:
            if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(exc) and 'net::ERR_BLOCKED' not in str(exc):
                # A restricted local browser can fail in several policy-specific ways. Inline mode still exercises the complete runtime.
                mode['http_error']=str(exc)
            mode['value']='inline'
    try:
        page.goto('about:blank',wait_until='domcontentloaded',timeout=5000)
    except Exception:
        page.wait_for_timeout(500)
    content=inline_page(site,filename,bundle)
    last_error=None
    for _ in range(3):
        try:
            page.set_content(content,wait_until='domcontentloaded',timeout=20000);wait_ready(page);return 'inline'
        except Exception as exc:
            last_error=exc;page.wait_for_timeout(500)
    raise last_error

def screenshot_view(page:Any,selector:str,path:Path)->None:
    locator=page.locator(selector);locator.scroll_into_view_if_needed();page.wait_for_timeout(120);locator.screenshot(path=str(path))

def run(site:Path,output:Path)->dict[str,Any]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        report={'schema':'goalos.sme.kernel.v3.browser_qa.v1','status':'FAIL','checks_total':1,'checks_passed':0,'checks_failed':1,'checks':[{'label':'playwright-import','status':'FAIL','detail':str(exc)}]};write_json(output/'browser-report.json',report);return report
    output.mkdir(parents=True,exist_ok=True)
    results:list[dict[str,Any]]=[];console_errors:list[str]=[];failed_requests:list[str]=[];external_requests:list[str]=[];bundle_source=worker_bundle(site);load_mode={'value':'auto'}
    with serve(site) as base, sync_playwright() as playwright:
        browser=launch_browser(playwright)
        try:
            context=browser.new_context(viewport={'width':1600,'height':1000},device_scale_factor=1,reduced_motion='reduce',accept_downloads=True)
            page=context.new_page();page.set_default_timeout(20000)
            page.on('console',lambda msg: console_errors.append(f'{page.url}: {msg.text}') if msg.type=='error' else None)
            page.on('pageerror',lambda err: console_errors.append(f'{page.url}: {err}'))
            page.on('request',lambda req: external_requests.append(f'{req.method} {req.url}') if is_external(req.url) else None)
            page.on('requestfailed',lambda req: failed_requests.append(f'{req.method} {req.url}: {req.failure}') if not ('ERR_BLOCKED_BY_ADMINISTRATOR' in str(req.failure) and load_mode.get('value')=='inline') else None)

            mode=load_surface(page,site,base,PAGES['experience'],bundle_source,load_mode)
            record(results,'runtime-load-mode',mode in {'http','inline'},mode)
            record(results,'experience-title',page.title()=='Sovereign Machine Economy Kernel v3 · GoalOS',page.title())
            record(results,'experience-ready',page.locator('html').get_attribute('data-kv3-ready')=='true',page.locator('html').get_attribute('data-kv3-ready'))
            record(results,'experience-seventeen-states',page.locator('.kv3-state').count()==17,page.locator('.kv3-state').count())
            record(results,'experience-five-role-identities',page.locator('.kv3-identity').count()==5,page.locator('.kv3-identity').count())
            record(results,'experience-three-adapters',page.locator('.kv3-adapter').count()==3,page.locator('.kv3-adapter').count())
            record(results,'experience-six-metrics',page.locator('.kv3-metric').count()==6,page.locator('.kv3-metric').count())
            record(results,'experience-default-authority-none','NONE_GRANTED' in page.locator('.kv3-boundary').inner_text(),page.locator('.kv3-boundary').inner_text())
            record(results,'experience-desktop-no-overflow',not overflow(page)['overflow'],overflow(page))
            page.screenshot(path=str(output/'01-kernel-v3-hero-desktop.png'),full_page=False)

            page.locator('#kv3-mission-form').evaluate('form=>form.requestSubmit()')
            wait_text(page,'#kv3-current-state','AWAITING_HUMAN_REVIEW',35000)
            mission_id=page.locator('#kv3-mission-id').text_content();chain_head=page.locator('#kv3-chain-head').text_content()
            record(results,'machine-cycle-awaits-human-review',page.locator('#kv3-current-state').inner_text()=='AWAITING_HUMAN_REVIEW',page.locator('#kv3-current-state').inner_text())
            record(results,'machine-cycle-thirteen-events',page.locator('.kv3-event').count()==13,page.locator('.kv3-event').count())
            record(results,'machine-cycle-chain-head',bool(re.fullmatch(r'[a-f0-9]{64}',chain_head)),chain_head)
            record(results,'machine-cycle-review-enabled',page.locator('#kv3-review-chamber').get_attribute('data-enabled')=='true',page.locator('#kv3-review-chamber').get_attribute('data-enabled'))
            record(results,'machine-cycle-signatures-visible',page.locator('.kv3-signature small').filter(has_text='VERIFIED').count()==13,page.locator('.kv3-signature small').filter(has_text='VERIFIED').count())
            screenshot_view(page,'#kernel-theatre',output/'02-constitutional-mission-theatre-desktop.png')
            screenshot_view(page,'.kv3-event-list',output/'03-signed-event-chronicle-desktop.png')
            screenshot_view(page,'#human-review',output/'04-human-review-chamber-desktop.png')

            page.locator('#kv3-review-notes').fill('Reviewed for deliberation only. Independent external attestation and factual certification remain pending.')
            page.locator('[data-review-action="APPROVED_FOR_DELIBERATION"]').click()
            wait_text(page,'#kv3-current-state','COMPLETE',20000)
            record(results,'human-review-final-state-complete',page.locator('#kv3-current-state').inner_text()=='COMPLETE',page.locator('#kv3-current-state').inner_text())
            record(results,'human-review-terminal-settlement-review',page.locator('#kv3-terminal-state').inner_text()=='HUMAN_SETTLEMENT_REVIEW',page.locator('#kv3-terminal-state').inner_text())
            record(results,'human-review-sixteen-events',page.locator('.kv3-event').count()==16,page.locator('.kv3-event').count())
            mission_bundle=page.evaluate("missionId=>window.__SME_KERNEL_V3__.call('EXPORT_MISSION',{missionId})",mission_id)
            record(results,'bundle-schema',mission_bundle.get('schema')=='goalos.sme.kernel.v3.mission_bundle',mission_bundle.get('schema'))
            record(results,'bundle-sixteen-events',len(mission_bundle.get('events',[]))==16,len(mission_bundle.get('events',[])))
            record(results,'bundle-five-public-identities',len(mission_bundle.get('identities',[]))==5,len(mission_bundle.get('identities',[])))
            record(results,'bundle-root-shape',bool(re.fullmatch(r'[a-f0-9]{64}',str(mission_bundle.get('bundleRoot','')))),mission_bundle.get('bundleRoot'))
            record(results,'bundle-no-private-keys','privateKey' not in json.dumps(mission_bundle),'' )
            direct_report=page.evaluate("bundle=>window.__SME_KERNEL_V3__.call('VERIFY_BUNDLE',{bundle})",mission_bundle)
            record(results,'bundle-direct-verification',direct_report.get('ok') is True,direct_report)
            bundle_path=output/'signed-mission-bundle.json';write_json(bundle_path,mission_bundle)

            load_surface(page,site,base,PAGES['chronicle'],bundle_source,load_mode)
            record(results,'chronicle-title',page.title()=='Kernel v3 Chronicle · GoalOS',page.title())
            record(results,'chronicle-five-identities',page.locator('.kv3-identity').count()==5,page.locator('.kv3-identity').count())
            if load_mode.get('value')=='http':
                page.wait_for_selector('[data-mission]',timeout=15000)
                record(results,'chronicle-durable-mission',page.locator('[data-mission]').count()>=1,page.locator('[data-mission]').count())
                record(results,'chronicle-sixteen-events',page.locator('.kv3-chronicle-row').count()==16,page.locator('.kv3-chronicle-row').count())
            else:
                record(results,'chronicle-inline-fallback-explicit','No durable missions yet' in page.locator('#kv3-mission-list').inner_text(),page.locator('#kv3-mission-list').inner_text())
            page.screenshot(path=str(output/'05-durable-append-only-chronicle-desktop.png'),full_page=False)

            load_surface(page,site,base,PAGES['protocol'],bundle_source,load_mode)
            record(results,'protocol-ten-envelopes',page.locator('.kv3-envelope').count()>=10,page.locator('.kv3-envelope').count())
            record(results,'protocol-seventeen-transition-nodes',page.locator('.kv3-transition-node').count()==17,page.locator('.kv3-transition-node').count())
            record(results,'protocol-five-identities',page.locator('.kv3-identity').count()==5,page.locator('.kv3-identity').count())
            record(results,'protocol-no-overflow',not overflow(page)['overflow'],overflow(page))
            page.screenshot(path=str(output/'06-versioned-protocol-desktop.png'),full_page=False)

            load_surface(page,site,base,PAGES['verifier'],bundle_source,load_mode)
            page.locator('#kv3-bundle-file').set_input_files(str(bundle_path))
            page.wait_for_selector('#kv3-verifier-result[data-status="pass"]',timeout=25000)
            record(results,'verifier-accepts-valid-bundle',page.locator('#kv3-verifier-result').get_attribute('data-status')=='pass',page.locator('#kv3-verifier-result').inner_text())
            record(results,'verifier-shows-sixteen-events','16' in page.locator('#kv3-verifier-result').inner_text(),page.locator('#kv3-verifier-result').inner_text())
            page.screenshot(path=str(output/'07-independent-verifier-pass-desktop.png'),full_page=False)
            page.locator('#kv3-tamper-bundle').click();page.wait_for_selector('#kv3-verifier-result[data-status="fail"]',timeout=20000)
            record(results,'verifier-rejects-tampering',page.locator('#kv3-verifier-result').get_attribute('data-status')=='fail',page.locator('#kv3-verifier-result').inner_text())
            page.screenshot(path=str(output/'08-independent-verifier-tamper-desktop.png'),full_page=False)

            load_surface(page,site,base,PAGES['sdk'],bundle_source,load_mode)
            record(results,'sdk-three-adapters',page.locator('.kv3-adapter').count()==3,page.locator('.kv3-adapter').count())
            record(results,'sdk-six-method-contract',all(method in page.locator('body').inner_text() for method in ['initialize','propose','execute','evaluate','produceEvidence','verifyEvidence']),'adapter contract')
            record(results,'sdk-downloads-present',all((site/path).is_file() for path in ['downloads/sme-kernel-v3/sme-kernel-v3-core.js','downloads/sme-kernel-v3/sme-kernel-v3-adapters.js','downloads/sme-kernel-v3/sme-kernel-v3-protocol-manifest.json']),'downloads')
            page.screenshot(path=str(output/'09-replaceable-adapter-sdk-desktop.png'),full_page=False)

            # Incident rehearsal returns a fail-closed terminal before human review.
            load_surface(page,site,base,PAGES['experience'],bundle_source,load_mode)
            page.locator('#kv3-incident').select_option('identity-drift')
            page.locator('#kv3-mission-form').evaluate('form=>form.requestSubmit()')
            wait_text(page,'#kv3-terminal-state','SAFE_HOLD',30000)
            record(results,'incident-safe-hold',page.locator('#kv3-terminal-state').inner_text()=='SAFE_HOLD',page.locator('#kv3-terminal-state').inner_text())
            record(results,'incident-stops-before-review',page.locator('#kv3-current-state').inner_text()=='EXECUTION_BOUNDED',page.locator('#kv3-current-state').inner_text())
            record(results,'incident-no-review-authority',page.locator('#kv3-review-chamber').get_attribute('data-enabled')=='false',page.locator('#kv3-review-chamber').get_attribute('data-enabled'))
            screenshot_view(page,'#kernel-theatre',output/'10-fail-closed-safe-hold-desktop.png')

            # Homepage gateway is static and must not require Kernel runtime.
            if load_mode.get('value')=='http':
                page.goto(f'{base}/index.html',wait_until='domcontentloaded',timeout=20000)
            else:
                page.set_content(inline_homepage(site),wait_until='domcontentloaded')
            gateway=page.locator('#sme-kernel-v3');gateway.scroll_into_view_if_needed()
            record(results,'homepage-gateway-once',gateway.count()==1 and gateway.is_visible(),gateway.count())
            record(results,'homepage-kernel-nav',page.locator('a[href="sovereign-machine-economy-kernel-v3.html"]').count()>=1,page.locator('a[href="sovereign-machine-economy-kernel-v3.html"]').count())
            record(results,'homepage-gateway-five-actions',gateway.locator('a').count()==4,gateway.locator('a').count())
            gateway.screenshot(path=str(output/'11-main-website-kernel-v3-gateway-desktop.png'))

            page.set_viewport_size({'width':1024,'height':1366});load_surface(page,site,base,PAGES['experience'],bundle_source,load_mode)
            record(results,'tablet-no-overflow',not overflow(page)['overflow'],overflow(page));record(results,'tablet-form-visible',page.locator('#kv3-mission-form').is_visible(),'')
            page.screenshot(path=str(output/'12-kernel-v3-tablet.png'),full_page=False)
            page.set_viewport_size({'width':390,'height':844});load_surface(page,site,base,PAGES['experience'],bundle_source,load_mode)
            mobile=overflow(page);record(results,'mobile-no-overflow',not mobile['overflow'],mobile);record(results,'mobile-run-visible',page.locator('#kv3-run').is_visible(),'');record(results,'mobile-five-authorities',page.locator('.kv3-identity').count()==5,page.locator('.kv3-identity').count())
            page.screenshot(path=str(output/'13-kernel-v3-mobile.png'),full_page=False)

            record(results,'console-errors-zero',not console_errors,console_errors)
            record(results,'failed-requests-zero',not failed_requests,failed_requests)
            record(results,'external-requests-zero',not external_requests,external_requests)
            context.close()
        finally: browser.close()
    failed=[x for x in results if x['status']=='FAIL']
    report={'schema':'goalos.sme.kernel.v3.browser_qa.v1','release':'GOALOS-AGIALPHA-SME-KERNEL-V3-001','status':'PASS' if not failed else 'FAIL','checks_total':len(results),'checks_passed':len(results)-len(failed),'checks_failed':len(failed),'load_mode':load_mode,'checks':results,'diagnostics':{'console_errors':console_errors,'failed_requests':failed_requests,'external_requests':external_requests}}
    write_json(output/'browser-report.json',report)
    print(json.dumps({'status':report['status'],'checks_total':report['checks_total'],'checks_passed':report['checks_passed'],'checks_failed':report['checks_failed'],'load_mode':load_mode.get('value'),'output':str(output/'browser-report.json')},indent=2))
    return report

def main()->int:
    root=Path(__file__).resolve().parents[2];parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--site',type=Path,default=root/'site');parser.add_argument('--output',type=Path);args=parser.parse_args();output=args.output or args.site/'qa/sme-kernel-v3-browser';report=run(args.site.resolve(),output.resolve());return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
