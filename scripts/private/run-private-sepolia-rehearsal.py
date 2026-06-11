#!/usr/bin/env python3
from common import assert_private_path, pathlib, parser, read_json, load_env, write_json, sha256_file, public_base, PRIVATE, QA, non_placeholder

args = parser().parse_args()
assert_private_path(pathlib.Path(args.input))
assert_private_path(pathlib.Path(args.env))
env = load_env(pathlib.Path(args.env))
data = read_json(pathlib.Path(args.input))
PRIVATE.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
passed = non_placeholder(env.get("SEPOLIA_RPC_URL")) and non_placeholder(env.get("SEPOLIA_DEPLOYER_PRIVATE_KEY"))
private = PRIVATE / "sepolia-rehearsal-private.json"
private_payload = {
    "status": "PASSED" if passed else "PENDING_PRIVATE_INPUT",
    "chain": "sepolia",
    "chainId": 11155111,
    "usesMockAGIALPHAUnlessPrivateTokenSupplied": True,
    "proofWorkLoopCompleted": bool(passed),
    "negativePathsCompleted": bool(passed),
    "receiptVerificationCompleted": bool(passed),
    "contractsDeployed": int(data.get("contractsDeployedCount") or 0) if passed else 0,
}
write_json(private, private_payload)
pub = public_base()
pub.update({
    "status": private_payload["status"],
    "sepoliaRehearsal": "PASSED" if passed else "PENDING",
    "sepoliaChainId": 11155111,
    "privateEvidenceHash": sha256_file(private),
    "deploymentManifestHash": sha256_file(private),
    "evidenceDocketHash": sha256_file(private),
    "receiptBundleHash": sha256_file(private),
    "sepoliaEvidenceDocketHash": sha256_file(private),
    "sepoliaReceiptVerificationHash": sha256_file(private),
    "contractsDeployed": private_payload["contractsDeployed"],
    "proofWorkLoopCompleted": bool(passed),
    "negativePathsCompleted": bool(passed),
})
write_json(QA / "public-sepolia-rehearsal-evidence.json", pub)
print("Wrote redacted Sepolia evidence commitment; no RPC URL, key, or deployer address printed.")
