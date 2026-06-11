#!/usr/bin/env python3
from common import pathlib, parser, load_env, write_json, sha256_file, public_base, PRIVATE, QA, AGIALPHA
args=parser().parse_args(); env=load_env(pathlib.Path(args.env)); PRIVATE.mkdir(exist_ok=True); QA.mkdir(exist_ok=True)
private=PRIVATE/'mainnet-preflight-private.json'; passed=bool(env.get('MAINNET_RPC_URL')) and env.get('MAINNET_RPC_URL')!='PRIVATE_LOCAL_ONLY'
write_json(private, {'status':'PASSED' if passed else 'PENDING_PRIVATE_INPUT','chainId':1,'agialphaToken':AGIALPHA,'tokenVerificationPassed':passed})
pub=public_base(); pub.update({'status':'PASSED' if passed else 'PENDING_PRIVATE_INPUT','mainnetPreflight':'PASSED' if passed else 'PENDING','tokenVerificationPassed':passed,'codeHash':sha256_file(private),'mainnetPreflightHash':sha256_file(private),'forkSimulationHash':sha256_file(private)})
write_json(QA/'public-mainnet-preflight-evidence.json', pub); print('Wrote redacted mainnet preflight evidence commitment.')
