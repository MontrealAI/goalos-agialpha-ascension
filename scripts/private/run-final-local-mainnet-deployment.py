#!/usr/bin/env python3
from common import pathlib, parser, read_json, load_env, ROOT, AGIALPHA, non_placeholder, valid_hash

CONFIRMATION = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET"
args = parser().parse_args()
env = load_env(pathlib.Path(args.env))
data = read_json(pathlib.Path(args.input))
auth = read_json(ROOT / "docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json")
dep = read_json(ROOT / "qa/public-mainnet-deployment-authorization-evidence.json")
errors: list[str] = []
if auth.get("status") != "YES" or auth.get("ETHEREUM_MAINNET_AUTHORIZED") != "YES":
    errors.append("Public Ethereum Mainnet authorization JSON is not YES")
if data.get("chain") != "ethereum" or data.get("chainId") != 1:
    errors.append("Private input target is not ethereum chainId 1")
if str(data.get("agialphaToken", "")).lower() != AGIALPHA.lower():
    errors.append("Private input AGIALPHA token mismatch")
if env.get("MAINNET_TARGET") != "ethereum":
    errors.append("MAINNET_TARGET must be ethereum")
if str(env.get("AGIALPHA_TOKEN_ADDRESS", "")).lower() != AGIALPHA.lower():
    errors.append("AGIALPHA_TOKEN_ADDRESS mismatch")
if env.get("PRIVATE_AUTHORIZATION_BUNDLE_STATUS") != "YES":
    errors.append("Private authorization bundle status is not YES")
if not valid_hash(dep.get("founderApprovalCommitmentHash")):
    errors.append("Founder approval commitment hash is missing")
if not non_placeholder(env.get("MAINNET_RPC_URL")):
    errors.append("MAINNET_RPC_URL must be loaded locally")
if env.get("FINAL_DEPLOY_CONFIRMATION") != CONFIRMATION:
    errors.append("Missing exact local typed deployment confirmation")
if errors:
    for error in errors:
        print(f"BLOCKED: {error}")
    raise SystemExit(1)
print("Private local deployment gate passed. Execute the audited Hardhat deployment locally only. No deployment executed by this helper.")
