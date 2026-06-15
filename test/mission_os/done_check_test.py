import subprocess

def test_done_checker_passes(tmp_path):
    out=tmp_path/'run'; subprocess.check_call(f'python scripts/mission-os/mission_os_until_done.py --mission examples/mission-os/ai-product-intelligence.json --out {out}', shell=True)
    subprocess.check_call(f'python scripts/mission-os/done_check.py --dir {out}', shell=True)
