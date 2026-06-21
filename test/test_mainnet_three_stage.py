import importlib.util, pathlib, os, subprocess, json, shutil
import pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m3', ROOT/'scripts/mainnet_three_stage.py')
m3=importlib.util.module_from_spec(spec); spec.loader.exec_module(m3)

@pytest.fixture(autouse=True)
def clear_public_protected_evidence(monkeypatch):
    shutil.rmtree(ROOT/'qa/mainnet-predeploy/evidence', ignore_errors=True)
    subprocess.run(['git','checkout','--','qa/mainnet-predeploy/fork-rehearsal.json','qa/mainnet-predeploy/authorization-certificate.json','qa/mainnet-predeploy/deployment-plan.public.json','qa/mainnet-predeploy/gates'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    yield
    shutil.rmtree(ROOT/'qa/mainnet-predeploy/evidence', ignore_errors=True)
    subprocess.run(['git','checkout','--','qa/mainnet-predeploy/fork-rehearsal.json','qa/mainnet-predeploy/authorization-certificate.json','qa/mainnet-predeploy/deployment-plan.public.json','qa/mainnet-predeploy/gates'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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

def test_stage_b_minimal_status_string_does_not_validate():
    bp=m3.POST/'deployment-verification-certificate.json'
    old=bp.read_text() if bp.exists() else None
    bp.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text('{"schemaVersion":"1.0","stage":"B_POSTDEPLOYMENT_VERIFICATION","status":"MAINNET_DEPLOYMENT_VERIFIED"}')
    try:
        assert m3.validate_stage_complete('qa/mainnet-postdeploy/deployment-verification-certificate.json','B_POSTDEPLOYMENT_VERIFICATION',{'MAINNET_DEPLOYMENT_VERIFIED','VERIFIED'}) is False
    finally:
        if old is None: bp.unlink(missing_ok=True)
        else: bp.write_text(old)

def test_existing_fork_and_complete_plan_are_preserved():
    forkp=m3.PRE/'fork-rehearsal.json'; planp=m3.PRE/'deployment-plan.public.json'
    oldf=forkp.read_text() if forkp.exists() else None; oldp=planp.read_text() if planp.exists() else None
    rid=m3.release_identity()
    fork={'schemaVersion':'1.0','executionMode':'MAINNET_FORK','upstreamChainId':1,'localChainId':31337,'forkBlockNumber':1,'forkBlockHash':'0xabc','canonicalAgialphaCodeHash':'0xdef','releaseIdentity':rid,'mainnetBroadcastOccurred':False,'status':'PASS'}
    plan={'schemaVersion':'1.0','stage':'A_PREDEPLOYMENT_AUTHORIZATION','releaseIdentity':rid,'chainId':1,'canonicalAgialpha':m3.AGI,'status':'PASS','orderedTransactions':[{'nonce':0}],'startingNonce':0,'planHash':'0x123'}
    forkp.parent.mkdir(parents=True, exist_ok=True); forkp.write_text(json.dumps(fork))
    planp.write_text(json.dumps(plan))
    try:
        assert m3.fork_report()['status']=='PASS'
        assert m3.plan_public()['status']=='PASS'
    finally:
        if oldf is None: forkp.unlink(missing_ok=True)
        else: forkp.write_text(oldf)
        if oldp is None: planp.unlink(missing_ok=True)
        else: planp.write_text(oldp)

def test_live_local_gated_invokes_canonical_deployer_when_authorized(monkeypatch):
    calls=[]
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.setattr(m3, 'validate_predeploy', lambda require_authorized=False: True)
    monkeypatch.setattr(m3.subprocess, 'call', lambda argv, cwd=None: calls.append((argv,cwd)) or 7)
    old_argv=m3.sys.argv[:]
    try:
        m3.sys.argv=['mainnet_three_stage.py','live-local-gated']
        try:
            m3.main()
        except SystemExit as exc:
            assert exc.code==7
    finally:
        m3.sys.argv=old_argv
    assert calls and calls[0][0]==['npm','run','deploy:ethereum-mainnet:gated']

def _write_valid_protected_package(root):
    root.mkdir(parents=True, exist_ok=True)
    rid=m3.git(['rev-parse','HEAD'])
    def write(name,obj):
        p=root/name; p.write_text(json.dumps(obj,sort_keys=True)); return p
    req=[{'id':'r','status':'PASS','evidenceHashes':['0x1']}]
    base={'schemaVersion':'1.0','releaseId':rid,'mainnetBroadcastOccurred':False,'requirements':req,'generatedBy':'fixture-tool','toolVersions':{},'rawEvidenceCommitments':{'log':'0x1'},'failures':[],'blockers':[]}
    files={}
    files['G1_AUTHORITY']=write('g1.json',{**base,'status':'PASS','observed':{'walletAZeroAuthority':True,'walletBPermanentAuthority':True}})
    files['G2_OVERRIDES']=write('g2.json',{**base,'status':'PASS','observed':{'typedOverrideCoverage':True}})
    files['G3_ACCOUNTING']=write('g3.json',{**base,'status':'PASS','observed':{'omittedAccountingComponents':0}})
    files['G4_LIFECYCLE']=write('g4.json',{**base,'status':'PASS','observed':{'unclassifiedSelectors':0}})
    files['G5_ASSURANCE']=write('g5.json',{**base,'status':'PASS','observed':{'invariantExecutedActions':1000000,'deterministicSeedCount':32,'mutationSurvived':0}})
    plan={'schemaVersion':'1.0','releaseId':rid,'chainId':1,'canonicalAgialpha':m3.AGI,'walletA':m3.WA,'walletB':m3.WB,'startingNonce':7,'orderedTransactions':[{'nonce':7,'expectedCreateAddress':'0x0000000000000000000000000000000000000001'}],'maximumCumulativeCost':'100','planHash':'0xplan','expiresAt':'2999-01-01T00:00:00Z','mainnetBroadcastOccurred':False}
    files['DEPLOYMENT_PLAN']=write('plan.json',plan)
    fork={'schemaVersion':'1.0','releaseId':rid,'executionMode':'MAINNET_FORK','upstreamChainId':1,'localChainId':31337,'forkBlockNumber':123,'forkBlockHash':'0xabc','forkBlockTimestamp':1,'primaryProviderCommitment':'0xp','secondaryProviderCommitment':'0xs','canonicalAgialpha':m3.AGI,'upstreamCanonicalAgialphaCodeHash':'0xcode','localForkCanonicalAgialphaCodeHash':'0xcode','deploymentPlanHash':'0xplan','deployedTopologyCount':49,'transactionReceiptCount':63,'runtimeBytecodeRoot':'0xruntime','mainnetBroadcastOccurred':False}
    files['MAINNET_FORK']=write('fork.json',fork)
    import hashlib
    def shp(p): return '0x'+hashlib.sha256(p.read_bytes()).hexdigest()
    idx={'schemaVersion':'1.0','releaseId':rid,'gitCommit':rid,'chainId':1,'walletA':m3.WA,'walletB':m3.WB,'canonicalAgialpha':m3.AGI,'entries':[{'type':t,'path':str(p),'sha256':shp(p),'schemaVersion':'1.0','releaseId':rid,'publicDisclosure':'COMMITMENT_ONLY'} for t,p in files.items()]}
    idx['indexSha256']='0xidx'
    (root/'protected-evidence-index.json').write_text(json.dumps(idx,sort_keys=True))
    return root/'protected-evidence-index.json'

def test_valid_protected_package_can_authorize_stage_a(tmp_path, monkeypatch):
    idx=_write_valid_protected_package(tmp_path/'protected')
    monkeypatch.setenv('GOALOS_PROTECTED_EVIDENCE_INDEX', str(idx))
    assert subprocess.run(['python','scripts/protected_stage_a_evidence.py','validate'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode==0
    assert subprocess.run(['python','scripts/protected_stage_a_evidence.py','import'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode==0
    c=m3.predeploy_certificate()
    assert c['status']=='AUTHORIZED'
    assert all(v=='PASS' for v in c['gates'].values())
    assert c['MAINNET_DEPLOYED']=='NO'

def test_missing_protected_evidence_doctor_fails_when_no_inputs(monkeypatch):
    for k in list(os.environ):
        if k.startswith('GOALOS_'):
            monkeypatch.delenv(k, raising=False)
    assert subprocess.run(['python','scripts/protected_stage_a_evidence.py','doctor'],cwd=ROOT,stdout=subprocess.PIPE,text=True).returncode in {2}

def test_valid_untracked_protected_evidence_authorizes_stage_a(tmp_path, monkeypatch):
    private_root=ROOT/'.private'/'mainnet-predeploy'/'pytest-untracked-stage-a'
    if private_root.exists():
        import shutil; shutil.rmtree(private_root)
    idx=_write_valid_protected_package(private_root)
    try:
        monkeypatch.setenv('GOALOS_PROTECTED_EVIDENCE_INDEX', str(idx))
        result=subprocess.run(['python','scripts/mainnet_three_stage.py','resolve-and-authorize'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        assert result.returncode==0, result.stdout
        assert 'AUTHORIZED_TO_DEPLOY_ON_ETHEREUM_MAINNET' in result.stdout
        assert 'committed evidence state remains blocked by missing protected Gate 1–5' not in result.stdout
        assert (ROOT/'qa/mainnet-predeploy/evidence/protected-evidence-commitments.json').exists()
        cert=json.loads((ROOT/'qa/mainnet-predeploy/authorization-certificate.json').read_text())
        assert cert['status']=='AUTHORIZED'
        assert all(v=='PASS' for v in cert['gates'].values())
        tracked=subprocess.run(['git','ls-files','--error-unmatch',str(idx.relative_to(ROOT))],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert tracked.returncode!=0
    finally:
        import shutil; shutil.rmtree(private_root, ignore_errors=True)

def test_missing_or_invalid_protected_evidence_blocks_stage_a(tmp_path, monkeypatch):
    bad=tmp_path/'bad'; bad.mkdir()
    p=bad/'g1.json'; p.write_text(json.dumps({'schemaVersion':'1.0','releaseId':m3.git(['rev-parse','HEAD']),'status':'FAIL','mainnetBroadcastOccurred':False}))
    monkeypatch.setenv('GOALOS_PROTECTED_EVIDENCE_ROOT', str(bad))
    monkeypatch.delenv('GOALOS_PROTECTED_EVIDENCE_INDEX', raising=False)
    result=subprocess.run(['python','scripts/mainnet_three_stage.py','resolve-and-authorize'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    assert result.returncode!=0
    assert 'AUTHORIZED_TO_DEPLOY_ON_ETHEREUM_MAINNET' not in result.stdout
    assert 'specific protected evidence validation failed' in result.stdout or 'BLOCKED' in result.stdout
