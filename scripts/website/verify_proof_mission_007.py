#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
START='<!-- GOALOS_PROOF_MISSION_007_START -->'; END='<!-- GOALOS_PROOF_MISSION_007_END -->'
STYLE_START='<!-- GOALOS_PROOF_MISSION_007_STYLE_START -->'; STYLE_END='<!-- GOALOS_PROOF_MISSION_007_STYLE_END -->'
PROMO_START='<!-- GOALOS_PROOF_MISSION_007_PROMOTION_START -->'; PROMO_END='<!-- GOALOS_PROOF_MISSION_007_PROMOTION_END -->'
FORBIDDEN=('recursive.com','recursive org','recursive-style','named competitor')
PAGES=['index.html','proof-missions.html','proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html','proof-mission-004.html','proof-mission-005.html','proof-mission-006.html','proof-mission-007.html']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def fail(m): raise AssertionError(m)
def strip(t,s,e):
 if t.count(s)!=1 or t.count(e)!=1: fail(f'marker count mismatch: {s}')
 return re.sub(r'(?:\r?\n)?'+re.escape(s)+r'.*?'+re.escape(e)+r'(?:\r?\n)?','\n',t,count=1,flags=re.S)
def run(cmd,cwd):
 r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
 if r.returncode: raise RuntimeError('command failed: '+' '.join(cmd)+'\n'+r.stdout+'\n'+r.stderr)

def build_baseline(repo):
 td=tempfile.TemporaryDirectory(prefix='goalos-m7-baseline-'); out=Path(td.name)/'site'
 run([sys.executable,'scripts/build_goalos_agialpha_ascension_website_v86.py','--out',str(out)],repo)
 for s in ['build_proof_gradient_sovereign.py','build_proof_mission_002.py','build_proof_mission_003.py','build_proof_mission_004.py','build_proof_mission_005.py','build_proof_mission_006.py']:
  run([sys.executable,'scripts/website/'+s,'--site',str(out)],repo)
 return td,out

def verify(site,repo):
 site=Path(site); repo=Path(repo); errors=[]
 def check(cond,msg):
  if not cond: errors.append(msg)
 c=load(repo/'content/proof-mission-007-civilizational-covenant.json'); m=load(repo/'data/mainnet/v4.4.0-mainnet-2026-06-21.json')
 check(c.get('missionId')=='GOALOS-PUBLIC-PROOF-MISSION-007','mission ID mismatch'); check(c.get('sequence')==7,'mission sequence mismatch')
 check(c.get('status')=='PROTOCOL_PUBLISHED_AWAITING_THREE_CONTINUITY_PROVEN_COMMONWEALTHS','status mismatch')
 check(len(c.get('proofRoute',[]))==48,'expected 48 proof-route stages'); check(len({x.get('contractName') for x in c.get('proofRoute',[])})==48,'route contracts must be distinct')
 check(len(c.get('validators',[]))==8,'expected eight validators'); check(len(c.get('stewardshipTrial',{}).get('covenants',[]))==8,'expected eight covenants')
 check(sum(x.get('share',0) for x in c.get('settlement',[]))==100,'settlement must total 100')
 check(m.get('goalosCreatedContractCount')==48,'Mainnet contract count mismatch'); check(m.get('verification',{}).get('verified')==48 and m.get('verification',{}).get('failed')==0,'Mainnet verification mismatch')
 check(m.get('phaseBGrantCount')==14,'grant count mismatch'); check(m.get('postcheck',{}).get('status')=='PASSED','postcheck mismatch')
 for f in PAGES: check((site/f).is_file() and (site/f).stat().st_size>0,f+' missing')
 if errors: return errors
 page=(site/'proof-mission-007.html').read_text(encoding='utf-8'); home=(site/'index.html').read_text(encoding='utf-8'); hub=(site/'proof-missions.html').read_text(encoding='utf-8'); m6=(site/'proof-mission-006.html').read_text(encoding='utf-8')
 check('THE <span>CIVILIZATIONAL COVENANT</span>' in page,'hero missing'); check('M7 — STEWARDSHIP-PROVEN' in json.dumps(c,ensure_ascii=False),'maturity missing')
 check(c['status'].replace('_',' ') in page,'mission status missing'); check('No civilizational stewardship result predeclared' in page,'claim footer missing')
 check('HORIZON_ONLY_NOT_YET_AUTHORIZED' not in page,'raw horizon enum leaked'); check('Horizon only · not authorized' in page,'Mission 008 horizon boundary missing')
 check(page.count('class="cv-route route-item"')==48,'expected 48 route cards'); check('id="cv-route-search"' in page,'route search missing')
 check(START in home and END in home and STYLE_START in home and STYLE_END in home,'homepage markers missing'); check(home.count(START)==home.count(END)==1,'homepage panel duplicated')
 check('THE CIVILIZATIONAL <span>COVENANT</span>' in home,'homepage panel missing'); check('The Civilizational Covenant' in hub and hub.count('PUBLIC PROOF MISSION 007')==1,'hub missing Mission 007')
 check('PUBLIC PROOF MISSION 007 · NOW PUBLISHED' in m6,'Mission 006 horizon not promoted'); check(PROMO_START in m6 and PROMO_END in m6,'Mission 006 promotion markers missing')
 low=(page+home+hub+m6).lower()
 for x in FORBIDDEN: check(x not in low,'prohibited reference: '+x)
 by={x['name']:x for x in m['contracts']}
 for x in c['proofRoute']:
  d=by[x['contractName']]; check(x['contractName'] in page,'route contract missing: '+x['contractName']); check(d['address'].lower() in page.lower(),'route address missing: '+x['contractName']); check(d['etherscanUrl'] in page,'Etherscan link missing: '+x['contractName'])
 dl=site/'downloads/proof-missions'; required=['public-proof-mission-007.json','mission-007-covenant-charter-template.json','mission-007-public-good-ledger-template.json','mission-007-rights-exit-register-template.json','mission-007-externality-accounting-template.json','mission-007-renewal-dissolution-template.json','mission-007-proof-route.csv']
 for f in required: check((dl/f).exists(),'download missing: '+f)
 for f in required[1:-1]:
  if (dl/f).exists(): check(load(dl/f).get('status')=='TEMPLATE_NOT_EVIDENCE','template boundary missing: '+f)
 if (dl/'mission-007-proof-route.csv').exists(): check(len(list(csv.DictReader((dl/'mission-007-proof-route.csv').open())))==48,'route CSV row count mismatch')
 for f in PAGES:
  text=(site/f).read_text(encoding='utf-8')
  for href in re.findall(r'href="([^"]+)"',text):
   if href.startswith(('http://','https://','#','mailto:','javascript:')): continue
   target=href.split('#',1)[0]
   if target and not (site/target).exists(): errors.append(f'{f}: broken link {target}')
 try:
  td,baseline=build_baseline(repo); base_home=(baseline/'index.html').read_text(encoding='utf-8'); stripped=strip(strip(home,START,END),STYLE_START,STYLE_END); check(stripped==base_home,'homepage differs from Missions 001–006 baseline after removing Mission 007 overlay')
  for f in ['proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html','proof-mission-004.html','proof-mission-005.html']:
   check(sha(site/f)==sha(baseline/f),f+' changed unexpectedly')
  base_m6=(baseline/'proof-mission-006.html').read_text(encoding='utf-8')
  match=re.search(r'<article class="horizon"><strong>MISSION 007 HORIZON</strong>.*?</article>',base_m6,re.S)
  check(match is not None,'baseline Mission 006 horizon not found')
  if match:
   normalized=re.sub(re.escape(PROMO_START)+r'.*?'+re.escape(PROMO_END),match.group(0),m6,count=1,flags=re.S)
   check(normalized==base_m6,'Mission 006 changed outside the promoted horizon')
  td.cleanup()
 except Exception as e: errors.append('baseline preservation verification failed: '+str(e))
 return errors

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); ap.add_argument('--repo',default='.'); a=ap.parse_args(); errors=verify(a.site,a.repo)
 report={'status':'PASS' if not errors else 'FAIL','missionId':'GOALOS-PUBLIC-PROOF-MISSION-007','errors':errors,'proofRouteStages':48,'publicNetworkTransactionSent':False}
 out=Path(a.site)/'qa/proof-mission-007-verification.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
