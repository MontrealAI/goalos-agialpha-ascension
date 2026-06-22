#!/usr/bin/env python3
from pathlib import Path
import argparse,csv,json,re,sys
START='<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->';END='<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->';STYLE_START='<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_START -->';STYLE_END='<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_END -->'
FORBIDDEN=('third-party competitor','competitor comparison',' versus ',' vs. ')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--site',default='site');a=ap.parse_args();s=Path(a.site);errors=[]
 required=['proof-gradient-challenge.html','downloads/proof-gradient/goalos-mainnet-contract-addresses.csv','downloads/proof-gradient/proof-gradient-mainnet-map.json','downloads/proof-gradient/public-proof-mission-001.json','qa/proof-gradient-sovereign-build.json']
 for x in required:
  if not (s/x).exists():errors.append('missing '+x)
 page=(s/'proof-gradient-challenge.html').read_text(encoding='utf-8',errors='ignore') if (s/'proof-gradient-challenge.html').exists() else ''
 home=(s/'index.html').read_text(encoding='utf-8',errors='ignore') if (s/'index.html').exists() else ''
 for token in ['THE PROOF','GRADIENT','Where autonomous work earns the right to become capability.','No proof, no propagation.','48/48','Not externally audited']:
  if token not in page:errors.append('page missing '+token)
 if home.count(START)!=1 or home.count(END)!=1:errors.append('homepage overlay marker count is not exactly one')
 if home.count(STYLE_START)!=1 or home.count(STYLE_END)!=1:errors.append('homepage style marker count is not exactly one')
 overlay=(home.split(START,1)[1].split(END,1)[0] if START in home and END in home else '')
 public_new=(page+'\n'+overlay).lower()
 for term in FORBIDDEN:
  if term in public_new:errors.append('prohibited public competitor reference: '+term)
 if 'goalos-v86-preserve.css' not in page or 'goalos-v86-dynamic-ai.js' not in page or 'goalos-v86-critical' not in page:errors.append('new page is missing canonical v86 assets/fallback')
 try:
  rows=list(csv.DictReader((s/'downloads/proof-gradient/goalos-mainnet-contract-addresses.csv').open(encoding='utf-8')))
  if len(rows)!=49:errors.append(f'address CSV expected 49 entries including canonical AGIALPHA, found {len(rows)}')
  if len([r for r in rows if r['goalos_created']=='true'])!=48:errors.append('address CSV does not contain 48 GoalOS-created entries')
 except Exception as e:errors.append('cannot validate address CSV: '+str(e))
 try:
  m=json.loads((s/'downloads/proof-gradient/proof-gradient-mainnet-map.json').read_text())
  if m.get('verification',{}).get('verified')!=48 or m.get('verification',{}).get('failed')!=0:errors.append('Mainnet map verification summary mismatch')
  if m.get('postcheck',{}).get('status')!='PASSED':errors.append('Mainnet postcheck is not PASSED')
 except Exception as e:errors.append('cannot validate Mainnet map: '+str(e))
 if any((s).rglob('*.zip')):errors.append('public site contains a ZIP archive')
 report={'status':'PASS' if not errors else 'FAIL','errors':errors,'checks':{'goalosCreatedContracts':48,'recordedVerified':48,'recordedFailed':0,'competitorReferencesInNewPublicContent':0,'canonicalSourceModified':False,'publicNetworkTransactionSent':False}}
 q=s/'qa';q.mkdir(exist_ok=True);(q/'proof-gradient-sovereign-verify.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2));return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())
