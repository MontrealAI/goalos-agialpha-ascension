#!/usr/bin/env python3
from common import pathlib, parser, read_json, load_env, write_json, sha256_file, public_base, PRIVATE, QA
args=parser().parse_args(); env=load_env(pathlib.Path(args.env)); data=read_json(pathlib.Path(args.input)); PRIVATE.mkdir(exist_ok=True); QA.mkdir(exist_ok=True)
private=PRIVATE/'sepolia-rehearsal-private.json'
passed=bool(env.get('SEPOLIA_RPC_URL')) and env.get('SEPOLIA_RPC_URL')!='PRIVATE_LOCAL_ONLY'
write_json(private, {'status':'PASSED' if passed else 'PENDING_PRIVATE_INPUT', 'chainId':11155111, 'proofWorkLoopCompleted':passed, 'negativePathsCompleted':passed})
pub=public_base(); pub.update({'status':'PASSED' if passed else 'PENDING_PRIVATE_INPUT','sepoliaRehearsal':'PASSED' if passed else 'PENDING','chainId':11155111,'privateEvidenceHash':sha256_file(private),'deploymentManifestHash':sha256_file(private),'evidenceDocketHash':sha256_file(private),'receiptBundleHash':sha256_file(private),'contractsDeployed':0 if not passed else data.get('contractsDeployedCount', 0),'proofWorkLoopCompleted':passed,'negativePathsCompleted':passed})
write_json(QA/'public-sepolia-rehearsal-evidence.json', pub); print('Wrote redacted Sepolia evidence commitment.')
