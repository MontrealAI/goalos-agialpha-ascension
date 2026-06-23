#!/usr/bin/env python3
import argparse, hashlib, json, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
POST=ROOT/'qa/mainnet-postdeploy'
WALLET_B='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'

def load(rel):
    p=ROOT/rel
    return p,json.loads(p.read_text())
def sha_file(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def validate(_args=None):
    sources=['qa/mainnet-release-state.json','deployments/ethereum-mainnet.agialpha.latest.json','qa/mainnet-postdeploy/verification-evidence.json','config/ethereum-mainnet.contracts.json','qa/mainnet-postdeploy/authority-readback.json','qa/mainnet-postdeploy/phase-b-grants-readback.json','qa/mainnet-postdeploy/seed-validation.json','qa/mainnet-postdeploy/wallet-a-zero-authority.json']
    loaded={}; hashes={}
    failures=[]
    for rel in sources:
        try:
            p,d=load(rel); loaded[rel]=d; hashes[rel]=sha_file(p)
        except Exception as e:
            failures.append(f'{rel}: {e}')
    if failures:
        status='FAIL'
    else:
        state=loaded['qa/mainnet-release-state.json']; manifest=loaded['deployments/ethereum-mainnet.agialpha.latest.json']; ver=loaded['qa/mainnet-postdeploy/verification-evidence.json']; registry=loaded['config/ethereum-mainnet.contracts.json']; auth=loaded['qa/mainnet-postdeploy/authority-readback.json']; phase=loaded['qa/mainnet-postdeploy/phase-b-grants-readback.json']; seed=loaded['qa/mainnet-postdeploy/seed-validation.json']; zero=loaded['qa/mainnet-postdeploy/wallet-a-zero-authority.json']
        contracts=manifest.get('contracts') or []
        goalos=[c for c in contracts if c.get('classification')!='external']
        checks={
            'chainId': state.get('deployment',{}).get('chainId')==1 and manifest.get('chainId')==1,
            'deploymentPath': state.get('deployment',{}).get('deploymentPath')=='DIRECT_OPERATOR_NO_CERTIFICATE' and manifest.get('deploymentMode')=='DIRECT_OPERATOR_NO_CERTIFICATE',
            'deployed': state.get('summary',{}).get('ETHEREUM_MAINNET_DEPLOYED')=='YES' and manifest.get('mainnetDeployed') is True,
            'configured': state.get('summary',{}).get('MAINNET_CONFIGURED')=='YES' and manifest.get('mainnetConfigured') is True,
            'registryEntries': len(registry.get('contracts') or [])==49 and len(contracts)==49,
            'goalosContracts': len(goalos)==48,
            'transactions': len(manifest.get('transactions') or [])==48 and len(set(manifest.get('transactions') or []))==48,
            'operatorVerification': ver.get('summary',{}).get('verified')==48 and ver.get('summary',{}).get('failed')==0,
            'phaseBGrants': state.get('summary',{}).get('PHASE_B_GRANTS')=='14/14' and len(manifest.get('phaseBGrants') or [])==14 and seed.get('phaseBGrants')==14 and seed.get('status')=='PASSED_NO_STAGE_B',
            'phaseBReadbackPendingHonest': phase.get('status') in {'REQUIRES_LIVE_RPC_VALIDATION','PENDING_EXTERNAL_INPUT','PASSED'},
            'walletB': manifest.get('walletB','').lower()==WALLET_B.lower() and (auth.get('walletB','').lower()==WALLET_B.lower() or auth.get('permanentAuthority') in ('Wallet B / Ledger','WALLET_B_LEDGER')),
            'walletAZero': state.get('summary',{}).get('WALLET_A_RESIDUAL_MANAGED_ROLES')==0 and zero.get('managedRoleCount')==0,
        }
        failures=[k for k,v in checks.items() if not v]
        status='PASS' if not failures else 'FAIL'
    report={'status':status,'chainId':1,'deploymentPath':'DIRECT_OPERATOR_NO_CERTIFICATE','goalosContracts':48,'registryEntries':49,'operatorVerification':'48/48','phaseBGrants':'14/14','walletAManagedRoles':0,'mainnetConfigured':True,'phaseBGrantEvidenceSource':'operator_seed_validation_and_manifest','phaseBGrantLiveReadback': 'PENDING_EXTERNAL_INPUT' if loaded.get('qa/mainnet-postdeploy/phase-b-grants-readback.json',{}).get('status')=='REQUIRES_LIVE_RPC_VALIDATION' else loaded.get('qa/mainnet-postdeploy/phase-b-grants-readback.json',{}).get('status'),'sourceEvidenceSha256':hashes,'failures':failures,'generatedAt':'2026-06-21T00:00:00Z'}
    write('qa/mainnet-postdeploy/operator-evidence-validation.json',report)
    print(json.dumps(report,indent=2,sort_keys=True))
    if status!='PASS': raise SystemExit(1)
    return report

def certificate(_args=None):
    report=validate(None)
    cert={'schemaVersion':'1.0','certificateType':'OPERATOR_POSTDEPLOYMENT_EVIDENCE','status':'PASS','chainId':1,'deploymentPath':'DIRECT_OPERATOR_NO_CERTIFICATE','postdeploymentStatus':'VERIFIED_AND_CONFIGURED','mainnetDeployed':'YES','mainnetConfigured':'YES','operatorVerification':'48/48','phaseBGrants':'14/14','permanentAuthority':'Wallet B / Ledger','walletAManagedRoles':0,'productionActivation':'NOT_ACTIVATED','userFundAuthorization':'NO','independentLiveRevalidation':'PENDING_EXTERNAL_INPUT','operatorEvidenceValidationSha256':sha_file(ROOT/'qa/mainnet-postdeploy/operator-evidence-validation.json'),'issuedAt':'2026-06-21T00:00:00Z'}
    write('qa/mainnet-postdeploy/operator-postdeployment-certificate.json',cert)
    print('operator postdeployment certificate issued')

def cert_validate(_args=None):
    p,d=load('qa/mainnet-postdeploy/operator-postdeployment-certificate.json')
    required={'status':'PASS','certificateType':'OPERATOR_POSTDEPLOYMENT_EVIDENCE','deploymentPath':'DIRECT_OPERATOR_NO_CERTIFICATE','operatorVerification':'48/48','phaseBGrants':'14/14','walletAManagedRoles':0,'independentLiveRevalidation':'PENDING_EXTERNAL_INPUT'}
    bad=[k for k,v in required.items() if d.get(k)!=v]
    if bad: raise SystemExit('invalid operator certificate: '+', '.join(bad))
    print('operator postdeployment certificate validated')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command'); args=ap.parse_args(); cmd=args.command.split('mainnet:postdeploy:')[-1]
    {'operator-evidence:validate':validate,'operator-certificate':certificate,'operator-certificate:validate':cert_validate}.get(cmd,validate)(args)
if __name__=='__main__': main()
