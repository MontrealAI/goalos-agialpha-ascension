import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class WorkflowSafetyTest(unittest.TestCase):
 def test_mission_workflows_do_not_use_mainnet_deploy_or_automerge(self):
  for wf in ['goalos-mission-os-until-done.yml','goalos-mission-os-qa.yml','goalos-autonomous-website-autopilot.yml','goalos-mission-os-paper-pages.yml']:
   text=(ROOT/'.github/workflows'/wf).read_text().lower()
   self.assertNotIn('deploy:ethereum-mainnet', text)
   self.assertNotIn('auto-merge: true', text)
   self.assertNotIn('private_mainnet_rpc_url', text)
   self.assertNotIn('deployer_private_key', text)
