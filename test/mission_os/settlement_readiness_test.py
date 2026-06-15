import json, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class SettlementReadinessTest(unittest.TestCase):
 def test_mainnet_readiness_uses_canonical_token_and_no_movement(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'m'; r=subprocess.run(['python','scripts/mission-os/mission_os_until_done.py','--mission','examples/mission-os/ethereum-mainnet-operator-readiness.json','--out',str(out)],cwd=ROOT,text=True,capture_output=True)
   self.assertEqual(r.returncode,0,r.stderr); d=json.loads((out/'MissionSettlementReadiness.json').read_text())
   self.assertEqual(d['chain_id'],1); self.assertFalse(d['token_movement_required']); self.assertFalse(d['token_movement_performed']); self.assertEqual(d['agialpha_token_address'].lower(),'0xa61a3b3a130a9c20768eebf97e21515a6046a1fa')
