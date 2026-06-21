import importlib.util, json, os, pathlib, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('dm', ROOT/'scripts/dormant_mainnet_v3.py')
dm=importlib.util.module_from_spec(spec); spec.loader.exec_module(dm)
class DormantMainnetV3Tests(unittest.TestCase):
    def test_truth_boundary_flags_are_false_and_status_is_scoped(self):
        c=dm.certificate()
        self.assertNotIn('MAINNET_DEPLOYMENT_AUTHORIZED', c)
        for k in dm.NO_FLAGS: self.assertIs(c[k], False)
        self.assertIn(c['status'], [dm.STATUS, 'BLOCKED_DORMANT_INITIAL_DEPLOYMENT'])
    def test_wallet_a_never_constructor_authority(self):
        plan=dm.plan()
        inv=json.loads((dm.QA/'deployment-instance-inventory.json').read_text())
        self.assertGreater(len(inv['instances']), 40)
        self.assertTrue(all(not i['walletAAppearsInConstructor'] for i in inv['instances']))
        self.assertTrue(all(t['value']=='0' for t in plan['transactions']))
    def test_wallet_b_exact_policy_not_global_allowlist(self):
        pol=dm.policy()
        self.assertNotIn('approvedPermanentAddresses', pol)
        for inst in pol['instances']:
            self.assertEqual(inst['expectedOwner'], dm.WALLET_B)
            self.assertNotEqual(inst['expectedOwner'].lower(), dm.WALLET_A.lower())
            self.assertEqual(inst['expectedRoleHolders']['DEFAULT_ADMIN_ROLE'], [dm.WALLET_B])
    def test_phase_b_forbidden(self):
        plan=dm.plan()
        self.assertFalse(plan['phaseBExecuted'])
        self.assertFalse(plan['phaseBConfigurationAuthorized'])
        self.assertTrue(all(x['forbiddenInDormantMode'] and not x['executed'] for x in plan['phaseBPlan']))
    def test_evidence_claim_guard(self):
        dm.docs(); dm.reports('evidence')
        forbidden=['launched','live for users','safe for deposits','audited','fully secured','production authorized']
        for path in [dm.DOC/'DORMANT_INITIAL_MAINNET_DEPLOYMENT_REPORT.md', dm.ROOT/'docs/DORMANT_MAINNET_AUTHORITY_AND_DORMANCY_MODEL.md']:
            text=path.read_text().lower()
            for phrase in forbidden: self.assertNotIn(phrase, text)
            self.assertIn('not production ready', text)
    def test_deprecated_etherscan_v1_config_absent(self):
        text=(dm.ROOT/'hardhat.config.ts').read_text()
        self.assertIn('apiKey: ETHERSCAN_API_KEY', text)
        self.assertIn('sourcify', text)
        self.assertNotIn('mainnet: ETHERSCAN_API_KEY', text)
    def test_certificate_invalidates_on_wallet_change(self):
        c=dm.certificate(); old=dm.WALLET_A
        try:
            dm.WALLET_A='0x0000000000000000000000000000000000000001'
            errs=dm.validate_cert()
            self.assertTrue(any('walletA' in e for e in errs))
        finally:
            dm.WALLET_A=old; dm.certificate()
    def test_sweep_is_blocked_early(self):
        with self.assertRaises(SystemExit) as cm: dm.live_like('sweep-deployer')
        self.assertIn('Sweep blocked', str(cm.exception))
if __name__=='__main__': unittest.main()
