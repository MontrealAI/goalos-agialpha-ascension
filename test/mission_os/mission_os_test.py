import json, subprocess
from pathlib import Path

def run(cmd): return subprocess.run(cmd, shell=True, text=True, capture_output=True)

def test_mission_os_run_done(tmp_path):
    out=tmp_path/'run'
    r=run(f'python scripts/mission-os/mission_os_until_done.py --mission examples/mission-os/ai-product-intelligence.json --out {out} --max-cycles 2')
    assert r.returncode==0, r.stderr+r.stdout
    state=json.loads((out/'run-state.json').read_text())
    assert state['done'] is True
    assert (out/'MissionSettlementReadiness.json').exists()
