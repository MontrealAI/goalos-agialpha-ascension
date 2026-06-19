#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
AGIALPHA="0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
READINESS=ROOT/'qa/mainnet-readiness'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(args):
    try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return 'UNKNOWN'
def read(rel):
    try: return json.loads((ROOT/rel).read_text())
    except Exception: return {}
def sha(rel):
    p=ROOT/rel
    if not p.exists(): return None
    if p.is_dir():
        h=hashlib.sha256()
        for f in sorted(x for x in p.rglob('*') if x.is_file()):
            h.update(str(f.relative_to(ROOT)).encode()); h.update(b'\0'); h.update(f.read_bytes()); h.update(b'\n')
        return '0x'+h.hexdigest()
    return '0x'+hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    # Regenerate the canonical five-gate dossier first.  This command is intentionally
    # allowed to return non-zero because BLOCKED is valid evidence, not an exception.
    subprocess.run(['python','scripts/mainnet_operational_readiness.py'],cwd=ROOT,check=False,stdout=subprocess.DEVNULL)
    gate_files={
        'G1':'qa/mainnet-readiness/gate-1-authority.json',
        'G2':'qa/mainnet-readiness/gate-2-overrides.json',
        'G3':'qa/mainnet-readiness/gate-3-accounting.json',
        'G4':'qa/mainnet-readiness/gate-4-lifecycle.json',
        'G5':'qa/mainnet-readiness/gate-5-assurance.json',
    }
    gates={k:read(v) for k,v in gate_files.items()}
    fork=read('qa/mainnet-readiness/fork-rehearsal.json')
    docket=read('qa/mainnet-readiness/security-docket.json')
    prod=read('qa/mainnet-readiness/production-readiness.json')
    release=read('qa/mainnet-readiness/release-identity.json')
    blockers=[]
    for gate,report in gates.items():
        if report.get('status')!='PASS':
            blockers.append(f'{gate} is {report.get("status","MISSING")}: '+ '; '.join(report.get('blockers') or ['missing PASS evidence']))
    if fork.get('status')!='PASS': blockers.append('Mainnet fork rehearsal is not PASS: '+ '; '.join(fork.get('blockers') or ['missing live fork evidence']))
    if docket.get('status')!='PASS': blockers.append('Security docket is not PASS: '+ '; '.join(docket.get('blockers') or ['missing assurance evidence']))
    if prod.get('MAINNET_DEPLOYED')!='NO' or prod.get('MAINNET_VERIFIED')!='NO': blockers.append('Production readiness attempted to claim live Mainnet deployment/verification without chain-1 evidence.')
    ready='YES' if not blockers else 'NO'
    evidence_paths={
        'releaseIdentity':'qa/mainnet-readiness/release-identity.json',
        'systemInventory':'qa/mainnet-readiness/system-inventory.json',
        'gate1Authority':gate_files['G1'], 'gate2Overrides':gate_files['G2'], 'gate3Accounting':gate_files['G3'], 'gate4Lifecycle':gate_files['G4'], 'gate5Assurance':gate_files['G5'],
        'forkRehearsal':'qa/mainnet-readiness/fork-rehearsal.json',
        'securityDocket':'qa/mainnet-readiness/security-docket.json',
        'productionReadiness':'qa/mainnet-readiness/production-readiness.json',
        'operationalDossier':'qa/mainnet-production-readiness-dossier.json',
        'packageScripts':'package.json',
    }
    evidence={k:{'path':v,'sha256':sha(v)} for k,v in evidence_paths.items()}
    cert={'schemaVersion':'2.0','generatedAt':now(),'generatedBy':'scripts/generate-mainnet-authorization-certificate.py','repository':'MontrealAI/goalos-agialpha-ascension','commit':git(['rev-parse','HEAD']),'sourceCommit':git(['rev-parse','HEAD']),'branch':git(['branch','--show-current']),'gitValidationMode':'GIT_CHECKOUT','releaseIdentity':release.get('sourceTreeHash'),'sourceTreeHash':release.get('sourceTreeHash'),'dependencyLockHash':release.get('dependencyLockHash'),'chain':'ethereum','chainId':1,'agialphaToken':AGIALPHA,'scope':'five-gate-technical-readiness-certificate-non-broadcasting','mainnetDeployed':'NO','MAINNET_DEPLOYED':'NO','MAINNET_VERIFIED':'NO','LIVE_OWNER_HANDOFF_COMPLETE':'NO','LIVE_CANARY_COMPLETE':'NO','runtimeSecretsStoredInGitHub':False,'ciCanDeployMainnet':False,'privateOperatorAuthorizationPackageRequired':False,'notExternallyAudited':True,'externalAuditRequired':False,'externalAuditPlanned':False,'technicallyMainnetReady':ready,'TECHNICALLY_READY_FOR_CONTROLLED_MAINNET_DEPLOYMENT':ready,'mainnetDeploymentAuthorized':ready,'ethereumMainnetAuthorized':ready,'authorization':'AUTHORIZED' if ready=='YES' else 'NOT_AUTHORIZED','gates':{k:v.get('status','MISSING') for k,v in gates.items()},'evidence':evidence,'blockers':blockers,'warnings':[],'claimBoundary':'No Ethereum Mainnet broadcast, deployment, verification, live owner handoff, or live canary completion is claimed by this certificate.'}
    canonical=json.dumps({k:v for k,v in cert.items() if k!='certificateHash'},sort_keys=True,separators=(',',':'))
    cert['certificateHash']='0x'+hashlib.sha256(canonical.encode()).hexdigest()
    (ROOT/'qa').mkdir(exist_ok=True); (ROOT/'qa/mainnet-authorization-certificate.json').write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
    (READINESS/'authorization-certificate.json').write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
    print(json.dumps(cert,indent=2,sort_keys=True))
if __name__=='__main__': main()
