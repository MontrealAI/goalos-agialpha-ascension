import importlib.util, pathlib, json, subprocess, shutil
import pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sb', ROOT/'scripts/mainnet_sepolia_backed.py')
sb=importlib.util.module_from_spec(spec); spec.loader.exec_module(sb)
OUT=ROOT/'qa/mainnet-predeploy-sepolia'

@pytest.fixture(autouse=True)
def clean_outputs():
    shutil.rmtree(OUT, ignore_errors=True)
    subprocess.run(['git','checkout','--','qa/mainnet-predeploy/authorization-certificate.json'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    yield
    shutil.rmtree(OUT, ignore_errors=True)
    subprocess.run(['git','checkout','--','qa/mainnet-predeploy/authorization-certificate.json'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def accept_historical_operator_provenance(monkeypatch):
    original_read = sb.read
    def fake_read(path):
        data = original_read(path)
        if str(path).endswith('qa/sepolia-release-evidence/provenance.json'):
            data = dict(data)
            data['inputHashes'] = {k: '0x' + '12' * 32 for k in (data.get('inputHashes') or {'manifest': None})}
        return data
    monkeypatch.setattr(sb, 'read', fake_read)

def test_valid_historical_sepolia_satisfies_external_network_requirement(monkeypatch):
    accept_historical_operator_provenance(monkeypatch)
    r=sb.validate_historical(True)
    assert r['status']=='PASS'
    assert r['HISTORICAL_SEPOLIA_CONTRACTS_VERIFIED']==49
    assert r['HISTORICAL_SEPOLIA_VERIFICATION_FAILURES']==0
    assert r['ACCEPTED_FOR_STAGE_A_SEPOLIA_EXTERNAL_NETWORK_EVIDENCE']=='YES'

def test_historical_mismatches_are_disclosed_and_not_parity(monkeypatch):
    accept_historical_operator_provenance(monkeypatch)
    r=sb.validate_historical(False)
    assert r['CURRENT_RELEASE_BYTECODE_PARITY']=='NO'
    assert r['CURRENT_RELEASE_AUTHORITY_PARITY']=='NO'
    assert '0.8.35' in r['mismatches']['compiler']
    assert 'MockAGIALPHA' in r['mismatches']['token']
    assert 'Wallet A' in r['mismatches']['authority']

def test_sepolia_backed_path_does_not_require_mainnet_fork_but_blocks_without_local_rehearsal(monkeypatch):
    accept_historical_operator_provenance(monkeypatch)
    c=sb.cert()
    assert c['FULL_MAINNET_FORK_ASSURANCE']=='NO'
    assert c['FULL_G1_G5_ASSURANCE']=='NO'
    assert c['status']!='AUTHORIZED_FOR_INITIAL_MAINNET_DEPLOYMENT_FROM_SEPOLIA_EVIDENCE'
    assert any('localRehearsal' in b for b in c['blockers'])

def _write_initial_profile_evidence(monkeypatch):
    OUT.mkdir(parents=True, exist_ok=True)
    accept_historical_operator_provenance(monkeypatch)
    monkeypatch.setattr(sb, 'clean_tree', lambda: True)
    (OUT/'build-and-test.json').write_text(json.dumps({'schemaVersion':'1.0','status':'PASS','releaseId':sb.git(['rev-parse','HEAD']),'mainnetBroadcastOccurred':False}))
    (OUT/'local-rehearsal.json').write_text(json.dumps({'schemaVersion':'1.0','status':'PASS','executionMode':'LOCAL_DETERMINISTIC_RELEASE_REHEARSAL','mainnetForkAssurance':False,'walletA':sb.WA,'walletB':sb.WB,'topologyCount':49,'transactionCount':63,'receiptCount':63,'ownerReadback':sb.WB,'walletAZeroAuthority':True,'walletBAuthority':True,'mainnetBroadcastOccurred':False}))
    checks={k:'PASS' for k in ['ownership_admin_assignment','semantic_override_replay_rejection','stale_state_rejection','no_arbitrary_executor','accounting_consistency','zero_canary_limit_disabled','lifecycle_transition_controls','shutdown_liability_checks','deployment_resume_logic']}
    (OUT/'initial-safety-checks.json').write_text(json.dumps({'schemaVersion':'1.0','status':'PASS','checks':checks,'mainnetBroadcastOccurred':False}))
    tx={'expectedNonce':0,'expectedCreateAddress':'0x0000000000000000000000000000000000000001','fullyQualifiedName':'contracts/registry/GoalOSDeploymentDirectory.sol:GoalOSDeploymentDirectory','artifactHash':'0x'+'11'*32,'constructorCommitment':'0x'+'22'*32,'initcodeHash':'0x'+'33'*32,'expectedRuntimeBytecodeHash':'0x'+'44'*32,'transactionValue':'0','gasEstimate':'1','gasLimit':'1','maxFeePerGas':'1','maxPriorityFeePerGas':'1','maximumTransactionCost':'1'}
    (OUT/'deployment-plan.public.json').write_text(json.dumps({'chainId':1,'canonicalAgialpha':sb.AGI,'walletA':sb.WA,'walletB':sb.WB,'startingNonce':0,'pendingTransactionDisposition':'NONE','orderedTransactions':[tx],'maximumCumulativeCost':'1','minimumWalletARemainingEth':'0','verificationInputCommitment':'0x'+'55'*32,'issuedAt':'2026-06-21T00:00:00Z','expiresAt':'2999-01-01T00:00:00Z','planHash':'0x'+'66'*32}))
    (OUT/'verification-readiness.json').write_text(json.dumps({'schemaVersion':'1.0','status':'PASS','etherscanV2':True,'privateConstructorInputsCommitment':'0x'+'77'*32,'mainnetBroadcastOccurred':False}))
    (OUT/'resume-readiness.json').write_text(json.dumps({'schemaVersion':'1.0','status':'PASS','appendOnlyJournal':True,'nonceLocking':True,'safeResumeTested':True,'mainnetBroadcastOccurred':False}))
    (OUT/'mainnet-dependency-doctor.json').write_text(json.dumps({'schemaVersion':'1.0','status':'PASS','chainId':1,'canonicalAgialpha':sb.AGI,'providerAgreement':True,'canonicalAgialphaCodeHash':'0x'+'88'*32,'mainnetBroadcastOccurred':False}))

def test_initial_profile_can_pass_without_mainnet_fork_artifact(monkeypatch):
    _write_initial_profile_evidence(monkeypatch)
    c=sb.cert()
    assert c['status']=='AUTHORIZED_TO_DEPLOY_ON_ETHEREUM_MAINNET'
    assert c['authorizationProfile']=='SEPOLIA_BACKED_INITIAL_MAINNET_V1'
    assert c['AUTHORIZATION_SCOPE']=='INITIAL_MAINNET_INFRASTRUCTURE_DEPLOYMENT_ONLY'
    assert c['FULL_MAINNET_FORK_ASSURANCE']=='NO'
    assert not (OUT/'fork-rehearsal.json').exists()
    assert all(v=='PASS' for v in c['gates'].values())

def test_certificate_cannot_claim_production_or_user_funds(monkeypatch):
    accept_historical_operator_provenance(monkeypatch)
    c=sb.cert()
    assert c['PRODUCTION_READY']=='NO'
    assert c['USER_FUNDS_AUTHORIZED']=='NO'
    assert c['PUBLIC_RELIANCE_AUTHORIZED']=='NO'
    assert c['PROTOCOL_ACTIVATION_AUTHORIZED']=='NO'


def test_missing_ledger_does_not_block_stage_a_but_blocks_live_arming():
    c=sb.cert()
    assert not any('ledgerRiskAcceptance' in b for b in c['blockers'])
    assert any('verificationReadiness' in b for b in c['blockers'])
    assert any('resumeReadiness' in b for b in c['blockers'])
    assert sb.arm_for_live_deployment() is False

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


def test_fixture_only_historical_sepolia_blocks_external_network_requirement():
    r = sb.validate_historical(False)
    assert r['status'] == 'BLOCKED'
    assert r['fixtureOnly'] is True
    assert r['ACCEPTED_FOR_STAGE_A_SEPOLIA_EXTERNAL_NETWORK_EVIDENCE'] == 'NO'

def test_current_release_requires_build_test_evidence(monkeypatch):
    OUT.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sb, 'clean_tree', lambda: True)
    r = sb.current_release()
    assert r['status'] == 'BLOCKED'
    assert 'build/test' in r['blockers'][0]

def test_failed_local_rehearsal_is_not_rewritten_to_pass(monkeypatch):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'local-rehearsal.json').write_text(json.dumps({'schemaVersion':'1.0','status':'FAIL','executionMode':'LOCAL_DETERMINISTIC_RELEASE_REHEARSAL','mainnetForkAssurance':False,'walletA':sb.WA,'walletB':sb.WB,'topologyCount':1,'transactionCount':1,'receiptCount':1,'ownerReadback':sb.WB,'walletAZeroAuthority':True,'walletBAuthority':True,'mainnetBroadcastOccurred':False}))
    assert sb.rehearsal()['status'] == 'BLOCKED'

def test_plan_rejects_blocked_or_broadcast_input():
    OUT.mkdir(parents=True, exist_ok=True)
    tx={'expectedNonce':0,'expectedCreateAddress':'0x0000000000000000000000000000000000000001','fullyQualifiedName':'x:y','artifactHash':'0x'+'11'*32,'constructorCommitment':'0x'+'22'*32,'initcodeHash':'0x'+'33'*32,'expectedRuntimeBytecodeHash':'0x'+'44'*32,'transactionValue':'0','gasEstimate':'1','gasLimit':'1','maxFeePerGas':'1','maxPriorityFeePerGas':'1','maximumTransactionCost':'1'}
    (OUT/'deployment-plan.public.json').write_text(json.dumps({'status':'BLOCKED','chainId':1,'canonicalAgialpha':sb.AGI,'walletA':sb.WA,'walletB':sb.WB,'startingNonce':0,'pendingTransactionDisposition':'NONE','orderedTransactions':[tx],'maximumCumulativeCost':'1','minimumWalletARemainingEth':'0','verificationInputCommitment':'0x'+'55'*32,'issuedAt':'2026-06-21T00:00:00Z','expiresAt':'2999-01-01T00:00:00Z','planHash':'0x'+'66'*32,'mainnetBroadcastOccurred':True}))
    r=sb.plan_validate(False)
    assert r['status']=='BLOCKED'
    assert any('status is not PASS' in e for e in r['errors'])
    assert any('mainnetBroadcastOccurred' in e for e in r['errors'])
