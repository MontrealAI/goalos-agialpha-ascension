#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
ACT=ROOT/'qa/mainnet-activation'; PRIV=ROOT/'.private/mainnet-activation'
TAG='v4.4.0-mainnet-2026-06-21'; WB='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'; WA='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'; SCOPE='CONTROLLED_PRODUCTION_CANARY_V1'
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def read(p):
 try: return json.loads((ROOT/p if isinstance(p,str) else p).read_text())
 except Exception: return {}
def sha(p):
 p=ROOT/p if isinstance(p,str) else p
 if not p.exists(): return None
 h=hashlib.sha256(); h.update(p.read_bytes()); return '0x'+h.hexdigest()
def hobj(o): return '0x'+hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def git(args):
 try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception: return 'UNKNOWN'
def stage_b_pass():
 c=read('qa/mainnet-postdeploy/deployment-verification-certificate.json')
 return c.get('stage')=='B_POSTDEPLOYMENT_VERIFICATION' and c.get('status') in {'MAINNET_DEPLOYMENT_VERIFIED','VERIFIED'} and c.get('chainId')==1
def source_pass():
 c=read('qa/mainnet-source-identity/source-identity-certificate.json')
 return c.get('status')=='PASS' and c.get('classification')=='EXACT_DEPLOYED_SOURCE_REPRODUCED_BY_COMMIT'
def profile(): return read('config/authorization-profiles/controlled-production-canary-v1.json')
def doctor():
 blockers=[]
 if os.environ.get('CI'): blockers.append('CI environment may not sign or broadcast activation actions')
 if not source_pass(): blockers.append('source-identity certificate is not PASS')
 if not stage_b_pass(): blockers.append('strict Stage-B certificate is not PASS')
 d={'schemaVersion':'1.0','generatedAt':now(),'chainId':1,'walletB':WB,'activationScope':SCOPE,'localOnlySigning':True,'status':'READY_FOR_LOCAL_PREPARATION' if not blockers else 'BLOCKED','blockers':blockers}
 write(ACT/'activation-doctor.json',d); return d
def inventory():
 d={'schemaVersion':'1.0','generatedAt':now(),'activationScope':SCOPE,'walletA':WA,'walletB':WB,'classes':['ON_CHAIN_TRANSACTION','LEDGER_SIGNED_EIP712_ATTESTATION','OFF_CHAIN_OPERATIONAL_CONFIGURATION','NO_ACTION_ALREADY_CORRECT'],'intendedActions':[{'id':'wallet-b-activation-attestation','class':'LEDGER_SIGNED_EIP712_ATTESTATION','signer':WB,'description':'Wallet B signs the hash-bound controlled canary activation statement.'},{'id':'bounded-canary-execution','class':'OFF_CHAIN_OPERATIONAL_CONFIGURATION','description':'Human operator imports sanitized receipts/events after local Ledger ceremony; no CI broadcast.'}], 'status':'INVENTORY_REQUIRES_LIVE_ABI_REVIEW' if not stage_b_pass() else 'INVENTORY_READY'}
 write(ACT/'activation-surface-inventory.json',d); return d
def monitoring():
 for name in ['monitoring-baseline','alert-routing.public','accounting-baseline','recovery-drill']:
  write(ACT/f'{name}.json',{'schemaVersion':'1.0','generatedAt':now(),'activationScope':SCOPE,'status':'READY_FOR_REVIEW','privateCredentialsCommitted':False,'monitors':['code','owner','roles','pause','balances','liabilities','outflows','provider-divergence']})
def plan():
 monitoring(); inv=inventory(); blockers=doctor()['blockers']
 d={'schemaVersion':'1.0','generatedAt':now(),'chainId':1,'releaseTag':TAG,'publishedReleaseTagSha':git(['rev-list','-n','1',TAG]),'reproductionSourceCommitSha':read('qa/mainnet-source-identity/source-identity-certificate.json').get('reproductionSourceCommitSha'),'sourceIdentityCertificateHash':sha('qa/mainnet-source-identity/source-identity-certificate.json'),'stageBCertificateHash':sha('qa/mainnet-postdeploy/deployment-verification-certificate.json'),'activationScope':SCOPE,'walletB':WB,'walletAForbidden':WA,'actions':inv['intendedActions'],'requiresTypedConfirmation':'ACTIVATE_CONTROLLED_PRODUCTION_CANARY_V1','expiresAt':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=7)).isoformat(),'USER_FUNDS_AUTHORIZED':'NO','PUBLIC_UNBOUNDED_RELIANCE':'NO','blockers':blockers,'status':'READY_AND_HASH_BOUND' if not blockers else 'BLOCKED'}
 d['planHash']=hobj({k:v for k,v in d.items() if k!='planHash'}); write(ACT/'activation-plan.public.json',d)
 PRIV.mkdir(parents=True,exist_ok=True); write(PRIV/'activation-plan.private.example.json',{'schemaVersion':'1.0','planHash':d['planHash'],'operatorNotes':'copy to activation-plan.private.json locally; do not commit private material'})
 write(PRIV/'operator.env.example',{'PRIMARY_MAINNET_RPC_URL':'<read-only mainnet RPC>','SECONDARY_MAINNET_RPC_URL':'<independent read-only mainnet RPC>','ETHERSCAN_API_KEY':'<etherscan key>','LEDGER_ACCOUNT':WB,'ACTIVATION_PLAN_HASH':d['planHash']})
 return d
def fork_rehearsal():
 p=plan(); d={'schemaVersion':'1.0','generatedAt':now(),'activationScope':SCOPE,'activationPlanHash':p['planHash'],'executionMode':'MAINNET_FORK','status':'BLOCKED_UNTIL_STAGE_B_AND_SOURCE_IDENTITY_PASS' if p['blockers'] else 'READY_TO_RUN_LOCAL_FORK_REHEARSAL','blockers':p['blockers'],'mainnetBroadcastOccurred':False}
 write(ACT/'fork-rehearsal.json',d); write(ACT/'fork-state-diff.json',d); write(ACT/'fork-accounting-reconciliation.json',d); return d
def prepare_local():
 p=plan(); cmd='./scripts/run-mainnet-activation-ledger.sh --plan qa/mainnet-activation/activation-plan.public.json --expected-plan-hash '+p['planHash']
 d={'schemaVersion':'1.0','status':'READY_FOR_HUMAN_LEDGER_CEREMONY' if not p['blockers'] else 'BLOCKED','blockers':p['blockers'],'exactLocalCommand':cmd,'expectedSanitizedEvidenceBundle':'.private/mainnet-activation/sanitized-evidence-bundle.json'}
 write(ACT/'prepare-local.json',d); return d
def refuse_live(cmd):
 if os.environ.get('CI'): print('REFUSED: CI/cloud cannot sign or broadcast Mainnet activation.'); return 2
 print(json.dumps({'status':'LOCAL_ONLY_NOT_EXECUTED_BY_CODEX','command':cmd,'requiredWalletB':WB,'requiredConfirmation':'ACTIVATE_CONTROLLED_PRODUCTION_CANARY_V1','planHash':read('qa/mainnet-activation/activation-plan.public.json').get('planHash')},indent=2)); return 2
def monitor():
 d={'schemaVersion':'1.0','generatedAt':now(),'status':'BLOCKED_UNTIL_SANITIZED_LIVE_CANARY_EVIDENCE_IMPORTED','healthy':False}; write(ACT/'canary-monitoring.json',d); return d
def reconcile():
 for n in ['canary-receipts','canary-events','canary-accounting','canary-authority-readback','canary-reconciliation','ledger-activation-attestation']:
  write(ACT/f'{n}.json',{'schemaVersion':'1.0','generatedAt':now(),'status':'BLOCKED_UNTIL_REAL_LEDGER_AND_RECEIPT_EVIDENCE'})
 return {'status':'BLOCKED_UNTIL_REAL_LEDGER_AND_RECEIPT_EVIDENCE'}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('cmd'); a=ap.parse_args(); c=a.cmd
 if c=='doctor': print(json.dumps(doctor(),indent=2)); return
 if c=='inventory': print(json.dumps(inventory(),indent=2)); return
 if c=='plan': print(json.dumps(plan(),indent=2)); return
 if c=='fork-rehearsal': print(json.dumps(fork_rehearsal(),indent=2)); return
 if c=='prepare-local': print(json.dumps(prepare_local(),indent=2)); return
 if c in {'ledger-sign','execute-canary','resume','abort'}: sys.exit(refuse_live(c))
 if c=='monitor': print(json.dumps(monitor(),indent=2)); return
 if c=='reconcile': print(json.dumps(reconcile(),indent=2)); return
 raise SystemExit('unknown command '+c)
if __name__=='__main__': main()
