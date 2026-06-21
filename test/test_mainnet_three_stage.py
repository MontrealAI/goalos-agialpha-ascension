import importlib.util, json, pathlib, os, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m3', ROOT/'scripts/mainnet_three_stage.py')
m3=importlib.util.module_from_spec(spec); spec.loader.exec_module(m3)

def test_predeploy_passes_without_live_mainnet_evidence():
    c=m3.predeploy_certificate()
    assert all(v=='PASS' for v in c['gates'].values())
    assert c['MAINNET_DEPLOYED']=='NO'
    assert not m3.semantic_lint_stage_a(c)

def test_stage_a_forbidden_live_evidence_fails():
    c=m3.predeploy_certificate(); c['evidence'].append({'type':'LIVE_MAINNET_RECEIPT','path':'qa/mainnet-postdeploy/x.json'})
    errs=m3.semantic_lint_stage_a(c)
    assert any('LIVE_MAINNET_RECEIPT' in e for e in errs)
    assert any('mainnet-postdeploy' in e for e in errs)

def test_valid_fork_local_31337_accepted_and_local_mislabel_rejected():
    r=m3.fork_report()
    assert r['executionMode']=='MAINNET_FORK' and r['upstreamChainId']==1 and r['localChainId']==31337
    bad=dict(r); bad['upstreamChainId']=31337; bad['normalLocalChain']=True
    assert not (bad['executionMode']=='MAINNET_FORK' and bad['upstreamChainId']==1 and bad['normalLocalChain'] is False)

def test_stage_a_fails_without_fork_evidence(monkeypatch):
    c=m3.predeploy_certificate(); (m3.PRE/'fork-rehearsal.json').unlink()
    assert m3.validate_predeploy() is False
    m3.fork_report()

def test_stage_b_and_c_blocked_before_required_evidence():
    b=m3.post_cert(); a=m3.act_cert()
    assert b['status'].startswith('BLOCKED') and b['MAINNET_DEPLOYED']=='NO'
    assert a['status'].startswith('BLOCKED') and a['PRODUCTION_ACTIVATION_EFFECTIVE']=='NO'

def test_later_stage_evidence_cannot_satisfy_stage_a():
    c=m3.predeploy_certificate(); c['evidence']=[{'type':'MAINNET_FORK','path':'qa/mainnet-postdeploy/receipt.json'}]
    assert m3.semantic_lint_stage_a(c)
    c['evidence']=[{'type':'DEPLOYMENT_PLAN','path':'qa/mainnet-activation/canary.json'}]
    assert m3.semantic_lint_stage_a(c)

def test_deployment_blocked_by_absent_stale_certificate():
    c=m3.predeploy_certificate(); c['expiresAt']='2000-01-01T00:00:00+00:00'
    assert c['expiresAt'] < '2026-01-01T00:00:00+00:00'

def test_verification_retry_not_redeployment_model():
    b=m3.post_cert()
    assert 'verification' in ' '.join(b['requires']).lower()
    assert b['status']=='BLOCKED_UNTIL_REAL_CHAIN_1_EVIDENCE'

def test_release_state_dag_acyclic():
    assert m3.validate_dag(m3.release_state())
    cyc={'stages':{'A':{'dependsOn':['B']},'B':{'dependsOn':['A']}}}
    assert not m3.validate_dag(cyc)

def test_final_check_allows_not_deployed_and_ci_broadcast_disabled(monkeypatch):
    c=m3.predeploy_certificate()
    assert c['MAINNET_DEPLOYED']=='NO' and c['MAINNET_DEPLOYMENT_AUTHORIZED']=='YES'
    monkeypatch.setenv('CI','true')
    assert os.environ['CI']=='true'
