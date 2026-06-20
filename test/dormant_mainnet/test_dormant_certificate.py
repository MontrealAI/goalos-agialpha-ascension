import json, pathlib, tempfile, unittest
import importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('dormant', ROOT/'scripts/dormant_mainnet.py')
dormant=importlib.util.module_from_spec(spec); spec.loader.exec_module(dormant)

class DormantCertificateNegativeTests(unittest.TestCase):
    def setUp(self):
        self.cert=dormant.compute()
        self.cert['blockers']=[]
        for k in dormant.DORM_YES: self.cert[k]='YES'
        self.cert['temporaryDeployerPermanentAuthority']=0
        self.cert['officialFundingTotal']=0
        self.cert['riskIncreasingEntryPointsDisabled']=True
        self.cert['mockTokenEnabled']=False
    def write_validate(self, mut):
        c=json.loads(json.dumps(self.cert)); mut(c)
        with tempfile.NamedTemporaryFile('w',delete=False,suffix='.json') as f:
            json.dump(c,f); name=f.name
        try: return dormant.validate(pathlib.Path(name))
        finally: pathlib.Path(name).unlink(missing_ok=True)
    def assertFails(self, mut, text):
        errs=self.write_validate(mut); self.assertTrue(any(text in e for e in errs), errs)
    def test_production_fields_yes_fail(self): self.assertFails(lambda c: c.update(PRODUCTION_MAINNET_DEPLOYMENT_AUTHORIZED='YES'), 'PRODUCTION_MAINNET_DEPLOYMENT_AUTHORIZED')
    def test_user_funds_activation_public_reliance_fail(self):
        for field in ['USER_FUNDS_AUTHORIZED','PROTOCOL_ACTIVATION_AUTHORIZED','PUBLIC_RELIANCE_AUTHORIZED']:
            self.assertFails(lambda c, f=field: c.update({f:'YES'}), field)
    def test_mock_token_enabled_fails(self): self.assertFails(lambda c: c.update(mockTokenEnabled=True), 'mock token is enabled')
    def test_chain_id_or_token_wrong_fails(self): self.assertFails(lambda c: c.update(chainId=5), 'chain ID/token is wrong')
    def test_temporary_deployer_authority_fails(self): self.assertFails(lambda c: c.update(temporaryDeployerPermanentAuthority=1), 'temporary deployer has permanent authority')
    def test_ledger_owner_absent_fails(self): self.assertFails(lambda c: c.update(ledgerOwner='0x0000000000000000000000000000000000000000'), 'Ledger Owner is absent')
    def test_nonzero_funding_fails(self): self.assertFails(lambda c: c.update(officialFundingTotal=1), 'funding is nonzero')
    def test_risk_entrypoint_not_disabled_fails(self): self.assertFails(lambda c: c.update(riskIncreasingEntryPointsDisabled=False), 'risk-increasing entry point')
    def test_fork_evidence_missing_or_stale_fails(self): self.assertFails(lambda c: c['evidence']['forkRehearsal'].update(sha256='0xdeadbeef'), 'certificate or source hash changes')
    def test_verification_inputs_incomplete_fail(self): self.assertFails(lambda c: c['evidence']['deploymentPlan'].pop('sha256'), 'verification inputs are incomplete')
    def test_certificate_source_hash_changes_fail(self): self.assertFails(lambda c: c['evidence']['certificateScript'].update(sha256='0xdeadbeef'), 'certificate or source hash changes')
    def test_ci_attempts_mainnet_broadcast_refused(self):
        import os, subprocess, sys
        env=os.environ.copy(); env['CI']='true'
        r=subprocess.run([sys.executable, str(ROOT/'scripts/dormant_mainnet.py'), 'live-local-gated'], cwd=ROOT, env=env, text=True, capture_output=True)
        self.assertNotEqual(r.returncode,0); self.assertIn('Refusing dormant Mainnet broadcast in CI', r.stderr+r.stdout)

if __name__=='__main__': unittest.main()
