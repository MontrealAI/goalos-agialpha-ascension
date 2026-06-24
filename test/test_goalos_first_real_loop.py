import hashlib, importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'scripts/website/build_goalos_first_real_loop.py'
VERIFY=ROOT/'scripts/website/verify_goalos_first_real_loop.py'
CONTENT=ROOT/'content/goalos-first-real-loop.json'
MAINNET=ROOT/'data/mainnet/v4.4.0-mainnet-2026-06-21.json'
SCHEMA=ROOT/'schemas/goalos-first-real-loop-evidence-docket.schema.json'

spec=importlib.util.spec_from_file_location('frl_build',BUILD)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def fixture_site(root):
    site=root/'site';(site/'assets').mkdir(parents=True)
    (site/'assets/goalos-v86-preserve.css').write_text('body{}',encoding='utf-8')
    (site/'assets/goalos-v86-dynamic-ai.js').write_text('void 0;',encoding='utf-8')
    (site/'index.html').write_text('<!doctype html><html><head></head><body><main><!-- GOALOS_PROOF_MISSION_008_END --></main></body></html>',encoding='utf-8')
    (site/'proof-mission-008.html').write_text('mission 008 sentinel',encoding='utf-8')
    (site/'ethereum-mainnet.html').write_text('mainnet sentinel',encoding='utf-8')
    (site/'sitemap.xml').write_text("<?xml version='1.0'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'></urlset>",encoding='utf-8')
    (site/'site-status.json').write_text('{"release":"fixture"}\n',encoding='utf-8')
    return site

class GoalOSFirstRealLoopTests(unittest.TestCase):
    def test_content_contract(self):
        c=json.loads(CONTENT.read_text())
        self.assertEqual(c['releaseId'],'GOALOS-AGIALPHA-FIRST-REAL-LOOP-001')
        self.assertEqual(len(c['runtime']['phases']),8)
        self.assertEqual(len(c['artifactLedger']),12)
        self.assertEqual(c['runtime']['finalState'],'HUMAN_REVIEW_REQUIRED')
        self.assertEqual(c['runtime']['authority'],'NONE_GRANTED')

    def test_original_lineage_preserved(self):
        c=json.loads(CONTENT.read_text())
        self.assertEqual(c['lineage']['sourceCommit'],'bd920a6c52d820a087116bf59f2a4236d0494ac0')
        self.assertEqual(c['seed']['id'],'ColdChain-Energy-Seed-001')
        self.assertEqual(c['compiler']['id'],'ColdChain-Energy-Compiler-v0')
        self.assertEqual(c['vNext']['parent_seed_id'],c['seed']['id'])

    def test_bounded_reuse_result(self):
        c=json.loads(CONTENT.read_text())
        x=c['comparison']
        self.assertEqual((x['control_yield'],x['treatment_yield'],x['reuse_lift_percent']),(0.3,0.5,66.67))
        self.assertEqual(x['hallucination_delta'],0)
        self.assertEqual(x['safety_delta'],0)

    def test_public_docket_commitment_is_stable(self):
        c=json.loads(CONTENT.read_text());m=json.loads(MAINNET.read_text())
        mod.validate(c,m);a=mod.make_public_docket(c,m);b=mod.make_public_docket(c,m)
        self.assertEqual(a['runCommitment'],b['runCommitment'])
        self.assertRegex(a['runCommitment'],r'^[a-f0-9]{64}$')
        unsigned=dict(a);unsigned.pop('runCommitment')
        self.assertEqual(mod.digest(unsigned),a['runCommitment'])

    def test_schema_enforces_human_boundary(self):
        s=json.loads(SCHEMA.read_text())
        terminal=s['properties']['terminal']['properties']
        self.assertEqual(terminal['state']['const'],'HUMAN_REVIEW_REQUIRED')
        self.assertEqual(terminal['authority']['const'],'NONE_GRANTED')
        self.assertEqual(terminal['externalActions']['const'],0)

    def test_frontend_has_no_external_execution_primitive(self):
        js=(ROOT/'website/first_real_loop/first-real-loop.js').read_text()
        for token in ['fetch(','XMLHttpRequest','WebSocket(','window.ethereum','eth_sendTransaction','sendBeacon(']: self.assertNotIn(token,js)
        self.assertIn('crypto.subtle',js)
        self.assertIn('document.body.dataset.runState',js)

    def test_additive_clean_room_build(self):
        with tempfile.TemporaryDirectory() as d:
            site=fixture_site(Path(d));sentinel_before=sha(site/'proof-mission-008.html')
            subprocess.run([sys.executable,str(BUILD),'--site',str(site),'--content',str(CONTENT),'--mainnet',str(MAINNET),'--assets',str(ROOT/'website/first_real_loop')],cwd=ROOT,check=True,capture_output=True,text=True)
            self.assertEqual(sha(site/'proof-mission-008.html'),sentinel_before)
            self.assertTrue((site/'first-real-loop.html').is_file())
            self.assertTrue((site/'first-real-loop-architecture.html').is_file())
            self.assertTrue((site/'first-real-loop-docket.html').is_file())
            self.assertEqual((site/'index.html').read_text().count('GOALOS_FIRST_REAL_LOOP_START'),1)
            report=json.loads((site/'qa/first-real-loop-build.json').read_text())
            self.assertEqual(report['unexpectedExistingChanges'],[])
            self.assertEqual(report['removedFiles'],[])

    def test_build_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            site=fixture_site(Path(d));cmd=[sys.executable,str(BUILD),'--site',str(site),'--content',str(CONTENT),'--mainnet',str(MAINNET),'--assets',str(ROOT/'website/first_real_loop')]
            subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
            tracked=['index.html','sitemap.xml','site-status.json','first-real-loop.html','first-real-loop-architecture.html','first-real-loop-docket.html','qa/first-real-loop-build.json']
            first={p:sha(site/p) for p in tracked}
            subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
            self.assertEqual(first,{p:sha(site/p) for p in tracked})
            self.assertEqual((site/'index.html').read_text().count('GOALOS_FIRST_REAL_LOOP_START'),1)

    def test_static_verifier_passes_clean_room_site(self):
        with tempfile.TemporaryDirectory() as d:
            site=fixture_site(Path(d));subprocess.run([sys.executable,str(BUILD),'--site',str(site),'--content',str(CONTENT),'--mainnet',str(MAINNET),'--assets',str(ROOT/'website/first_real_loop')],cwd=ROOT,check=True,capture_output=True,text=True)
            p=subprocess.run([sys.executable,str(VERIFY),'--site',str(site),'--content',str(CONTENT),'--schema',str(SCHEMA)],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            report=json.loads((site/'qa/first-real-loop-static.json').read_text())
            self.assertEqual(report['status'],'PASS')
            self.assertGreaterEqual(report['checks'],180)

    def test_downloaded_docket_preserves_zero_authority(self):
        with tempfile.TemporaryDirectory() as d:
            site=fixture_site(Path(d));subprocess.run([sys.executable,str(BUILD),'--site',str(site),'--content',str(CONTENT),'--mainnet',str(MAINNET),'--assets',str(ROOT/'website/first_real_loop')],cwd=ROOT,check=True,capture_output=True,text=True)
            docket=json.loads((site/'downloads/first-real-loop/first-real-loop-evidence-docket.json').read_text())
            self.assertEqual(docket['terminal'],{'state':'HUMAN_REVIEW_REQUIRED','authority':'NONE_GRANTED','externalActions':0,'walletConnections':0,'networkRequests':0})
            self.assertEqual(docket['goalosRecord']['productionActivation'],'NOT_ACTIVATED')
            self.assertEqual(docket['goalosRecord']['userFundAuthorization'],'NO')

if __name__=='__main__': unittest.main()
