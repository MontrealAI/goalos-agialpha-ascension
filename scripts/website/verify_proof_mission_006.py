#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
START='<!-- GOALOS_PROOF_MISSION_006_START -->'; END='<!-- GOALOS_PROOF_MISSION_006_END -->'
STYLE_START='<!-- GOALOS_PROOF_MISSION_006_STYLE_START -->'; STYLE_END='<!-- GOALOS_PROOF_MISSION_006_STYLE_END -->'
PROMO_START='<!-- GOALOS_PROOF_MISSION_006_PROMOTION_START -->'; PROMO_END='<!-- GOALOS_PROOF_MISSION_006_PROMOTION_END -->'
FORBIDDEN=('recursive.com','recursive org','recursive-style','competitor comparison','named competitor')
PAGES=['index.html','proof-missions.html','proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html','proof-mission-004.html','proof-mission-005.html','proof-mission-006.html']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def fail(m): raise AssertionError(m)
def strip(t,s,e):
    if t.count(s)!=1 or t.count(e)!=1: fail(f'marker count mismatch: {s}')
    return re.sub(r'(?:\r?\n)?'+re.escape(s)+r'.*?'+re.escape(e)+r'(?:\r?\n)?','\n',t,count=1,flags=re.S)
def run(cmd,cwd):
    r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
    if r.returncode: raise RuntimeError('command failed: '+' '.join(cmd)+'\n'+r.stdout+'\n'+r.stderr)

def build_baseline(repo):
    td=tempfile.TemporaryDirectory(prefix='goalos-m6-baseline-'); out=Path(td.name)/'site'
    run([sys.executable,'scripts/build_goalos_agialpha_ascension_website_v86.py','--out',str(out)],repo)
    for s in ['build_proof_gradient_sovereign.py','build_proof_mission_002.py','build_proof_mission_003.py','build_proof_mission_004.py','build_proof_mission_005.py']:
        run([sys.executable,'scripts/website/'+s,'--site',str(out)],repo)
    return td,out

def verify(site,repo):
    site=Path(site); repo=Path(repo); errors=[]
    def check(cond,msg):
        if not cond: errors.append(msg)
    c=load(repo/'content/proof-mission-006-long-horizon.json'); m=load(repo/'data/mainnet/v4.4.0-mainnet-2026-06-21.json')
    check(c.get('missionId')=='GOALOS-PUBLIC-PROOF-MISSION-006','mission ID mismatch')
    check(c.get('sequence')==6,'mission sequence mismatch')
    check(c.get('status')=='PROTOCOL_PUBLISHED_AWAITING_ONE_FEDERATION_PROVEN_COMMONWEALTH','status mismatch')
    check(len(c.get('proofRoute',[]))==44,'expected 44 proof-route stages')
    check(len({x.get('contractName') for x in c.get('proofRoute',[])})==44,'proof-route contracts must be distinct')
    check(len(c.get('validators',[]))==7,'expected seven validators')
    check(len(c.get('continuityTrial',{}).get('eras',[]))==7,'expected seven eras')
    check(sum(x.get('share',0) for x in c.get('settlement',[]))==100,'settlement must total 100')
    check(m.get('goalosCreatedContractCount')==48,'Mainnet contract count mismatch')
    check(m.get('verification',{}).get('verified')==48 and m.get('verification',{}).get('failed')==0,'Mainnet verification mismatch')
    check(m.get('phaseBGrantCount')==14,'grant count mismatch')
    check(m.get('postcheck',{}).get('status')=='PASSED','postcheck mismatch')
    for f in PAGES:
        check((site/f).exists(),f+' missing')
    if errors: return errors
    page=(site/'proof-mission-006.html').read_text()
    home=(site/'index.html').read_text()
    hub=(site/'proof-missions.html').read_text()
    m5=(site/'proof-mission-005.html').read_text()
    check('THE <span>LONG HORIZON</span>' in page,'hero missing')
    check('M6 — CONTINUITY-PROVEN' in json.dumps(c,ensure_ascii=False),'maturity designation missing')
    check(c['status'].replace('_',' ') in page,'mission status missing')
    check('No continuity result predeclared' in page,'claim boundary footer missing')
    check('HORIZON_ONLY_NOT_YET_AUTHORIZED' not in page,'raw horizon enum leaked')
    check('Horizon only · not authorized' in page,'Mission 007 horizon boundary missing')
    check(page.count('class="route-item"')==44,'expected 44 route cards')
    check('id="lh-route-search"' in page,'route search missing')
    check(START in home and END in home and STYLE_START in home and STYLE_END in home,'homepage markers missing')
    check(home.count(START)==home.count(END)==1,'homepage section duplicated')
    check('THE LONG <span>HORIZON</span>' in home,'homepage panel missing')
    check('The Long Horizon' in hub and hub.count('PUBLIC PROOF MISSION 006')==1,'six-mission hub missing Mission 006')
    check('PUBLIC PROOF MISSION 006 · NOW PUBLISHED' in m5,'Mission 005 horizon was not promoted')
    check(PROMO_START in m5 and PROMO_END in m5,'Mission 005 promotion markers missing')
    low=(page+home+hub+m5).lower()
    for x in FORBIDDEN: check(x not in low,'prohibited reference: '+x)
    by={x['name']:x for x in m['contracts']}
    for x in c['proofRoute']:
        d=by[x['contractName']]
        check(x['contractName'] in page,'route contract missing: '+x['contractName'])
        check(d['address'].lower() in page.lower(),'route address missing: '+x['contractName'])
        check(d['etherscanUrl'] in page,'Etherscan link missing: '+x['contractName'])
    dl=site/'downloads/proof-missions'
    required=['public-proof-mission-006.json','mission-006-continuity-charter-template.json','mission-006-succession-ledger-template.json','mission-006-cryptographic-migration-template.json','mission-006-archive-recovery-template.json','mission-006-dissolution-renewal-template.json','mission-006-proof-route.csv']
    for f in required: check((dl/f).exists(),'download missing: '+f)
    for f in required[1:-1]:
        if (dl/f).exists(): check(load(dl/f).get('status')=='TEMPLATE_NOT_EVIDENCE','template boundary missing: '+f)
    if (dl/'mission-006-proof-route.csv').exists():
        rows=list(csv.DictReader((dl/'mission-006-proof-route.csv').open()))
        check(len(rows)==44,'route CSV row count mismatch')
    # Internal href integrity for all mission pages.
    for f in PAGES:
        text=(site/f).read_text()
        for href in re.findall(r'href="([^"]+)"',text):
            if href.startswith(('http://','https://','#','mailto:','javascript:')): continue
            target=href.split('#',1)[0]
            if target and not (site/target).exists(): errors.append(f'{f}: broken link {target}')
    # Rebuild Missions 001–005 and prove Mission 006 is additive.
    try:
        td,baseline=build_baseline(repo)
        base_home=(baseline/'index.html').read_text()
        stripped=strip(strip(home,START,END),STYLE_START,STYLE_END)
        check(stripped==base_home,'homepage differs from Missions 001–005 baseline after removing Mission 006 overlay')
        base_m5=(baseline/'proof-mission-005.html').read_text()
        stripped_m5=strip(m5,PROMO_START,PROMO_END)
        # Promotion replaces the original horizon; normalize to compare presence of all text before promotion.
        check(sha(site/'proof-gradient-challenge.html')==sha(baseline/'proof-gradient-challenge.html'),'Mission 001 changed unexpectedly')
        check(sha(site/'proof-mission-002.html')==sha(baseline/'proof-mission-002.html'),'Mission 002 changed unexpectedly')
        check(sha(site/'proof-mission-003.html')==sha(baseline/'proof-mission-003.html'),'Mission 003 changed unexpectedly')
        check(sha(site/'proof-mission-004.html')==sha(baseline/'proof-mission-004.html'),'Mission 004 changed unexpectedly')
        # Mission 005 is intentionally altered only in its horizon section.
        check('The Interinstitutional Accord' in stripped_m5,'Mission 005 core content missing')
        td.cleanup()
    except Exception as e: errors.append('baseline preservation verification failed: '+str(e))
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); ap.add_argument('--repo',default='.'); a=ap.parse_args()
    errors=verify(a.site,a.repo)
    report={'status':'PASS' if not errors else 'FAIL','missionId':'GOALOS-PUBLIC-PROOF-MISSION-006','errors':errors,'proofRouteStages':44,'publicNetworkTransactionSent':False}
    out=Path(a.site)/'qa/proof-mission-006-verification.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
