import subprocess
from pathlib import Path

def test_generate_mission_page_not_blank():
    subprocess.check_call('python scripts/mission-os/generate_mission_page.py', shell=True)
    t=Path('mission-os.html').read_text()
    assert 'GoalOS Mission OS' in t and 'GoalOS_Mission_OS_Paper.pdf' in t
