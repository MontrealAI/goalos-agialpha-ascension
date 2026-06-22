import json,subprocess,tempfile,unittest,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProofGradientSovereignTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=Path(tempfile.mkdtemp());cls.site=cls.tmp/'site';subprocess.run(['python3','scripts/build_goalos_agialpha_ascension_website_v86.py','--out',str(cls.site)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);subprocess.run(['python3','scripts/website/build_proof_gradient_sovereign.py','--site',str(cls.site)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 @classmethod
 def tearDownClass(cls):shutil.rmtree(cls.tmp)
 def test_additive_and_idempotent(self):
  original=(ROOT/'website/v86_actual_site/index.html').read_bytes();first=(self.site/'index.html').read_bytes();subprocess.run(['python3','scripts/website/build_proof_gradient_sovereign.py','--site',str(self.site)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);second=(self.site/'index.html').read_bytes();self.assertEqual(first,second);self.assertEqual(original,(ROOT/'website/v86_actual_site/index.html').read_bytes())
 def test_public_content_has_no_competitor_reference(self):
  page=(self.site/'proof-gradient-challenge.html').read_text().lower();home=(self.site/'index.html').read_text();overlay=home.split('<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_START -->',1)[1].split('<!-- GOALOS_PROOF_GRADIENT_SOVEREIGN_END -->',1)[0].lower();
  for term in ['third-party competitor','competitor comparison',' versus ',' vs. ']:self.assertNotIn(term,page+'\n'+overlay)
 def test_mainnet_evidence_and_contract_count(self):
  m=json.loads((self.site/'downloads/proof-gradient/proof-gradient-mainnet-map.json').read_text());self.assertEqual(m['verification']['verified'],48);self.assertEqual(m['verification']['failed'],0);self.assertEqual(len([x for x in m['contracts'] if x['goalosCreated']]),48);self.assertEqual(m['postcheck']['status'],'PASSED')
 def test_verifier_passes(self):
  r=subprocess.run(['python3','scripts/website/verify_proof_gradient_sovereign.py','--site',str(self.site)],cwd=ROOT);self.assertEqual(r.returncode,0)
if __name__=='__main__':unittest.main()
