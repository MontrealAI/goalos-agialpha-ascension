from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content/proof-mission-006-long-horizon.json'
MAINNET=ROOT/'data/mainnet/v4.4.0-mainnet-2026-06-21.json'
BUILDERS=[
'build_proof_gradient_sovereign.py','build_proof_mission_002.py','build_proof_mission_003.py',
'build_proof_mission_004.py','build_proof_mission_005.py','build_proof_mission_006.py']

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd):
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0,r.stdout+'\n'+r.stderr

def build_site():
    td=tempfile.TemporaryDirectory(prefix='goalos-m6-test-')
    site=Path(td.name)/'site'
    run([sys.executable,'scripts/generate_goalos_agialpha_ascension_v86_final.py','--source','website/v86_actual_site','--output',str(site)])
    for b in BUILDERS: run([sys.executable,'scripts/website/'+b,'--site',str(site)])
    return td,site

def test_identity_and_status():
    c=load(CONTENT)
    assert c['missionId']=='GOALOS-PUBLIC-PROOF-MISSION-006'
    assert c['sequence']==6
    assert c['status']=='PROTOCOL_PUBLISHED_AWAITING_ONE_FEDERATION_PROVEN_COMMONWEALTH'
    assert c['mission7']['status']=='HORIZON_ONLY_NOT_YET_AUTHORIZED'

def test_constitution_budget_and_settlement():
    c=load(CONTENT); b=c['missionBudget']
    assert len(c['constitution'])==3 and len(c['continuityTrial']['eras'])==7
    assert b['modelAndToolchainGenerations']==8 and b['cryptographicEpochs']==3
    assert b['challengeWindowHours']==720 and b['archiveLossPercent']==50
    assert sum(x['share'] for x in c['settlement'])==100

def test_proof_route_matches_mainnet():
    c=load(CONTENT); m=load(MAINNET); names={x['name'] for x in m['contracts']}
    route=[x['contractName'] for x in c['proofRoute']]
    assert len(route)==44 and len(set(route))==44 and set(route)<=names
    assert m['goalosCreatedContractCount']==48
    assert m['verification']=={'verified':48,'failed':0,'complete':True}
    assert m['phaseBGrantCount']==14 and m['postcheck']['status']=='PASSED'

def test_no_competitor_or_predeclared_result():
    text=CONTENT.read_text().lower()
    for token in ('recursive.com','recursive org','recursive-style','named competitor'):
        assert token not in text
    c=load(CONTENT)
    assert all('achieved' not in x.lower() for x in c['claimBoundaries'])
    assert 'AWAITING' in c['status']

def test_build_generates_complete_public_experience():
    td,site=build_site()
    try:
        page=(site/'proof-mission-006.html').read_text()
        hub=(site/'proof-missions.html').read_text()
        assert 'THE LONG <span>HORIZON</span>' in page
        assert page.count('class="route-item"')==44
        assert 'The Long Horizon' in hub
        assert (site/'downloads/proof-missions/public-proof-mission-006.json').exists()
        assert (site/'downloads/proof-missions/mission-006-proof-route.csv').exists()
    finally: td.cleanup()

def test_build_is_additive_for_missions_001_to_004():
    td,site=build_site()
    try:
        # Builder itself records and enforces these hashes.
        report=load(site/'qa/proof-mission-006-build.json')
        assert report['mission001To004Preserved'] is True
        assert report['mission005HorizonPromoted'] is True
        assert report['publicNetworkTransactionSent'] is False
    finally: td.cleanup()

def test_homepage_has_one_marked_panel():
    td,site=build_site()
    try:
        home=(site/'index.html').read_text()
        assert home.count('<!-- GOALOS_PROOF_MISSION_006_START -->')==1
        assert home.count('<!-- GOALOS_PROOF_MISSION_006_END -->')==1
        assert home.count('PUBLIC PROOF MISSION 006')==1
    finally: td.cleanup()

def test_templates_are_not_evidence():
    td,site=build_site()
    try:
        dl=site/'downloads/proof-missions'
        for p in dl.glob('mission-006-*-template.json'):
            assert load(p)['status']=='TEMPLATE_NOT_EVIDENCE'
    finally: td.cleanup()

def test_full_verifier_passes_without_network_or_broadcast():
    td,site=build_site()
    try:
        run([sys.executable,'scripts/website/verify_proof_mission_006.py','--site',str(site),'--repo','.'])
        r=load(site/'qa/proof-mission-006-verification.json')
        assert r['status']=='PASS'
        assert r['publicNetworkTransactionSent'] is False
    finally: td.cleanup()
