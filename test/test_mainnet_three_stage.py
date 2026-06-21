import importlib.util, pathlib, os, subprocess, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m3', ROOT/'scripts/mainnet_three_stage.py')
m3=importlib.util.module_from_spec(spec); spec.loader.exec_module(m3)

def test_stage_a_fails_closed_without_protected_evidence_and_live_receipts_not_required():
    c=m3.predeploy_certificate()
    assert c['status']=='BLOCKED'
    assert all(v in {'NOT_RUN','FAIL'} for v in c['gates'].values())
    assert c['MAINNET_DEPLOYED']=='NO'
    assert 'LIVE_MAINNET_RECEIPT' not in str(c)

def test_gate_report_schema_and_missing_artifact_not_run():
    r=m3.generate_gate_report('G1')
    assert r['stage']=='A_PREDEPLOYMENT_AUTHORIZATION'
    assert r['status'] in {'NOT_RUN','FAIL','PASS'}
    assert r['requirements'] and {'id','mandatory','status','command','evidence','observed','failureReason'} <= set(r['requirements'][0])

def test_empty_requirements_cannot_pass():
    assert m3.evaluate_report({'requirements':[]})=='NOT_RUN'

def test_stage_a_forbidden_live_or_later_stage_evidence_fails():
    c=m3.predeploy_certificate(); c['evidence'].append({'type':'LIVE_MAINNET_RECEIPT','path':'qa/mainnet-postdeploy/x.json'})
    errs=m3.semantic_lint_stage_a(c)
    assert any('LIVE_MAINNET_RECEIPT' in e for e in errs)
    assert any('mainnet-postdeploy' in e for e in errs)
    c['evidence']=[{'type':'DEPLOYMENT_PLAN','path':'qa/mainnet-activation/canary.json'}]
    assert m3.semantic_lint_stage_a(c)

def test_fork_requires_env_and_does_not_fallback(monkeypatch):
    monkeypatch.delenv('MAINNET_FORK_RPC_URL', raising=False)
    r=m3.fork_report()
    assert r['status']=='NOT_RUN'
    assert not m3.fork_valid(r)
    assert 'fallback' in r['failureReason']

def test_live_local_gated_refuses_in_ci():
    env=os.environ.copy(); env['CI']='true'
    p=subprocess.run(['python','scripts/mainnet_three_stage.py','live-local-gated'],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE)
    assert p.returncode==2 and 'disabled in CI' in p.stdout

def test_stage_b_and_c_are_blocked_before_live_evidence():
    b=m3.post_cert(); a=m3.act_cert()
    assert b['status'].startswith('BLOCKED') and a['status'].startswith('BLOCKED')

def test_release_state_dag_acyclic_and_no_mainnet_tx_sent_by_tests():
    assert m3.validate_dag(m3.release_state())
    assert not m3.validate_dag({'stages':{'A':{'dependsOn':['B']},'B':{'dependsOn':['A']}}})
    assert m3.predeploy_certificate()['MAINNET_DEPLOYED']=='NO'

def test_no_direct_gate_pass_assignment_pattern():
    text=(ROOT/'scripts/mainnet_three_stage.py').read_text()
    forbidden=["'status':'PASS'", '"status":"PASS"', "status = 'PASS'", 'status = "PASS"']
    assert not any(x in text for x in forbidden)


def test_validate_predeploy_regenerates_and_structurally_passes_blocked_certificate(monkeypatch):
    monkeypatch.delenv('MAINNET_FORK_RPC_URL', raising=False)
    ok=m3.validate_predeploy(False)
    c=m3.read(m3.PRE/'authorization-certificate.json')
    assert ok is True
    assert c['status']=='BLOCKED'
    assert c['gates']['Gate 1'] in {'NOT_RUN','FAIL'}

def test_handwritten_gate_pass_artifact_is_rejected(tmp_path):
    base=m3.GATES/'gate-1'
    base.mkdir(parents=True, exist_ok=True)
    ev=base/'fork_topology_deployed.json'
    old=ev.read_text() if ev.exists() else None
    ev.write_text('{"status":"PASS"}')
    try:
        r=m3.generate_gate_report('G1')
        req=next(x for x in r['requirements'] if x['id']=='fork_topology_deployed')
        assert req['status']=='FAIL'
        assert 'schemaVersion' in req['failureReason']
    finally:
        if old is None:
            ev.unlink(missing_ok=True)
        else:
            ev.write_text(old)

def test_stage_b_c_complete_certificates_are_preserved():
    bp=m3.POST/'deployment-verification-certificate.json'; ap=m3.ACT/'activation-certificate.json'
    bold=bp.read_text() if bp.exists() else None; aold=ap.read_text() if ap.exists() else None
    bp.parent.mkdir(parents=True, exist_ok=True); ap.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text('{"schemaVersion":"1.0","stage":"B_POSTDEPLOYMENT_VERIFICATION","status":"MAINNET_DEPLOYMENT_VERIFIED"}')
    ap.write_text('{"schemaVersion":"1.0","stage":"C_PRODUCTION_ACTIVATION","status":"PRODUCTION_ACTIVATION_EFFECTIVE"}')
    try:
        assert m3.post_cert()['status']=='MAINNET_DEPLOYMENT_VERIFIED'
        assert m3.act_cert()['status']=='PRODUCTION_ACTIVATION_EFFECTIVE'
    finally:
        if bold is None: bp.unlink(missing_ok=True)
        else: bp.write_text(bold)
        if aold is None: ap.unlink(missing_ok=True)
        else: ap.write_text(aold)

def test_stage_b_c_validation_dispatch_commands_exist():
    assert subprocess.run(['python','scripts/mainnet_three_stage.py','postdeploy-validate'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode in {0,1}
    assert subprocess.run(['python','scripts/mainnet_three_stage.py','activation-validate'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode in {0,1}
