#!/usr/bin/env python3
from __future__ import annotations
from common import assert_private_path, pathlib, parser, read_json, load_env, write_json, ROOT, QA, AGIALPHA, non_placeholder, valid_hash, now, sha256_json
import os
import subprocess

CONFIRMATION = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET"
args = parser().parse_args()
env_path = pathlib.Path(args.env)
input_path = pathlib.Path(args.input)
assert_private_path(env_path)
assert_private_path(input_path)
local_env = load_env(env_path)
data = read_json(input_path)
auth = read_json(ROOT / "docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json")
dep = read_json(ROOT / "qa/public-mainnet-deployment-authorization-evidence.json")
tech = read_json(ROOT / "qa/public-mainnet-technical-readiness-evidence.json")
errors: list[str] = []
if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true": errors.append("Final mainnet deployment wrapper cannot run in CI")
if auth.get("status") != "YES" or auth.get("ETHEREUM_MAINNET_AUTHORIZED") != "YES": errors.append("Public Ethereum Mainnet authorization JSON is not YES")
if dep.get("deploymentAuthorization") != "YES": errors.append("Redacted deployment authorization evidence is not YES")
if tech.get("technicalReadiness") != "YES": errors.append("Redacted technical readiness evidence is not YES")
if data.get("chain") != "ethereum" or data.get("chainId") != 1: errors.append("Private input target is not ethereum chainId 1")
if str(data.get("agialphaToken", "")).lower() != AGIALPHA.lower(): errors.append("Private input AGIALPHA token mismatch")
if local_env.get("MAINNET_TARGET") != "ethereum": errors.append("MAINNET_TARGET must be ethereum")
if str(local_env.get("AGIALPHA_TOKEN_ADDRESS", "")).lower() != AGIALPHA.lower(): errors.append("AGIALPHA_TOKEN_ADDRESS mismatch")
if local_env.get("PRIVATE_AUTHORIZATION_BUNDLE_STATUS") != "YES" and data.get("privateAuthorizationBundleStatus") != "YES": errors.append("Private authorization bundle status is not YES")
for key in ["FOUNDER_APPROVAL_HASH", "ADDRESS_CEREMONY_HASH", "TOOLCHAIN_CLEARANCE_HASH", "SEPOLIA_EVIDENCE_HASH", "MAINNET_PREFLIGHT_HASH", "AUTHORIZATION_DECISION_HASH"]:
    if not valid_hash(local_env.get(key)): errors.append(f"{key} commitment hash is missing")
if not non_placeholder(local_env.get("MAINNET_RPC_URL")): errors.append("MAINNET_RPC_URL must be loaded locally")
if not non_placeholder(local_env.get("MAINNET_DEPLOYER_PRIVATE_KEY")): errors.append("MAINNET_DEPLOYER_PRIVATE_KEY must be loaded locally")
if local_env.get("FINAL_DEPLOY_CONFIRMATION") != CONFIRMATION: errors.append("Missing exact local typed deployment confirmation")
if errors:
    for error in errors: print(f"BLOCKED: {error}")
    raise SystemExit(1)
print("Final local Ethereum Mainnet deployment checklist:")
for item in ["technical readiness YES", "deployment authorization YES", "Ethereum Mainnet authorization YES", "canonical AGIALPHA token", "private operator inputs loaded", "CI disabled", "typed confirmation present"]:
    print(f"- {item}")
run_env = os.environ.copy()
run_env.update(local_env)
run_env["PRIVATE_MAINNET_RPC_URL"] = local_env.get("MAINNET_RPC_URL", "")
run_env["PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY"] = local_env.get("MAINNET_DEPLOYER_PRIVATE_KEY", "")
run_env["MAINNET_DEPLOYMENT_CONFIRMATION"] = CONFIRMATION
transcript = {"generatedAt": now(), "command": "npm run deploy:ethereum-mainnet:gated", "private": True, "redacted": True}
proc = subprocess.run(["npm", "run", "deploy:ethereum-mainnet:gated"], cwd=ROOT, env=run_env, text=True, capture_output=True)
transcript["returncode"] = proc.returncode
transcript["stdoutRedacted"] = "see local terminal; secrets never intentionally printed"
transcript["stderrRedacted"] = "see local terminal; secrets never intentionally printed" if proc.stderr else ""
write_json(ROOT / ".private/deployment-transcript-private.json", transcript)
commitment = {"redacted": True, "containsSecrets": False, "containsPrivateAddresses": False, "chain": "ethereum", "chainId": 1, "agialphaToken": AGIALPHA, "generatedAt": now(), "deploymentTranscriptCommitmentHash": sha256_json(transcript), "deploymentCommandReturnCode": proc.returncode, "mainnetDeploymentAttemptedLocally": True}
write_json(QA / "public-mainnet-deployment-commitment.json", commitment)
print(proc.stdout)
if proc.returncode != 0:
    print(proc.stderr)
    raise SystemExit(proc.returncode)
