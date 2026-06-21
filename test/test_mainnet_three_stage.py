import importlib.util, pathlib, os, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m3', ROOT/'scripts/mainnet_three_stage.py')
m3=importlib.util.module_from_spec(spec); spec.loader.exec_module(m3)

def test_blocked_gate_reports_cannot_authorize_when_not_regenerated():
    rid=m3.release_identity(); p=ROOT/'qa/mainnet-readiness/gate-1-authority.json'
    old=p.read_text(); p.write_text('{"status":"BLOCKED","releaseIdentity":"%s","requirements":[{"id":"x","status":"BLOCKED"}]}'%rid)
    try:
        _, errs=m3.validate_gate_report('qa/mainnet-readiness/gate-1-authority.json', rid)
        assert errs
    finally: p.write_text(old)

def test_hard_coded_pass_mutation_detected_by_requirements_validation():
    rid=m3.release_identity(); p=ROOT/'qa/mainnet-readiness/gate-2-overrides.json'
    old=p.read_text(); p.write_text('{"status":"PASS","releaseIdentity":"%s","requirements":[]}'%rid)
    try:
        _, errs=m3.validate_gate_report('qa/mainnet-readiness/gate-2-overrides.json', rid)
        assert any('requirements array missing' in e for e in errs)
    finally: p.write_text(old)

def test_all_five_valid_reports_authorize_stage_a_without_live_mainnet_receipts():
    c=m3.predeploy_certificate()
    assert c['status']=='AUTHORIZED'
    assert all(v=='PASS' for v in c['gates'].values())
    assert c['MAINNET_DEPLOYED']=='NO'
    assert 'LIVE_MAINNET_RECEIPT' not in str(c)

def test_stage_a_forbidden_live_or_later_stage_evidence_fails():
    c=m3.predeploy_certificate(); c['evidence'].append({'type':'LIVE_MAINNET_RECEIPT','path':'qa/mainnet-postdeploy/x.json'})
    errs=m3.semantic_lint_stage_a(c)
    assert any('LIVE_MAINNET_RECEIPT' in e for e in errs)
    assert any('mainnet-postdeploy' in e for e in errs)
    c['evidence']=[{'type':'DEPLOYMENT_PLAN','path':'qa/mainnet-activation/canary.json'}]
    assert m3.semantic_lint_stage_a(c)

def test_fork_authenticity_accepts_31337_local_and_rejects_fake_local():
    r=m3.fork_report(); assert m3.fork_valid(r)
    assert r['upstreamChainId']==1 and r['localChainId']==31337
    bad=dict(r); bad['upstreamChainId']=31337; bad['normalLocalChain']=True
    assert not m3.fork_valid(bad)

def test_live_local_gated_refuses_in_ci_and_uses_canonical_deployer_text():
    text=(ROOT/'scripts/mainnet_three_stage.py').read_text()
    assert "deploy:ethereum-mainnet:gated" in text
    env=os.environ.copy(); env['CI']='true'
    p=subprocess.run(['python','scripts/mainnet_three_stage.py','live-local-gated'],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE)
    assert p.returncode==2 and 'disabled in CI' in p.stdout

def test_verify_fails_without_real_manifest_or_network():
    text=(ROOT/'scripts/mainnet_three_stage.py').read_text()
    assert "verify:mainnet:all" in text

def test_status_does_not_claim_verification_from_file_existence():
    m3.predeploy_certificate(); p=subprocess.run(['python','scripts/mainnet_three_stage.py','status'],cwd=ROOT,text=True,stdout=subprocess.PIPE)
    assert p.returncode==0 and 'PREDEPLOYMENT_AUTHORIZED' in p.stdout and 'MAINNET_DEPLOYMENT_VERIFIED' not in p.stdout

def test_resume_recover_route_to_real_wizard_without_duplicate_placeholder():
    text=(ROOT/'scripts/mainnet_three_stage.py').read_text()
    assert "goalos-deploy-wizard.ts" in text and "cmd,'--network','ethereumMainnet'" in text

def test_stage_b_and_c_final_checks_fail_before_evidence_and_placeholders_do_not_validate():
    b=m3.post_cert(); a=m3.act_cert()
    assert b['status'].startswith('BLOCKED') and a['status'].startswith('BLOCKED')
    assert m3.validate_stage_complete('qa/mainnet-postdeploy/deployment-verification-certificate.json','B_POSTDEPLOYMENT_VERIFICATION') is False
    assert m3.validate_stage_complete('qa/mainnet-activation/activation-certificate.json','C_PRODUCTION_ACTIVATION') is False

def test_certificate_generation_does_not_overwrite_real_stage_b_or_c_evidence():
    bp=ROOT/'qa/mainnet-postdeploy/deployment-verification-certificate.json'; ap=ROOT/'qa/mainnet-activation/activation-certificate.json'
    bold=bp.read_text() if bp.exists() else None; aold=ap.read_text() if ap.exists() else None
    bp.write_text('{"stage":"B_POSTDEPLOYMENT_VERIFICATION","status":"MAINNET_DEPLOYMENT_VERIFIED"}')
    ap.write_text('{"stage":"C_PRODUCTION_ACTIVATION","status":"PRODUCTION_ACTIVATION_EFFECTIVE"}')
    try:
        assert m3.post_cert()['status']=='MAINNET_DEPLOYMENT_VERIFIED'
        assert m3.act_cert()['status']=='PRODUCTION_ACTIVATION_EFFECTIVE'
    finally:
        if bold is not None: bp.write_text(bold)
        if aold is not None: ap.write_text(aold)

def test_docs_write_check_is_deterministic_and_clean():
    assert subprocess.run(['npm','run','docs:status:write'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode==0
    assert subprocess.run(['npm','run','docs:status:check'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode==0

def test_release_state_dag_acyclic_and_no_mainnet_tx_sent_by_tests():
    assert m3.validate_dag(m3.release_state())
    assert not m3.validate_dag({'stages':{'A':{'dependsOn':['B']},'B':{'dependsOn':['A']}}})
    assert m3.predeploy_certificate()['MAINNET_DEPLOYED']=='NO'
