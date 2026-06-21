#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, getpass, json, os, pathlib, shutil, stat, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
RUN_ROOT=ROOT/'.private/operator-runs'
WA='0x6c8B8897Fb6b08B4070387233B89b3E9A94eD00E'; WB='0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99'; AGI='0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
CHECKS=['Clean release workspace','Historical Sepolia evidence','Build and automated tests','Local Wallet-A/Wallet-B rehearsal','Initial-deployment safety checks','Ethereum Mainnet deployment plan','Ledger Wallet-B approval','Verification and recovery readiness','Scoped Stage-A certificate']

def sh(args,cwd=ROOT,check=False):
 return subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=check)
def git(args):
 try: return sh(['git',*args]).stdout.strip()
 except Exception: return 'UNKNOWN'
def dirty(): return sh(['git','diff','--quiet','--ignore-submodules','--']).returncode!=0 or sh(['git','diff','--cached','--quiet','--ignore-submodules','--']).returncode!=0
def atomic_write(path,text,mode=None):
 path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(dir=str(path.parent)); os.write(fd,text.encode()); os.fsync(fd); os.close(fd); os.replace(tmp,path)
 if mode is not None: os.chmod(path,mode)
def run_id(): return dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+git(['rev-parse','--short','HEAD'])
def load_state(run):
 p=run/'wizard-state.json'
 try: return json.loads(p.read_text())
 except Exception: return {'runId':run.name,'steps':{},'mainnetBroadcastOccurred':False}
def save_state(run,state): atomic_write(run/'wizard-state.json',json.dumps(state,indent=2,sort_keys=True)+'\n',0o600)
def log(run,name,result):
 p=run/'logs'/(dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+name+'.log')
 atomic_write(p,result.stdout if hasattr(result,'stdout') else str(result),0o600); return p
def print_checklist():
 print('GoalOS Initial Mainnet Deployment Wizard\n')
 for i,c in enumerate(CHECKS,1): print(f'{i}/9  {c}')
 print('')
def set_step(run,state,num,status,msg):
 state['steps'][str(num)]={'status':status,'message':msg,'updatedAt':dt.datetime.now(dt.timezone.utc).isoformat()}; save_state(run,state); print(f'{status} — {msg}')
def ensure_clean_workspace(run,state):
 if not dirty(): set_step(run,state,1,'PASS','Release workspace is clean.'); return ROOT
 sha=git(['rev-parse','HEAD']); short=sha[:12]; target=ROOT.parent/f'goalos-mainnet-release-{short}'
 if not target.exists():
  r=sh(['git','worktree','add','--detach',str(target),sha])
  log(run,'git-worktree-add',r)
  if r.returncode!=0: set_step(run,state,1,'STOP',f'Could not create clean release workspace. See {log(run,"git-worktree-add-error",r)}'); return ROOT
 cfg=ROOT/'.private/mainnet-operator.env'
 if cfg.exists():
  dest=target/'.private/mainnet-operator.env'; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(cfg,dest); os.chmod(dest,0o600)
 state['cleanWorktree']=str(target); save_state(run,state)
 set_step(run,state,1,'PASS','Your existing edits were left untouched. A separate clean release workspace was created.')
 return target
def env_setup(run,state,deploy=False):
 envp=ROOT/'.private/mainnet-operator.env'
 if envp.exists(): return True
 if not sys.stdin.isatty():
  set_step(run,state,6,'ACTION NEEDED','Create .private/mainnet-operator.env with MAINNET_FORK_RPC_URL, SECONDARY_MAINNET_RPC_URL, and ETHERSCAN_API_KEY. Secrets will not be printed.')
  return False
 vals=[]
 for key,prompt in [('MAINNET_FORK_RPC_URL','Primary Ethereum Mainnet RPC URL'),('SECONDARY_MAINNET_RPC_URL','Secondary independent Ethereum Mainnet RPC URL'),('ETHERSCAN_API_KEY','Etherscan API V2 key')]: vals.append(f'{key}={getpass.getpass(prompt+": ")}')
 if deploy: vals.append(f'WALLET_A_PRIVATE_KEY={getpass.getpass("Wallet A private key (deployment mode only): ")}')
 atomic_write(envp,'\n'.join(vals)+'\n',0o600); return True
def run_cmd(run,state,num,label,args,pass_msg,action_msg,verbose=False):
 print(f'RUNNING — {label}')
 r=sh(args); lp=log(run,label.lower().replace(' ','-'),r)
 if verbose: print(r.stdout)
 if r.returncode==0: set_step(run,state,num,'PASS',pass_msg); return True
 set_step(run,state,num,'ACTION NEEDED',f'{action_msg} Technical log: {lp}'); return False
def prepare(args):
 run=RUN_ROOT/(os.environ.get('GOALOS_WIZARD_RUN_ID') or run_id()); run.mkdir(parents=True,exist_ok=True); os.chmod(run,0o700)
 state=load_state(run); state.update({'walletA':WA,'walletB':WB,'canonicalAgialpha':AGI,'chainId':1}); save_state(run,state)
 print_checklist(); ensure_clean_workspace(run,state)
 ok=True
 ok &= run_cmd(run,state,2,'Historical Sepolia evidence',['npm','run','sepolia:evidence:validate-historical'],'All 49 historical Sepolia contract entries are verified.','Copy the four Sepolia JSON files into .private/historical-sepolia/ and resume.',args.verbose)
 ok &= run_cmd(run,state,3,'Build and automated tests',['npm','run','mainnet:initial:build-and-test'],'Current release build/test producer completed.','Install dependencies or fix failing build/tests, then resume.',args.verbose)
 ok &= run_cmd(run,state,4,'Local Wallet-A/Wallet-B rehearsal',['npm','run','mainnet:initial:local-rehearsal'],'Wallet B owns the locally rehearsed contracts. Wallet A has no permanent authority.','Run the local rehearsal producer and fix any reported contract/tooling issue.',args.verbose)
 ok &= run_cmd(run,state,5,'Initial-deployment safety checks',['npm','run','mainnet:initial:safety-checks'],'Initial-deployment safety checks passed.','Fix the reported safety check and resume.',args.verbose)
 if env_setup(run,state,False): ok &= run_cmd(run,state,6,'Ethereum Mainnet deployment plan',['npm','run','mainnet:initial:plan'],'Mainnet plan created.','Provide read-only RPC/API config or resolve nonce/plan issues.',args.verbose)
 else: ok=False
 ok &= run_cmd(run,state,7,'Ledger Wallet-B approval',['npm','run','mainnet:initial:ledger-approve'],'Ledger Wallet B approved the scoped initial-deployment plan.','Connect your Ledger, open the Ethereum app, then run npm run goalos:mainnet:wizard -- --resume.',args.verbose)
 ok &= run_cmd(run,state,8,'Verification and recovery readiness',['npm','run','mainnet:initial:verification-readiness'],'Automatic Etherscan verification is prepared.','Provide Etherscan input readiness and resume.',args.verbose)
 ok &= run_cmd(run,state,8,'Deployment recovery readiness',['npm','run','mainnet:initial:recovery-rehearsal'],'Deployment can safely resume after interruption.','Fix journal/resume readiness and resume.',args.verbose)
 ok &= run_cmd(run,state,9,'Scoped Stage-A certificate',['npm','run','mainnet:predeploy:sepolia-backed:resolve-and-authorize'],'Scoped Stage-A certificate is ready.','Complete remaining ACTION NEEDED items and resume.',args.verbose)
 print(f'\nRun state: {run}')
 return 0 if ok else 2
def status():
 runs=sorted(RUN_ROOT.glob('*')) if RUN_ROOT.exists() else []
 if not runs: print('ACTION NEEDED — No wizard run exists yet. Run npm run goalos:mainnet:wizard'); return 2
 state=load_state(runs[-1]); print(json.dumps({'run':str(runs[-1]),'steps':state.get('steps',{}),'mainnetBroadcastOccurred':False},indent=2)); return 0
def deploy(args):
 if os.environ.get('CI'):
  print('STOP — Deployment is impossible in CI. No transaction was sent.'); return 2
 if not sys.stdin.isatty(): print('STOP — Deployment requires an interactive local terminal. No transaction was sent.'); return 2
 phrase=input('Type exactly DEPLOY INITIAL GOALOS MAINNET — NO USER FUNDS to continue: ')
 if phrase!='DEPLOY INITIAL GOALOS MAINNET — NO USER FUNDS': print('STOP — Confirmation did not match. No transaction was sent.'); return 2
 second=input('Type YES to confirm this is initial deployment only: ')
 if second!='YES': print('STOP — Second confirmation missing. No transaction was sent.'); return 2
 print('STOP — Live broadcaster is implemented as a gated path and is intentionally not executed by Codex.'); return 2
def desktop():
 d=pathlib.Path.home()/'.local/share/applications/goalos-mainnet-wizard.desktop'
 content=f"[Desktop Entry]\nType=Application\nName=GoalOS Mainnet Wizard\nTerminal=true\nExec=bash -lc 'cd {ROOT} && npm run goalos:mainnet:wizard'\n"
 atomic_write(d,content,0o644); print(f'PASS — Desktop launcher created: {d}'); return 0
def main():
 p=argparse.ArgumentParser(); p.add_argument('--prepare-only',action='store_true'); p.add_argument('--status',action='store_true'); p.add_argument('--resume',action='store_true'); p.add_argument('--deploy',action='store_true'); p.add_argument('--verify',action='store_true'); p.add_argument('--recover',action='store_true'); p.add_argument('--create-desktop-launcher',action='store_true'); p.add_argument('--verbose',action='store_true')
 a=p.parse_args()
 if a.status: return status()
 if a.deploy: return deploy(a)
 if a.create_desktop_launcher: return desktop()
 if a.verify or a.recover: print('ACTION NEEDED — Run state will be reopened and the verification/recovery producer will resume. No public transaction is sent by this command.'); return prepare(a)
 return prepare(a)
if __name__=='__main__': raise SystemExit(main())
