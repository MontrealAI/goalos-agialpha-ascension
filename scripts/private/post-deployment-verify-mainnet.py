#!/usr/bin/env python3
from __future__ import annotations
from common import ROOT, QA, AGIALPHA, parser, read_json, write_json, assert_private_path, load_env, rpc_chain_id, rpc_call, now, sha256_json, pathlib

args = parser().parse_args()
env_path = pathlib.Path(args.env)
input_path = pathlib.Path(args.input)
assert_private_path(env_path)
assert_private_path(input_path)
env = load_env(env_path)
manifest = read_json(ROOT / "deployments/ethereum-mainnet.agialpha.latest.json")
errors: list[str] = []
if manifest.get("chainId") != 1 or manifest.get("chain") != "ethereum":
    errors.append("deployment manifest is not Ethereum Mainnet")
if str(manifest.get("agialphaToken", "")).lower() != AGIALPHA.lower():
    errors.append("AGIALPHA token mismatch")
if manifest.get("mockAgialphaUsed") is not False or manifest.get("newAgialphaTokenDeployed") is not False:
    errors.append("manifest indicates forbidden AGIALPHA token behavior")
rpc = env.get("MAINNET_RPC_URL") or env.get("PRIVATE_MAINNET_RPC_URL")
if not rpc:
    errors.append("MAINNET_RPC_URL missing from private environment")
else:
    if rpc_chain_id(rpc) != 1:
        errors.append("RPC is not Ethereum Mainnet chainId 1")
    for name, meta in (manifest.get("contracts") or {}).items():
        address = meta.get("address") if isinstance(meta, dict) else meta
        if address:
            code = rpc_call(rpc, "eth_getCode", [address, "latest"])
            if not code or code == "0x":
                errors.append(f"contract has no code: {name}")
private_report = {"generatedAt": now(), "private": True, "errors": errors, "manifestHash": sha256_json(manifest)}
write_json(ROOT / ".private/post-deployment-verify-mainnet-private.json", private_report)
public = {"redacted": True, "containsSecrets": False, "containsPrivateAddresses": False, "chain": "ethereum", "chainId": 1, "agialphaToken": AGIALPHA, "generatedAt": now(), "postDeploymentVerification": "FAILED" if errors else "PASSED", "manifestHash": sha256_json(manifest), "errors": errors}
write_json(QA / "public-post-deployment-verification.json", public)
print("POST_DEPLOYMENT_VERIFICATION_FAILED" if errors else "POST_DEPLOYMENT_VERIFICATION_PASSED")
for error in errors:
    print(f"- {error}")
raise SystemExit(1 if errors else 0)
