#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
from urllib.parse import unquote

PAGES=['first-real-loop.html','first-real-loop-architecture.html','first-real-loop-docket.html']
REQUIRED=[*PAGES,'assets/first-real-loop/first-real-loop.css','assets/first-real-loop/first-real-loop.js','downloads/first-real-loop/first-real-loop-evidence-docket.json','downloads/first-real-loop/first-real-loop-artifact-ledger.json','downloads/first-real-loop/first-real-loop-replay-manifest.json','downloads/first-real-loop/first-real-loop-executive-brief.md','qa/first-real-loop-build.json']
HOME_START='<!-- GOALOS_FIRST_REAL_LOOP_START -->'
HOME_END='<!-- GOALOS_FIRST_REAL_LOOP_END -->'
HOME_STYLE_START='<!-- GOALOS_FIRST_REAL_LOOP_STYLE_START -->'
HOME_STYLE_END='<!-- GOALOS_FIRST_REAL_LOOP_STYLE_END -->'


def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,v): p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def canonical(v): return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def local_targets(raw): return re.findall(r'(?:href|src)=["\']([^"\']+)["\']',raw,re.I)


def verify(site: Path, content_path: Path, schema_path: Path):
    errors=[];warnings=[];checks=0;passed=0
    def check(condition,label):
        nonlocal checks,passed
        checks+=1
        if condition: passed+=1
        else: errors.append(label)
    def warn(condition,label):
        if not condition: warnings.append(label)
    for rel in REQUIRED:
        p=site/rel;check(p.is_file() and p.stat().st_size>0,f'missing or empty required output: {rel}')
    index=(site/'index.html').read_text(encoding='utf-8',errors='ignore')
    check(index.count(HOME_START)==1,'homepage gateway start marker must appear once')
    check(index.count(HOME_END)==1,'homepage gateway end marker must appear once')
    check(index.count(HOME_STYLE_START)==1,'homepage style marker must appear once')
    check(index.count(HOME_STYLE_END)==1,'homepage style end marker must appear once')
    check(index.count('data-goalos-feature="first-real-loop"')==1,'homepage gateway must be unique')
    check('first-real-loop.html' in index,'homepage must link to experience')
    check('first-real-loop-architecture.html' in index,'homepage must link to architecture')
    check('first-real-loop-docket.html' in index,'homepage must link to docket')
    sitemap=(site/'sitemap.xml').read_text(encoding='utf-8',errors='ignore')
    for page in PAGES:
        check(sitemap.count(page)==1,f'sitemap entry must appear once: {page}')
    page_words={}
    for page in PAGES:
        raw=(site/page).read_text(encoding='utf-8',errors='ignore');low=raw.lower()
        check('<!doctype html>' in low,f'{page}: missing doctype')
        check('goalos-v86-preserve.css' in raw,f'{page}: missing v86 CSS')
        check('goalos-v86-dynamic-ai.js' in raw,f'{page}: missing v86 dynamic script')
        check('goalos-v86-critical' in raw,f'{page}: missing critical fallback')
        check('assets/first-real-loop/first-real-loop.css' in raw,f'{page}: missing feature CSS')
        check('assets/first-real-loop/first-real-loop.js' in raw,f'{page}: missing feature JS')
        check('GoalOS AGIALPHA Ascension' in raw,f'{page}: product identity missing')
        check('HUMAN_REVIEW_REQUIRED' in raw or 'Human review required' in raw,f'{page}: human boundary missing')
        check('NONE_GRANTED' in raw or 'authority withheld' in low,f'{page}: authority boundary missing')
        check('id="frl-data"' in raw,f'{page}: embedded source data missing')
        check('<script type="application/json" id="frl-data">' in raw,f'{page}: data script must be non-executable JSON')
        words=len(re.findall(r'\b[\wαΑ-]+\b',re.sub(r'<[^>]+>',' ',raw)))
        page_words[page]=words;check(words>=500,f'{page}: too little explanatory content ({words} words)')
        for target in local_targets(raw):
            if not target or target.startswith(('#','mailto:','tel:','javascript:','data:','http://','https://')): continue
            clean=unquote(target.split('#')[0].split('?')[0])
            if not clean: continue
            dest=(site/clean.lstrip('/')) if clean.startswith('/') else (site/page).parent/clean
            check(dest.exists(),f'{page}: broken local target {target}')
        check('fetch(' not in low,f'{page}: inline network call prohibited')
        check('window.ethereum' not in low,f'{page}: wallet API prohibited')
    exp=(site/'first-real-loop.html').read_text(encoding='utf-8')
    for phrase in ['THE FIRST','REAL LOOP','Where intelligence earns memory.','66.67%','5 / 5','12','Run the governed loop','No Evidence Docket, no promotion.']:
        check(phrase in exp,f'experience page missing: {phrase}')
    check(exp.count('class="frl-phase"')==8,'experience must expose eight proof phases')
    check(exp.count('class="frl-job')>=5,'experience must expose five jobs')
    check(exp.count('<article class="frl-intervention ') == 4,'experience must expose four accepted interventions')
    arch=(site/'first-real-loop-architecture.html').read_text(encoding='utf-8')
    check(arch.count('class="frl-layer ') == 9,'architecture must expose nine layers')
    for phrase in ['Capability ≠ authority.','Nova-Seed','MARK Admissibility Kernel','Human Promotion Boundary','Threat and failure atlas']:
        check(phrase in arch,f'architecture page missing: {phrase}')
    docket_html=(site/'first-real-loop-docket.html').read_text(encoding='utf-8')
    check(docket_html.count('class="frl-ledger-row"')==12,'docket page must expose twelve artifacts')
    for phrase in ['THE EVIDENCE','DOCKET','Run commitment','NOT_ACTIVATED','NOT AUTHORIZED','HUMAN_REVIEW_REQUIRED']:
        check(phrase in docket_html,f'docket page missing: {phrase}')
    js=(site/'assets/first-real-loop/first-real-loop.js').read_text(encoding='utf-8');css=(site/'assets/first-real-loop/first-real-loop.css').read_text(encoding='utf-8')
    for token in ['fetch(','XMLHttpRequest','WebSocket(','window.ethereum','eth_sendTransaction','sendBeacon(']:
        check(token not in js,f'feature JS contains prohibited external/network primitive: {token}')
    for token in ['frl-run','finalState','crypto.subtle','download(','document.body.dataset.runState']:
        check(token in js,f'feature JS missing runtime behavior: {token}')
    check('@media(max-width:540px)' in css,'feature CSS missing mobile breakpoint')
    check('@media(prefers-reduced-motion:reduce)' in css,'feature CSS missing reduced-motion handling')
    check('.frl-home-gateway' in css,'feature CSS missing homepage gateway')
    check('.frl-console' in css,'feature CSS missing runtime console')
    check(len(css)>25000,'feature CSS unexpectedly small')
    docket=load(site/'downloads/first-real-loop/first-real-loop-evidence-docket.json')
    ledger=load(site/'downloads/first-real-loop/first-real-loop-artifact-ledger.json')
    replay=load(site/'downloads/first-real-loop/first-real-loop-replay-manifest.json')
    content=load(content_path);schema=load(schema_path)
    check(schema.get('title')=='GoalOS AGIALPHA Ascension First Real Loop Evidence Docket','schema identity mismatch')
    check(docket.get('schemaVersion')=='1.0.0','docket schema version mismatch')
    check(docket.get('docketId')=='GOALOS-FIRST-REAL-LOOP-DOCKET-001','docket identity mismatch')
    check(docket.get('releaseId')==content.get('releaseId'),'docket/content release mismatch')
    commitment=docket.get('runCommitment','')
    check(bool(re.fullmatch(r'[a-f0-9]{64}',commitment)),'run commitment must be 64 lowercase hex characters')
    unsigned=dict(docket);unsigned.pop('runCommitment',None)
    check(sha_bytes(canonical(unsigned).encode('utf-8'))==commitment,'run commitment does not match canonical docket')
    check(docket.get('mark',{}).get('decision')=='GREEN_FLAMED','MARK decision mismatch')
    check(docket.get('mark',{}).get('averageScore')==4.67,'MARK average mismatch')
    check(len(docket.get('jobs',[]))==5 and all(x.get('success') for x in docket.get('jobs',[])),'docket job record mismatch')
    summary=docket.get('evidenceSummary',{})
    check(summary.get('credibleSources')==12,'source count mismatch')
    check(summary.get('acceptedInterventions')==4,'accepted intervention count mismatch')
    check(summary.get('artifactCount')==12,'artifact count mismatch')
    tc=docket.get('treatmentControl',{})
    check(tc.get('control_yield')==0.3,'control yield mismatch')
    check(tc.get('treatment_yield')==0.5,'treatment yield mismatch')
    check(tc.get('reuse_lift_percent')==66.67,'reuse lift mismatch')
    check(tc.get('hallucination_delta')==0,'hallucination delta mismatch')
    check(tc.get('safety_delta')==0,'safety delta mismatch')
    terminal=docket.get('terminal',{})
    check(terminal.get('state')=='HUMAN_REVIEW_REQUIRED','terminal state mismatch')
    check(terminal.get('authority')=='NONE_GRANTED','terminal authority mismatch')
    check(terminal.get('externalActions')==0,'external action count must be zero')
    check(terminal.get('walletConnections')==0,'wallet connection count must be zero')
    check(terminal.get('networkRequests')==0,'network request count must be zero')
    check(len(ledger.get('artifacts',[]))==12,'artifact ledger count mismatch')
    check(ledger.get('runCommitment')==commitment,'artifact ledger commitment mismatch')
    for item in ledger.get('artifacts',[]):
        check(bool(re.fullmatch(r'[a-f0-9]{64}',item.get('sha256',''))),f'artifact hash malformed: {item.get("id")}')
    check(replay.get('runCommitment')==commitment,'replay manifest commitment mismatch')
    check(replay.get('contentSha256')==sha_bytes(content_path.read_bytes()),'replay content hash mismatch')
    build=load(site/'qa/first-real-loop-build.json')
    check(build.get('status')=='PASS','build report status mismatch')
    check(build.get('unexpectedExistingChanges')==[],'unexpected existing-site changes recorded')
    check(build.get('removedFiles')==[],'removed files recorded')
    check(build.get('existingFilesChanged')==['index.html','site-status.json','sitemap.xml'],'declared integration surfaces mismatch')
    status=load(site/'site-status.json').get('first_real_loop',{})
    check(status.get('run_commitment')==commitment,'site status commitment mismatch')
    check(status.get('terminal_state')=='HUMAN_REVIEW_REQUIRED','site status terminal mismatch')
    check(status.get('authority')=='NONE_GRANTED','site status authority mismatch')
    archives=[str(p.relative_to(site)) for p in site.rglob('*') if p.is_file() and p.suffix.lower() in {'.zip','.7z','.tar','.gz','.rar'}]
    check(not archives,'archive found in public site: '+', '.join(archives[:10]))
    public_blob='\n'.join((site/p).read_text(encoding='utf-8',errors='ignore') for p in PAGES).lower()
    for phrase in ['guaranteed roi','guaranteed return','user funds authorized','production authorized','achieved superintelligence']:
        check(phrase not in public_blob,f'unbounded claim found: {phrase}')
    warn('independent reviewer' in public_blob,'independent review boundary is not prominent')
    report={'status':'PASS' if not errors else 'FAIL','checks':checks,'passed':passed,'failed':len(errors),'errors':errors,'warnings':warnings,'pageWords':page_words,'runCommitment':commitment,'artifactCount':len(ledger.get('artifacts',[])),'externalActions':0,'authority':'NONE_GRANTED','terminalState':'HUMAN_REVIEW_REQUIRED'}
    dump(site/'qa/first-real-loop-static.json',report)
    md=['# GoalOS AGIALPHA Ascension First Real Loop — Static Verification','',f"Status: **{report['status']}**",'',f"Checks: **{passed}/{checks}**",'',f"Run commitment: `{commitment}`",'','## Errors']+[f'- {x}' for x in errors or ['None']]+['','## Warnings']+[f'- {x}' for x in warnings or ['None']]
    (site/'qa/first-real-loop-static.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));return 0 if not errors else 1


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--site',default='site');ap.add_argument('--content',default='content/goalos-first-real-loop.json');ap.add_argument('--schema',default='schemas/goalos-first-real-loop-evidence-docket.schema.json');a=ap.parse_args()
    return verify(Path(a.site),Path(a.content),Path(a.schema))
if __name__=='__main__': raise SystemExit(main())
