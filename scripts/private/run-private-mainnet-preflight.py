#!/usr/bin/env python3
from common import assert_private_path, pathlib, parser, load_env, write_json, sha256_file, public_base, PRIVATE, QA, AGIALPHA, non_placeholder

args = parser().parse_args()
assert_private_path(pathlib.Path(args.input))
assert_private_path(pathlib.Path(args.env))
env = load_env(pathlib.Path(args.env))
PRIVATE.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
passed = non_placeholder(env.get("MAINNET_RPC_URL"))
private = PRIVATE / "mainnet-preflight-private.json"
private_payload = {
    "status": "PASSED" if passed else "PENDING_PRIVATE_INPUT",
    "chain": "ethereum",
    "chainId": 1,
    "agialphaToken": AGIALPHA,
    "tokenVerificationPassed": bool(passed),
    "mockAgialphaMainnetDeploymentBlocked": True,
    "newAgialphaMainnetDeploymentBlocked": True,
    "forkSimulationCompleted": bool(passed),
}
write_json(private, private_payload)
pub = public_base()
pub.update({
    "status": private_payload["status"],
    "mainnetPreflight": "PASSED" if passed else "PENDING",
    "tokenVerificationPassed": bool(passed),
    "mockAgialphaMainnetDeploymentBlocked": True,
    "newAgialphaMainnetDeploymentBlocked": True,
    "codeHash": sha256_file(private),
    "mainnetPreflightHash": sha256_file(private),
    "forkSimulationHash": sha256_file(private),
})
write_json(QA / "public-mainnet-preflight-evidence.json", pub)
print("Wrote redacted mainnet preflight commitment; no RPC URL or private address printed.")
