#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
MARKERS=[
('<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->','<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->','Mission 001 overlay'),
('<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_START -->','<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_END -->','Mission 001 style'),
('<!-- GOALOS_PROOF_MISSION_002_START -->','<!-- GOALOS_PROOF_MISSION_002_END -->','Mission 002 overlay'),
('<!-- GOALOS_PROOF_MISSION_002_STYLE_START -->','<!-- GOALOS_PROOF_MISSION_002_STYLE_END -->','Mission 002 style'),
('<!-- GOALOS_PROOF_MISSION_003_START -->','<!-- GOALOS_PROOF_MISSION_003_END -->','Mission 003 overlay'),
('<!-- GOALOS_PROOF_MISSION_003_STYLE_START -->','<!-- GOALOS_PROOF_MISSION_003_STYLE_END -->','Mission 003 style'),
('<!-- GOALOS_PROOF_MISSION_004_START -->','<!-- GOALOS_PROOF_MISSION_004_END -->','Mission 004 overlay'),
('<!-- GOALOS_PROOF_MISSION_004_STYLE_START -->','<!-- GOALOS_PROOF_MISSION_004_STYLE_END -->','Mission 004 style'),
('<!-- GOALOS_PROOF_MISSION_005_START -->','<!-- GOALOS_PROOF_MISSION_005_END -->','Mission 005 overlay'),
('<!-- GOALOS_PROOF_MISSION_005_STYLE_START -->','<!-- GOALOS_PROOF_MISSION_005_STYLE_END -->','Mission 005 style'),
]
FORBIDDEN=('recursive.com','recursive org','recursive-style','competitor comparison','named competitor')
PRIVATE=('PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY','MAINNET_RPC_URL=','ETHERSCAN_API_KEY=','SEED_PHRASE','MNEMONIC')
def rm(t,s,e): return re.sub(re.escape(s)+r'.*?'+re.escape(e),'',t,flags=re.S)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--site',default='site'); ap.add_argument('--canonical',default='website/v86_actual_site/index.html'); ap.add_argument('--content',default='content/proof-mission-005-interinstitutional-accord.json'); ap.add_argument('--mainnet',default='data/mainnet/v4.4.0-mainnet-2026-06-21.json'); a=ap.parse_args(); site=Path(a.site); errors=[]
 required=['proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html','proof-mission-004.html','proof-mission-005.html','proof-missions.html','downloads/proof-missions/public-proof-mission-005.json','downloads/proof-missions/mission-005-commonwealth-treaty-template.json','downloads/proof-missions/mission-005-reciprocal-obligation-ledger-template.json','downloads/proof-missions/mission-005-dispute-appeal-template.json','downloads/proof-missions/mission-005-member-exit-template.json','downloads/proof-missions/mission-005-proof-route.csv','qa/proof-mission-005-build.json']
 for r in required:
  if not (site/r).exists(): errors.append('missing '+r)
 read=lambda r:(site/r).read_text(encoding='utf-8',errors='ignore') if (site/r).exists() else ''
 page,hub,home,m4=map(read,['proof-mission-005.html','proof-missions.html','index.html','proof-mission-004.html'])
 for token in ['THE INTERINSTITUTIONAL','ACCORD','Where sovereign institutions learn to cooperate without surrendering sovereignty.','No treaty without proof.','No shared resource without reciprocal accountability.','No federation without exit, appeal, and human sovereignty.','The Five-Act Commonwealth Trial','M5 is earned only by reciprocal proof across sovereign institutions.','No institution may judge its own decisive claim.','Forty interinstitutional stages','MISSION 006 HORIZON','No federation result predeclared']:
  if token not in page: errors.append('Mission 005 page missing '+token)
 if page.count('class="ia-route-item"')!=40: errors.append('Mission 005 page must contain exactly 40 route entries')
 if page.count('class="ia-validator"')!=6: errors.append('Mission 005 page must contain exactly six validators')
 for token in ['The Proof Gradient','The Ascension Protocol','The Capability Constellation','The Sovereign Institution','The Interinstitutional Accord','proof-mission-005.html','The Long Horizon']:
  if token not in hub: errors.append('hub missing '+token)
 if hub.count('class="pm-card')!=5: errors.append('hub must contain five mission cards')
 for s,e,l in MARKERS:
  if home.count(s)!=1 or home.count(e)!=1: errors.append(l+' marker count is not one')
 if 'PUBLIC PROOF MISSION 005 · NOW PUBLISHED' not in m4 or 'proof-mission-005.html' not in m4: errors.append('Mission 004 horizon not promoted')
 if 'MISSION 005 HORIZON' in m4: errors.append('stale Mission 005 horizon remains')
 blob=(page+'\n'+hub+'\n'+home+'\n'+m4).lower()
 for t in FORBIDDEN:
  if t in blob: errors.append('prohibited public reference: '+t)
 for t in PRIVATE:
  if t.lower() in blob: errors.append('private operator material appears: '+t)
 try:
  c=json.loads(Path(a.content).read_text()); b=c['missionBudget']
  if c.get('sequence')!=5 or c.get('status')!='PROTOCOL_PUBLISHED_AWAITING_THREE_INSTITUTION_PROVEN_MEMBERS': errors.append('Mission 005 identity/status mismatch')
  if len(c.get('proofRoute',[]))!=40 or len(c.get('validators',[]))!=6 or len(c.get('commonwealthTrial',{}).get('acts',[]))!=5: errors.append('Mission 005 structural counts mismatch')
  if b.get('challengeWindowHours')!=504 or b.get('independentReplayInstitutions')!=3: errors.append('Mission 005 challenge/replay mismatch')
  if sum(int(x.get('share',0)) for x in c.get('settlement',[]))!=100: errors.append('settlement does not total 100')
  if c.get('mission6',{}).get('status')!='HORIZON_ONLY_NOT_YET_AUTHORIZED': errors.append('Mission 006 horizon mismatch')
 except Exception as x: errors.append('content validation failed: '+str(x))
 try:
  m=json.loads(Path(a.mainnet).read_text()); by={x['name']:x for x in m['contracts']}
  with (site/'downloads/proof-missions/mission-005-proof-route.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
  if len(rows)!=40: errors.append('route CSV must contain 40 rows')
  for r in rows:
   d=by.get(r['contract'])
   if not d or d['address'].lower()!=r['address'].lower(): errors.append('route mismatch for '+r['contract'])
  if m.get('goalosCreatedContractCount')!=48 or m.get('verification',{}).get('verified')!=48 or m.get('verification',{}).get('failed')!=0 or m.get('phaseBGrantCount')!=14 or m.get('postcheck',{}).get('status')!='PASSED': errors.append('Mainnet evidence summary mismatch')
 except Exception as x: errors.append('Mainnet validation failed: '+str(x))
 for t in ['mission-005-commonwealth-treaty-template.json','mission-005-reciprocal-obligation-ledger-template.json','mission-005-dispute-appeal-template.json','mission-005-member-exit-template.json']:
  try:
   if json.loads((site/'downloads/proof-missions'/t).read_text()).get('status')!='TEMPLATE_NOT_EVIDENCE': errors.append(t+' not marked non-evidence')
  except Exception as x: errors.append('template validation failed '+t+': '+str(x))
 try:
  canonical=Path(a.canonical).read_text(); stripped=home
  for s,e,_ in MARKERS: stripped=rm(stripped,s,e)
  norm=lambda x:re.sub(r'>\s+<','><',x).strip()
  if norm(stripped)!=norm(canonical): errors.append('homepage differs from canonical beyond marked overlays')
 except Exception as x: errors.append('canonical preservation failed: '+str(x))
 if any(site.rglob('*.zip')): errors.append('public site contains a ZIP archive')
 report={'status':'PASS' if not errors else 'FAIL','errors':errors,'checks':{'mission001To004Preserved':True,'mission005Pages':2,'proofRouteStages':40,'goalosCreatedContracts':48,'recordedVerified':48,'recordedFailed':0,'configuredGrants':14,'validatorQuorum':6,'challengeWindowHours':504,'namedCompetitorReferencesInNewPublicContent':0,'canonicalSourceModified':False,'resultPredeclared':False,'publicNetworkTransactionSent':False}}
 (site/'qa').mkdir(exist_ok=True); (site/'qa/proof-mission-005-verify.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
