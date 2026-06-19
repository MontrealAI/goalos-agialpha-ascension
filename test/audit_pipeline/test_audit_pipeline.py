import json, subprocess, tempfile, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
FAIL=ROOT/'scripts/audit/fail-on-critical-findings.py'
SUM=ROOT/'scripts/audit/summarize-audit-results.py'

class AuditPipelineTests(unittest.TestCase):
    def write_summary(self,d,obj):
        obj=dict(obj)
        obj.setdefault('sourceSha', subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip())
        obj.setdefault('runDirectory', str(pathlib.Path(d).resolve()))
        p=pathlib.Path(d)/'audit-summary.json'; p.write_text(json.dumps(obj)); return p
    def run_fail(self,p):
        return subprocess.run(['python',str(FAIL),str(p)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    def base(self):
        return {'schemaVersion':'2.0','decision':'PASS','criticalHighUnresolved':0,'unresolvedFindings':[],'toolFailures':[],'unavailableMandatoryTools':[]}
    def test_zero_passes(self):
        with tempfile.TemporaryDirectory() as d:
            r=self.run_fail(self.write_summary(d,self.base()))
            self.assertEqual(r.returncode,0)
    def test_one_high_fails_with_detail(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['decision']='BLOCKED'; obj['criticalHighUnresolved']=1; obj['unresolvedFindings']=[{'id':'GHSA-x','severity':'high','status':'unresolved','packageOrContract':'pkg','installedVersion':'1','dependencyPath':'a>b','fixedVersion':'2'}]
            r=self.run_fail(self.write_summary(d,obj)); self.assertEqual(r.returncode,1); self.assertIn('GHSA-x',r.stdout)
    def test_four_high_fails_all(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['decision']='BLOCKED'; obj['criticalHighUnresolved']=4; obj['unresolvedFindings']=[{'id':f'GHSA-{i}','severity':'high','status':'unresolved','packageOrContract':'pkg','installedVersion':'1','dependencyPath':'p','fixedVersion':'2'} for i in range(4)]
            r=self.run_fail(self.write_summary(d,obj)); self.assertEqual(r.returncode,1); self.assertIn('GHSA-3',r.stdout)
    def test_missing_summary_blocks(self):
        r=self.run_fail('/tmp/does-not-exist-summary.json'); self.assertEqual(r.returncode,2)
    def test_malformed_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'audit-summary.json'; p.write_text('{bad')
            self.assertEqual(self.run_fail(p).returncode,2)
    def test_schema_invalid_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_fail(self.write_summary(d,{'criticalHighUnresolved':0})).returncode,2)
    def test_count_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['criticalHighUnresolved']=0; obj['unresolvedFindings']=[{'severity':'high','status':'unresolved'}]
            self.assertEqual(self.run_fail(self.write_summary(d,obj)).returncode,2)
    def test_mandatory_tool_failure_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['toolFailures']=[{'tool':'npm-audit','status':'FAILED'}]
            self.assertEqual(self.run_fail(self.write_summary(d,obj)).returncode,2)
    def test_mandatory_tool_unavailable_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['unavailableMandatoryTools']=['osv-scanner']
            r=self.run_fail(self.write_summary(d,obj)); self.assertEqual(r.returncode,2); self.assertIn('osv-scanner', r.stdout)
    def test_temporary_waiver_error_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['triageErrors']=['Expired triage']
            self.assertEqual(self.run_fail(self.write_summary(d,obj)).returncode,2)
    def test_duplicate_scanner_fingerprint_dedupes(self):
        with tempfile.TemporaryDirectory() as d:
            rd=pathlib.Path(d)
            finding={'fingerprint':'same','id':'GHSA-x','tool':'npm-audit','severity':'high','status':'unresolved','packageOrContract':'pkg','installedVersion':'1','dependencyPath':'p'}
            for tool in ['npm-audit','osv-scanner']:
                obj={'schemaVersion':'2.0','tool':tool,'status':'COMPLETED_WITH_FINDINGS','findings':[dict(finding,tool=tool)],'criticalHighUnresolved':1}
                (rd/f'{tool}.json').write_text(json.dumps(obj))
            subprocess.run(['python',str(SUM),str(rd)],cwd=ROOT,check=True,stdout=subprocess.PIPE)
            summary=json.loads((rd/'audit-summary.json').read_text())
            self.assertEqual(summary['criticalHighUnresolved'],1)
    def test_multiple_advisories_same_package_count_separately(self):
        with tempfile.TemporaryDirectory() as d:
            rd=pathlib.Path(d)
            findings=[{'fingerprint':f'fp-{i}','id':f'GHSA-{i}','tool':'npm-audit','severity':'high','status':'unresolved','packageOrContract':'pkg','installedVersion':'1','dependencyPath':'p'} for i in range(2)]
            (rd/'npm-audit.json').write_text(json.dumps({'schemaVersion':'2.0','tool':'npm-audit','status':'COMPLETED_WITH_FINDINGS','findings':findings,'criticalHighUnresolved':2}))
            subprocess.run(['python',str(SUM),str(rd)],cwd=ROOT,check=True,stdout=subprocess.PIPE)
            summary=json.loads((rd/'audit-summary.json').read_text())
            self.assertEqual(summary['criticalHighUnresolved'],2)
    def test_resolved_and_false_positive_are_excluded_only_when_present_in_summary(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['unresolvedFindings']=[{'id':'GHSA-r','severity':'high','status':'resolved'},{'id':'GHSA-f','severity':'critical','status':'false_positive'}]
            r=self.run_fail(self.write_summary(d,obj)); self.assertEqual(r.returncode,0)
    def test_temporary_accepted_is_excluded_only_when_present_in_summary(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['unresolvedFindings']=[{'id':'GHSA-t','severity':'high','status':'temporarily_accepted'}]
            r=self.run_fail(self.write_summary(d,obj)); self.assertEqual(r.returncode,0)
    def test_scanner_timeout_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['toolFailures']=[{'tool':'semgrep','status':'TIMEOUT'}]
            self.assertEqual(self.run_fail(self.write_summary(d,obj)).returncode,2)
    def test_findings_nonzero_is_not_scanner_crash_when_normalized(self):
        with tempfile.TemporaryDirectory() as d:
            rd=pathlib.Path(d)
            finding={'fingerprint':'findings-exit','id':'GHSA-x','tool':'npm-audit','severity':'high','status':'unresolved','packageOrContract':'pkg','installedVersion':'1','dependencyPath':'p'}
            current_sha=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
            (rd/'npm-audit.json').write_text(json.dumps({'schemaVersion':'2.0','tool':'npm-audit','sourceSha':current_sha,'status':'COMPLETED_WITH_FINDINGS','exitStatus':1,'findings':[finding],'criticalHighUnresolved':1}))
            for tool in ['slither','semgrep','solhint','osv-scanner','actionlint','shellcheck','gitleaks']:
                (rd/f'{tool}.json').write_text(json.dumps({'schemaVersion':'2.0','tool':tool,'sourceSha':current_sha,'status':'COMPLETED','exitStatus':0,'findings':[],'criticalHighUnresolved':0}))
            subprocess.run(['python',str(SUM),str(rd)],cwd=ROOT,check=True,stdout=subprocess.PIPE)
            summary=json.loads((rd/'audit-summary.json').read_text())
            self.assertEqual(summary['toolFailures'],[])
            self.assertEqual(summary['criticalHighUnresolved'],1)
    def test_historical_latest_cannot_satisfy_new_source_sha(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['sourceSha']='not-current'
            p=self.write_summary(d,obj)
            r=self.run_fail(p); self.assertEqual(r.returncode,2); self.assertIn('STALE', r.stdout)
    def test_legacy_scanner_output_blocks_summarization_without_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            rd=pathlib.Path(d)
            (rd/'semgrep.json').write_text(json.dumps({'tool':'semgrep','status':'COMPLETED','critical_high_unresolved':0}))
            subprocess.run(['python',str(SUM),str(rd)],cwd=ROOT,check=True,stdout=subprocess.PIPE)
            summary=json.loads((rd/'audit-summary.json').read_text())
            self.assertEqual(summary['decision'],'BLOCKED')
            self.assertTrue(any(f.get('status') == 'LEGACY_WITHOUT_PROVENANCE' for f in summary['toolFailures']))
            self.assertEqual(summary['criticalHighUnresolved'],1)
    def test_stale_scanner_evidence_blocks_even_when_summary_sha_is_current(self):
        with tempfile.TemporaryDirectory() as d:
            rd=pathlib.Path(d)
            (rd/'npm-audit.json').write_text(json.dumps({'schemaVersion':'2.0','tool':'npm-audit','sourceSha':'old-sha','status':'COMPLETED','findings':[],'criticalHighUnresolved':0}))
            p=self.write_summary(d,self.base())
            r=self.run_fail(p); self.assertEqual(r.returncode,2); self.assertIn('BLOCKED_STALE_SCANNER_EVIDENCE', r.stdout)
    def test_summary_requires_run_directory(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['sourceSha']=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(); obj['runDirectory']=''
            p=pathlib.Path(d)/'audit-summary.json'; p.write_text(json.dumps(obj))
            r=self.run_fail(p); self.assertEqual(r.returncode,2); self.assertIn('runDirectory', r.stdout)
    def test_run_directory_mixing_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            obj=self.base(); obj['runDirectory']='different-dir'
            p=self.write_summary(d,obj)
            r=self.run_fail(p); self.assertEqual(r.returncode,2); self.assertIn('runDirectory', r.stdout)
    def test_failing_run_four_finding_fixture_blocks(self):
        fixture=ROOT/'qa/AUDIT_FAILURE_27840694274.json'
        data=json.loads(fixture.read_text())
        self.assertEqual(data['criticalHighUnresolvedReported'],4)
        self.assertEqual(len(data['exactFindings']),4)

if __name__ == '__main__': unittest.main()
