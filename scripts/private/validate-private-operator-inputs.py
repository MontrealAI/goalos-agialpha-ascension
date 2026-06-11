#!/usr/bin/env python3
from common import assert_private_path, pathlib, parser, read_json, load_env, AGIALPHA, non_placeholder

args = parser().parse_args()
assert_private_path(pathlib.Path(args.input))
assert_private_path(pathlib.Path(args.env))
data = read_json(pathlib.Path(args.input))
env = load_env(pathlib.Path(args.env))
errors: list[str] = []
if data.get("chain") != "ethereum" or data.get("chainId") != 1:
    errors.append("chain must be ethereum with chainId 1")
if str(data.get("agialphaToken", "")).lower() != AGIALPHA.lower():
    errors.append("AGIALPHA token mismatch")
for key in ["SEPOLIA_RPC_URL", "SEPOLIA_DEPLOYER_PRIVATE_KEY", "MAINNET_RPC_URL"]:
    if not non_placeholder(env.get(key)):
        errors.append(f"{key} must be filled locally")
policy = data.get("policyWaivers") or {}
for key in ["legalTokenCounsel", "taxAccounting", "publicClaims"]:
    if policy.get(key) == "required_blocker":
        errors.append(f"policyWaivers.{key} remains required_blocker")
print({"status": "PASSED" if not errors else "FAILED", "errors": errors})
raise SystemExit(1 if errors else 0)
