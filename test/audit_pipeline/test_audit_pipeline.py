import json, subprocess, tempfile, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
FAIL=ROOT/'scripts/audit/fail-on-critical-findings.py'
SUM=ROOT/'scripts/audit/summarize-audit-results.py'

class AuditPipelineTests(unittest.TestCase):
    def write_summary(self,d,obj):
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

if __name__ == '__main__': unittest.main()
