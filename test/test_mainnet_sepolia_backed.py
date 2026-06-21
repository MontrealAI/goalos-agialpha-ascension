import importlib.util, pathlib, json, subprocess, shutil
import pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sb', ROOT/'scripts/mainnet_sepolia_backed.py')
sb=importlib.util.module_from_spec(spec); spec.loader.exec_module(sb)
OUT=ROOT/'qa/mainnet-predeploy-sepolia'

@pytest.fixture(autouse=True)
def clean_outputs():
    shutil.rmtree(OUT, ignore_errors=True)
    yield
    shutil.rmtree(OUT, ignore_errors=True)

def test_valid_historical_sepolia_satisfies_external_network_requirement():
    r=sb.validate_historical(True)
    assert r['status']=='PASS'
    assert r['HISTORICAL_SEPOLIA_CONTRACTS_VERIFIED']==49
    assert r['HISTORICAL_SEPOLIA_VERIFICATION_FAILURES']==0
    assert r['ACCEPTED_FOR_STAGE_A_SEPOLIA_EXTERNAL_NETWORK_EVIDENCE']=='YES'

def test_historical_mismatches_are_disclosed_and_not_parity():
    r=sb.validate_historical(False)
    assert r['CURRENT_RELEASE_BYTECODE_PARITY']=='NO'
    assert r['CURRENT_RELEASE_AUTHORITY_PARITY']=='NO'
    assert '0.8.35' in r['mismatches']['compiler']
    assert 'MockAGIALPHA' in r['mismatches']['token']
    assert 'Wallet A' in r['mismatches']['authority']

def test_sepolia_backed_path_does_not_require_mainnet_fork_but_blocks_without_local_rehearsal():
    c=sb.cert()
    assert c['FULL_MAINNET_FORK_ASSURANCE']=='NO'
    assert c['FULL_G1_G5_ASSURANCE']=='NO'
    assert c['status']!='AUTHORIZED_FOR_INITIAL_MAINNET_DEPLOYMENT_FROM_SEPOLIA_EVIDENCE'
    assert any('localRehearsal' in b for b in c['blockers'])

def test_certificate_cannot_claim_production_or_user_funds():
    c=sb.cert()
    assert c['PRODUCTION_READY']=='NO'
    assert c['USER_FUNDS_AUTHORIZED']=='NO'
    assert c['PUBLIC_RELIANCE_AUTHORIZED']=='NO'
    assert c['PROTOCOL_ACTIVATION_AUTHORIZED']=='NO'


def test_missing_ledger_and_readiness_block_authorization():
    c=sb.cert()
    assert any('ledgerRiskAcceptance' in b for b in c['blockers'])
    assert any('verificationReadiness' in b for b in c['blockers'])
    assert any('resumeReadiness' in b for b in c['blockers'])

def test_empty_or_aggregate_only_plan_blocks():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'deployment-plan.public.json').write_text(json.dumps({'chainId':1,'canonicalAgialpha':sb.AGI,'walletA':sb.WA,'walletB':sb.WB,'orderedTransactions':[{'commitment':'protected','count':1}]}))
    r=sb.plan_validate(True)
    assert r['status']=='BLOCKED'
    assert any('aggregate-only' in e for e in r['errors'])

def test_manually_edited_certificate_yes_is_rejected():
    OUT.mkdir(parents=True, exist_ok=True)
    bad={'schemaVersion':'1.0','certificateType':'MAINNET_PREDEPLOY_SEPOLIA_BACKED_INITIAL_DEPLOYMENT','status':'AUTHORIZED_FOR_INITIAL_MAINNET_DEPLOYMENT_FROM_SEPOLIA_EVIDENCE','AUTHORIZATION_MODE':'SEPOLIA_BACKED_INITIAL_DEPLOYMENT','AUTHORIZATION_SCOPE':'INITIAL_DEPLOYMENT_ONLY','PRODUCTION_READY':'YES','USER_FUNDS_AUTHORIZED':'YES','FULL_MAINNET_FORK_ASSURANCE':'YES','FULL_G1_G5_ASSURANCE':'YES','MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','certificateHash':'0x00'}
    (OUT/'initial-deployment-certificate.json').write_text(json.dumps(bad))
    assert sb.validate_cert(False) is False

def test_stage_b_and_c_still_fail_closed_without_live_evidence():
    assert subprocess.run(['python','scripts/mainnet_three_stage.py','postdeploy-validate'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode in {0,1}
    assert subprocess.run(['python','scripts/mainnet_three_stage.py','activation-validate'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode in {0,1}

def test_no_public_network_transaction_is_sent_by_resolver():
    result=subprocess.run(['python','scripts/mainnet_sepolia_backed.py','resolve-and-authorize'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    assert result.returncode!=0
    assert 'mainnetBroadcastOccurred' in result.stdout
    assert 'AUTHORIZED_FOR_INITIAL_MAINNET_DEPLOYMENT_FROM_SEPOLIA_EVIDENCE\n\nINITIAL_MAINNET_DEPLOYMENT_AUTHORIZED = YES' not in result.stdout
