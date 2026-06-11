#!/usr/bin/env python3
from common import pathlib, parser, read_json, load_env, ROOT, AGIALPHA
args=parser().parse_args(); env=load_env(pathlib.Path(args.env)); auth=read_json(ROOT/'docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json')
if auth.get('status')!='YES': raise SystemExit('Public Ethereum Mainnet authorization JSON is not YES.')
if env.get('FINAL_DEPLOY_CONFIRMATION')!='DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET': raise SystemExit('Missing local typed deployment confirmation.')
print('Private local deployment gate passed. Run npm run deploy:ethereum-mainnet:gated locally with private env loaded. No deployment executed by this helper.')
