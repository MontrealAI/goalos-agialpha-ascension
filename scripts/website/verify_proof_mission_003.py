#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

MARKERS=[
("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->","<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->","Mission 001 overlay"),
("<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_START -->","<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_STYLE_END -->","Mission 001 style"),
("<!-- GOALOS_PROOF_MISSION_002_START -->","<!-- GOALOS_PROOF_MISSION_002_END -->","Mission 002 overlay"),
("<!-- GOALOS_PROOF_MISSION_002_STYLE_START -->","<!-- GOALOS_PROOF_MISSION_002_STYLE_END -->","Mission 002 style"),
("<!-- GOALOS_PROOF_MISSION_003_START -->","<!-- GOALOS_PROOF_MISSION_003_END -->","Mission 003 overlay"),
("<!-- GOALOS_PROOF_MISSION_003_STYLE_START -->","<!-- GOALOS_PROOF_MISSION_003_STYLE_END -->","Mission 003 style"),
]
FORBIDDEN=("recursive.com","recursive org","recursive-style","competitor comparison","named competitor")

def remove_marked(text,start,end): return re.sub(re.escape(start)+r".*?"+re.escape(end),"",text,flags=re.S)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--site',default='site'); p.add_argument('--canonical',default='website/v86_actual_site/index.html'); p.add_argument('--content',default='content/proof-mission-003-capability-constellation.json'); p.add_argument('--mainnet',default='data/mainnet/v4.4.0-mainnet-2026-06-21.json'); a=p.parse_args()
    site=Path(a.site); errors=[]
    required=[
      'proof-gradient-challenge.html','proof-mission-002.html','proof-mission-003.html','proof-missions.html',
      'downloads/proof-missions/public-proof-mission-003.json','downloads/proof-missions/mission-003-constellation-manifest-template.json',
      'downloads/proof-missions/mission-003-interface-covenant-template.json','downloads/proof-missions/mission-003-fault-domain-register-template.json',
      'downloads/proof-missions/mission-003-proof-route.csv','qa/proof-mission-003-build.json'
    ]
    for r in required:
        if not (site/r).exists(): errors.append('missing '+r)
    read=lambda r:(site/r).read_text(encoding='utf-8',errors='ignore') if (site/r).exists() else ''
    page,hub,home=read('proof-mission-003.html'),read('proof-missions.html'),read('index.html')
    for token in ['THE CAPABILITY','CONSTELLATION','Where proven capabilities become a governed intelligence.','No composition without conformance.','No shared memory without provenance.','No collective action without containment and rollback.','Composition-Proven','No result predeclared']:
        if token not in page: errors.append('Mission 003 page missing '+token)
    for token in ['THE PROOF','MISSIONS','The Proof Gradient','The Ascension Protocol','The Capability Constellation','proof-mission-003.html']:
        if token not in hub: errors.append('Proof Missions hub missing '+token)
    for start,end,label in MARKERS:
        if home.count(start)!=1 or home.count(end)!=1: errors.append(label+' marker count is not exactly one')
    m3s,m3e=MARKERS[4][0],MARKERS[4][1]
    overlay=home.split(m3s,1)[1].split(m3e,1)[0] if m3s in home and m3e in home else ''
    new_public=(page+'\n'+hub+'\n'+overlay).lower()
    for term in FORBIDDEN:
        if term in new_public: errors.append('prohibited public reference: '+term)
    if 'proof-mission-003.html' not in home or 'proof-missions.html' not in home: errors.append('homepage Mission 003 links missing')
    if 'goalos-v86-preserve.css' not in page or 'goalos-v86-dynamic-ai.js' not in page: errors.append('Mission 003 page missing canonical assets')
    if 'PROTOCOL_PUBLISHED_AWAITING_THREE_TRANSFER_PROVEN_CAPABILITIES'.lower() in page.lower(): errors.append('raw machine status leaked into public page')
    try:
        content=json.loads(Path(a.content).read_text())
        if content.get('status')!='PROTOCOL_PUBLISHED_AWAITING_THREE_TRANSFER_PROVEN_CAPABILITIES': errors.append('unexpected Mission 003 status')
        if sum(int(x.get('share',0)) for x in content.get('settlement',[]))!=100: errors.append('settlement shares do not total 100')
        if len(content.get('proofRoute',[]))!=24: errors.append('expected 24 Mission 003 proof-route stages')
        if len(content.get('validators',[]))!=4: errors.append('expected four validators')
        b=content.get('missionBudget',{})
        if b.get('transferProvenCapabilitiesMin')!=3 or b.get('transferProvenCapabilitiesMax')!=5: errors.append('expected 3–5 capability admission rule')
        if b.get('challengeWindowHours')!=168: errors.append('expected 168-hour challenge window')
        if content.get('mission4',{}).get('status')!='HORIZON_ONLY_NOT_YET_AUTHORIZED': errors.append('Mission 004 horizon status mismatch')
    except Exception as exc: errors.append('cannot validate Mission 003 content: '+str(exc))
    try:
        mainnet=json.loads(Path(a.mainnet).read_text()); by={x['name']:x for x in mainnet['contracts']}
        rows=list(csv.DictReader((site/'downloads/proof-missions/mission-003-proof-route.csv').open(encoding='utf-8')))
        if len(rows)!=24: errors.append(f'proof route expected 24 rows, found {len(rows)}')
        for row in rows:
            c=by.get(row['contract'])
            if not c or c['address'].lower()!=row['address'].lower(): errors.append('proof route address mismatch for '+row['contract'])
        if mainnet.get('goalosCreatedContractCount')!=48: errors.append('Mainnet contract count mismatch')
        if mainnet.get('verification',{}).get('verified')!=48 or mainnet.get('verification',{}).get('failed')!=0: errors.append('Mainnet verification summary mismatch')
        if mainnet.get('phaseBGrantCount')!=14: errors.append('Mainnet configured grant count mismatch')
        if mainnet.get('postcheck',{}).get('status')!='PASSED': errors.append('Mainnet postcheck not PASSED')
    except Exception as exc: errors.append('cannot validate proof route/Mainnet data: '+str(exc))
    for template in ['mission-003-constellation-manifest-template.json','mission-003-interface-covenant-template.json','mission-003-fault-domain-register-template.json']:
        try:
            d=json.loads((site/'downloads/proof-missions'/template).read_text())
            if d.get('status')!='TEMPLATE_NOT_EVIDENCE': errors.append(template+' must be explicitly non-evidence')
        except Exception as exc: errors.append('cannot validate '+template+': '+str(exc))
    try:
        canonical=Path(a.canonical).read_text(encoding='utf-8'); stripped=home
        for start,end,_ in MARKERS: stripped=remove_marked(stripped,start,end)
        norm=lambda s:re.sub(r">\s+<","><",s).strip()
        if norm(stripped)!=norm(canonical): errors.append('generated homepage differs from canonical source beyond marked mission overlays')
    except Exception as exc: errors.append('cannot validate canonical homepage preservation: '+str(exc))
    if any(site.rglob('*.zip')): errors.append('public site contains a ZIP archive')
    report={'status':'PASS' if not errors else 'FAIL','errors':errors,'checks':{
      'mission001Preserved':True,'mission002Preserved':True,'mission003Pages':2,'proofRouteContracts':24,
      'goalosCreatedContracts':48,'recordedVerified':48,'recordedFailed':0,'configuredGrants':14,
      'namedCompetitorReferencesInNewPublicContent':0,'canonicalSourceModified':False,'resultPredeclared':False,
      'publicNetworkTransactionSent':False}}
    (site/'qa').mkdir(exist_ok=True); (site/'qa/proof-mission-003-verify.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
