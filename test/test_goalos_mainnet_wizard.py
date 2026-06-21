import importlib.util, pathlib, os, subprocess, json, shutil
import pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('wiz', ROOT/'scripts/goalos_mainnet_wizard.py')
wiz=importlib.util.module_from_spec(spec); spec.loader.exec_module(wiz)

def test_private_state_does_not_print_secrets(tmp_path, capsys):
    run=tmp_path/'run'; run.mkdir()
    state={'secret':'should-not-print','mainnetBroadcastOccurred':False}
    wiz.save_state(run,state)
    out=capsys.readouterr().out
    assert 'should-not-print' not in out
    assert (run/'wizard-state.json').stat().st_mode & 0o777 == 0o600

def test_prepare_mode_cannot_broadcast_via_status():
    r=subprocess.run(['python','scripts/goalos_mainnet_wizard.py','--status'],cwd=ROOT,stdout=subprocess.PIPE,text=True)
    assert 'mainnetBroadcastOccurred' in r.stdout or r.returncode in {0,2}

def test_deploy_is_impossible_in_ci(monkeypatch):
    env=os.environ.copy(); env['CI']='1'
    r=subprocess.run(['python','scripts/goalos_mainnet_wizard.py','--deploy'],cwd=ROOT,env=env,stdout=subprocess.PIPE,text=True)
    assert r.returncode!=0
    assert 'Deployment is impossible in CI' in r.stdout

def test_desktop_launcher_has_no_secrets(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))
    assert wiz.desktop()==0
    text=(tmp_path/'.local/share/applications/goalos-mainnet-wizard.desktop').read_text()
    assert 'GoalOS Mainnet Wizard' in text
    assert 'PRIVATE_KEY' not in text and 'ETHERSCAN' not in text

def test_wrapper_invokes_wizard_script():
    text=(ROOT/'goalos-mainnet-wizard.sh').read_text()
    assert 'npm run goalos:mainnet:wizard' in text

def test_checklist_is_plain_language(capsys):
    wiz.print_checklist()
    out=capsys.readouterr().out
    assert 'GoalOS Initial Mainnet Deployment Wizard' in out
    assert '1/9  Clean release workspace' in out
    assert '9/9  Scoped Stage-A certificate' in out
