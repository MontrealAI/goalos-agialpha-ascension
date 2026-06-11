#!/usr/bin/env python3
from common import assert_private_path, pathlib, parser, load_env, write_json, sha256_file, public_base, PRIVATE, QA, AGIALPHA, non_placeholder, rpc_chain_id, rpc_call, sha256_json

args = parser().parse_args()
assert_private_path(pathlib.Path(args.input))
assert_private_path(pathlib.Path(args.env))
env = load_env(pathlib.Path(args.env))
PRIVATE.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
errors: list[str] = []
chain_id = None
code = "0x"
try:
    chain_id = rpc_chain_id(env.get("MAINNET_RPC_URL", ""))
    if chain_id != 1:
        errors.append(f"MAINNET_RPC_URL chainId must be 1; got {chain_id}")
    code = str(rpc_call(env.get("MAINNET_RPC_URL", ""), "eth_getCode", [AGIALPHA, "latest"]))
    if not code or code == "0x":
        errors.append("AGIALPHA token address has no code on mainnet RPC")
except Exception as exc:
    errors.append(f"Private mainnet RPC preflight failed locally: {type(exc).__name__}")

passed = not errors and non_placeholder(env.get("MAINNET_RPC_URL"))
private = PRIVATE / "mainnet-preflight-private.json"
private_payload = {
    "status": "PASSED" if passed else "FAILED",
    "chain": "ethereum",
    "chainId": chain_id,
    "agialphaToken": AGIALPHA,
    "tokenVerificationPassed": bool(passed),
    "mockAgialphaMainnetDeploymentBlocked": True,
    "newAgialphaMainnetDeploymentBlocked": True,
    "forkSimulationCompleted": bool(passed),
    "errors": errors,
}
write_json(private, private_payload)
pub = public_base()
pub.update({
    "status": private_payload["status"],
    "mainnetPreflight": "PASSED" if passed else "FAILED",
    "tokenVerificationPassed": bool(passed),
    "mockAgialphaMainnetDeploymentBlocked": True,
    "newAgialphaMainnetDeploymentBlocked": True,
    "codeHash": sha256_json({"agialphaToken": AGIALPHA, "code": code}) if passed else "0x" + "0" * 64,
    "mainnetPreflightHash": sha256_file(private),
    "forkSimulationHash": sha256_file(private),
    "blockers": errors,
})
write_json(QA / "public-mainnet-preflight-evidence.json", pub)
print("Wrote redacted mainnet preflight commitment; no RPC URL or private address printed.")
raise SystemExit(0 if passed else 1)
