import json, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'scripts/sepolia_evidence.py'
QA=ROOT/'qa/sepolia-release-evidence'

def run(*args):
 return subprocess.run(['python',str(SCRIPT),*args],cwd=ROOT,text=True,capture_output=True)

class SepoliaEvidenceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  r=run('import','--fixture')
  assert r.returncode==0, r.stderr+r.stdout
  for k in ['authority-readback','accounting-readback','lifecycle-readback','docket','gate-contribution','release-candidate-deploy','release-candidate-verify','release-candidate-readback','release-candidate-docket']:
   rr=run(k); assert rr.returncode==0, rr.stderr+rr.stdout
 def test_exact_expected_hashes_preserved(self):
  prov=json.loads((QA/'provenance.json').read_text())
  self.assertEqual(prov['expectedHashes']['manifest'],'d8895bddefd944062bb040ca35fd962455be3e0b7411df672eac035836bf3ac6')
  self.assertEqual(prov['expectedHashes']['deploymentEvidence'],'5398773ff4cf9fb32a4092f282207ef2efd0f21d8d6b376a8c099566475dd808')
  self.assertEqual(prov['expectedHashes']['independentCheck'],'8f630fbb8db1366413bdc9a6a95c0f69ea92e06a03dc722891774e53671e1045')
  self.assertEqual(prov['expectedHashes']['verificationReport'],'baf57d5bdff69fc0d5c572f5bc34d1371989797ee51cbb684b14e9b97190a6a2')
 def test_counts_verification_alias_reconciliation(self):
  rec=json.loads((QA/'deployment-evidence.reconciled.json').read_text())
  self.assertEqual(rec['contractCount'],49); self.assertEqual(rec['transactionCount'],63)
  self.assertEqual(rec['verificationSummary']['etherscanV2'],'49/49')
  self.assertEqual(rec['receiptStatusSummary']['failed'],0)
  self.assertIn('VERIFIED_49_OF_49',rec['verificationStatus'])
  aliases={c['name']:c['fqn'] for c in rec['contracts']}
  self.assertIn('MockAGIALPHA', aliases['AGIALPHA'])
  for a in ['ProofRewardsVault','LiquidityVault','SecurityVault','CommunityVault']:
   self.assertIn('TokenReserveVault', aliases[a])
 def test_historical_unbound_privacy_and_non_overclaim(self):
  prov=json.loads((QA/'provenance.json').read_text())
  self.assertEqual(prov['classification'],'HISTORICAL_VERIFIED_SEPOLIA_DEPLOYMENT')
  self.assertEqual(prov['releaseBindingStatus'],'HISTORICAL_UNBOUND')
  gate=json.loads((QA/'gate-contribution.json').read_text())
  self.assertEqual(gate['productionGateStatuses'], {f'gate{i}':'BLOCKED' for i in range(1,6)})
  self.assertEqual(gate['requirements']['gate1']['status'],'PARTIAL')
  self.assertEqual(gate['requirements']['gate2']['status'],'NOT_SUPPORTED')
  self.assertEqual(gate['requirements']['gate5']['status'],'PARTIAL')
 def test_wrong_chain_fails_closed(self):
  import scripts.sepolia_evidence as se
  objs=se.fixture(); objs['manifest']['chainId']=1
  self.assertEqual(se.validate(objs)['status'],'FAIL')
 def test_failed_missing_empty_conflicting_evidence_fails(self):
  import scripts.sepolia_evidence as se
  objs=se.fixture(); objs['manifest']['transactions']=objs['manifest']['transactions'][:-1]
  self.assertEqual(se.validate(objs)['status'],'FAIL')
  objs=se.fixture(); objs['manifest']['contracts'][1]['address']=objs['manifest']['contracts'][0]['address']
  self.assertEqual(se.validate(objs)['status'],'FAIL')
  objs=se.fixture(); objs['verificationReport']['failed']=1
  self.assertEqual(se.validate(objs)['status'],'FAIL')
  objs=se.fixture(); objs['manifest']['contracts'][2]['fqn']='contracts/X.sol:Wrong'
  self.assertEqual(se.validate(objs)['status'],'FAIL')
 def test_current_release_workflow_and_no_mainnet_broadcast(self):
  for name in ['release-candidate-deploy','release-candidate-verify','release-candidate-readback','release-candidate-docket']:
   data=json.loads((QA/(name+'.json')).read_text())
   self.assertFalse(data['mainnetBroadcast'])
   self.assertEqual(data['status'],'MANUAL_PROTECTED_WORKFLOW_NOT_EXECUTED')
 def test_online_verify_blocks_without_credentials(self):
  r=run('verify','--fixture')
  self.assertEqual(r.returncode,0)
  self.assertEqual(json.loads(r.stdout)['status'],'BLOCKED')

if __name__=='__main__': unittest.main()
