import json, os, pathlib, subprocess, sys, tempfile, unittest, importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('dormant', ROOT/'scripts/dormant_mainnet.py')
dormant=importlib.util.module_from_spec(spec); spec.loader.exec_module(dormant)
RAW_TEMP='0x'+'6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'
RAW_OWNER='0x'+'d76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'

def run_scan(path):
    env=os.environ.copy(); env['NO_PRIVATE_OPERATOR_SCAN_PATHS']=str(path.relative_to(ROOT))
    return subprocess.run([sys.executable,'scripts/no_private_operator_data_check.py'],cwd=ROOT,env=env,text=True,capture_output=True)

class DormantCertificateTests(unittest.TestCase):
    def setUp(self):
        self.cert=dormant.compute()
    def tmp_repo_file(self, rel, obj):
        p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2)+'\n'); self.addCleanup(lambda: p.unlink(missing_ok=True)); return p
    def test_raw_address_failures_reproduce_for_old_certificate_and_plan(self):
        p=self.tmp_repo_file('qa/dormant-mainnet-readiness/raw-cert.test.json', {'temporaryDeployer':RAW_TEMP})
        self.assertNotEqual(run_scan(p).returncode,0)
        p2=self.tmp_repo_file('qa/dormant-mainnet-readiness/raw-plan.test.json', {'admin':RAW_OWNER})
        self.assertNotEqual(run_scan(p2).returncode,0)
    def test_commitment_only_certificate_and_public_plan_pass(self):
        self.assertEqual(run_scan(ROOT/'qa/dormant-mainnet-readiness/authorization-certificate.json').returncode,0)
        self.assertEqual(run_scan(ROOT/'qa/dormant-mainnet-readiness/deployment-plan.public.json').returncode,0)
    def test_private_overlay_validates_locally_and_address_change_invalidates(self):
        (ROOT/'.private').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'.private') as td:
            p=pathlib.Path(td)/'operator-config.json'
            payload=dormant.operator_payload(); p.write_text(json.dumps({'temporaryDeployerAddress':payload['temporaryDeployerAddress'],'finalLedgerOwnerAddress':payload['finalLedgerOwnerAddress'],'permanentRoleAddresses':payload['permanentRoleAddresses']},indent=2)); p.chmod(0o600)
            ok,errs=dormant.validate_private_overlay(p, json.loads((ROOT/'qa/dormant-mainnet-readiness/deployment-plan.public.json').read_text())); self.assertTrue(ok, errs)
            data=json.loads(p.read_text()); data['finalLedgerOwnerAddress']='0x0000000000000000000000000000000000000001'; p.write_text(json.dumps(data)); p.chmod(0o600)
            ok,errs=dormant.validate_private_overlay(p, json.loads((ROOT/'qa/dormant-mainnet-readiness/deployment-plan.public.json').read_text())); self.assertFalse(ok); self.assertTrue(any('mismatch' in e for e in errs))
    def test_tracking_private_overlay_fails(self):
        p=self.tmp_repo_file('.private/dormant-mainnet/operator-config.scan-test.json', {'temporaryDeployerAddress':RAW_TEMP})
        self.assertNotEqual(run_scan(p).returncode,0)
    def test_missing_private_overlay_ci_ok_but_prepare_blocks(self):
        self.assertEqual(dormant.validate()[0:0], [])
        r=subprocess.run([sys.executable,'scripts/dormant_mainnet.py','prepare'],cwd=ROOT,text=True,capture_output=True)
        self.assertNotEqual(r.returncode,0); self.assertIn('private operator overlay', r.stdout+r.stderr)
    def test_receipt_backed_postdeployment_passes_fake_fails(self):
        base={'temporaryDeployer':RAW_TEMP,'chainId':1,'deploymentStatus':'DEPLOYED_DORMANT','transactionHashes':['0x'+'11'*32],'receipts':[{'status':1}], 'allReceiptsSuccessful':True,'runtimeBytecodeHashesMatch':True,'canonicalAgialphaMatches':True,'ownerRoleReadbackSucceeded':True,'temporaryDeployerResidualAuthority':0,'officialFunding':0,'activation':False}
        good=self.tmp_repo_file('qa/dormant-mainnet-deployment/good.test.json', base); self.assertEqual(run_scan(good).returncode,0)
        bad=dict(base); bad.pop('receipts'); fake=self.tmp_repo_file('qa/dormant-mainnet-deployment/fake.test.json', bad); self.assertNotEqual(run_scan(fake).returncode,0)
    def test_dormant_yes_cannot_change_production_or_bypass_recompute(self):
        c=json.loads(json.dumps(self.cert)); c['PRODUCTION_MAINNET_DEPLOYMENT_AUTHORIZED']='YES'
        with tempfile.NamedTemporaryFile('w',delete=False,suffix='.json') as f: json.dump(c,f); name=f.name
        self.addCleanup(lambda: pathlib.Path(name).unlink(missing_ok=True)); self.assertTrue(any('PRODUCTION' in e for e in dormant.validate(name)))
        c=json.loads(json.dumps(self.cert)); c['blockers']=[]
        for k in dormant.DORM_YES: c[k]='YES'
        with tempfile.NamedTemporaryFile('w',delete=False,suffix='.json') as f: json.dump(c,f); name2=f.name
        self.addCleanup(lambda: pathlib.Path(name2).unlink(missing_ok=True)); self.assertTrue(any('freshly computed' in e or 'blockers' in e for e in dormant.validate(name2)))
    def test_final_check_blocks_when_not_ready_and_generation_deterministic(self):
        self.assertTrue(any('final-check requires' in e for e in dormant.validate(require_ready=True)))
        self.assertEqual(dormant.compute()['certificateHash'], dormant.compute()['certificateHash'])
    def test_ci_broadcast_refused_without_logs_leaking_address(self):
        env=os.environ.copy(); env['CI']='true'
        r=subprocess.run([sys.executable,'scripts/dormant_mainnet.py','live-local-gated'],cwd=ROOT,env=env,text=True,capture_output=True)
        self.assertNotEqual(r.returncode,0); self.assertNotIn(RAW_TEMP, r.stdout+r.stderr)

if __name__=='__main__': unittest.main()
