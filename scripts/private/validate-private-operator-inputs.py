#!/usr/bin/env python3
from common import pathlib, parser, read_json, load_env, AGIALPHA
args=parser().parse_args(); data=read_json(pathlib.Path(args.input)); env=load_env(pathlib.Path(args.env)); errors=[]
if data.get('chain')!='ethereum' or data.get('chainId')!=1: errors.append('chain must be ethereum/1')
if str(data.get('agialphaToken','')).lower()!=AGIALPHA.lower(): errors.append('AGIALPHA token mismatch')
for key in ['SEPOLIA_RPC_URL','MAINNET_RPC_URL']:
    if not env.get(key) or 'PRIVATE_LOCAL_ONLY' in env.get(key,''): errors.append(f'{key} must be filled locally')
print({'status':'PASSED' if not errors else 'FAILED','errors':errors})
raise SystemExit(1 if errors else 0)
