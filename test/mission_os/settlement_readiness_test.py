import json, subprocess

def test_mainnet_readiness_never_broadcasts(tmp_path):
    out=tmp_path/'mainnet'; subprocess.check_call(f'python scripts/mission-os/mission_os_until_done.py --mission examples/mission-os/ethereum-mainnet-operator-readiness.json --out {out}', shell=True)
    r=json.loads((out/'MissionSettlementReadiness.json').read_text())
    assert r['chain_id']==1 and r['mainnet_broadcast_performed'] is False and r['token_movement_performed'] is False
    assert r['mainnet_deployed_status']=='NO'
