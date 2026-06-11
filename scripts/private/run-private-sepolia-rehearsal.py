#!/usr/bin/env python3
from common import assert_private_path, pathlib, parser, read_json, load_env, write_json, sha256_file, public_base, PRIVATE, QA, non_placeholder, rpc_chain_id, valid_hash

args = parser().parse_args()
assert_private_path(pathlib.Path(args.input))
assert_private_path(pathlib.Path(args.env))
env = load_env(pathlib.Path(args.env))
PRIVATE.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
private = PRIVATE / "sepolia-rehearsal-private.json"
existing = read_json(private)
errors: list[str] = []
chain_id = None
try:
    chain_id = rpc_chain_id(env.get("SEPOLIA_RPC_URL", ""))
    if chain_id != 11155111:
        errors.append(f"SEPOLIA_RPC_URL chainId must be 11155111; got {chain_id}")
except Exception as exc:
    errors.append(f"Private Sepolia RPC chainId check failed locally: {type(exc).__name__}")
if not non_placeholder(env.get("SEPOLIA_DEPLOYER_PRIVATE_KEY")):
    errors.append("SEPOLIA_DEPLOYER_PRIVATE_KEY must be present locally")
if existing:
    required_true = ["proofWorkLoopCompleted", "negativePathsCompleted", "receiptVerificationCompleted"]
    for key in required_true:
        if existing.get(key) is not True:
            errors.append(f"Private Sepolia evidence missing true {key}")
    if existing.get("chainId") != 11155111:
        errors.append("Private Sepolia evidence chainId mismatch")
    if existing.get("status") not in {"PASSED", "COMPLETED"}:
        errors.append("Private Sepolia evidence status is not PASSED/COMPLETED")
else:
    errors.append("Missing .private/sepolia-rehearsal-private.json produced by the local Sepolia proof-work replay")

def private_commitment_hash(primary_key: str, fallback_key: str | None = None) -> str:
    for key in [primary_key, fallback_key]:
        if not key:
            continue
        value = existing.get(key)
        if value is None:
            continue
        if valid_hash(value):
            return value
        errors.append(f"Private Sepolia field {key} must be a 0x-prefixed sha256 commitment; raw values are not publishable")
    return sha256_file(private)

passed = not errors
if not existing:
    write_json(private, {
        "status": "PENDING_PRIVATE_REHEARSAL",
        "chain": "sepolia",
        "chainId": chain_id or 11155111,
        "usesMockAGIALPHAUnlessPrivateTokenSupplied": True,
        "proofWorkLoopCompleted": False,
        "negativePathsCompleted": False,
        "receiptVerificationCompleted": False,
        "contractsDeployed": 0,
        "errors": errors,
    })
    existing = read_json(private)
pub = public_base()
pub.update({
    "status": "PASSED" if passed else "PENDING_PRIVATE_REHEARSAL",
    "sepoliaRehearsal": "PASSED" if passed else "PENDING",
    "sepoliaChainId": 11155111,
    "privateEvidenceHash": sha256_file(private),
    "deploymentManifestHash": private_commitment_hash("deploymentManifestHash"),
    "evidenceDocketHash": private_commitment_hash("evidenceDocketHash"),
    "receiptBundleHash": private_commitment_hash("receiptBundleHash"),
    "sepoliaEvidenceDocketHash": private_commitment_hash("sepoliaEvidenceDocketHash", "evidenceDocketHash"),
    "sepoliaReceiptVerificationHash": private_commitment_hash("sepoliaReceiptVerificationHash", "receiptBundleHash"),
    "contractsDeployed": int(existing.get("contractsDeployed") or 0),
    "proofWorkLoopCompleted": existing.get("proofWorkLoopCompleted") is True,
    "negativePathsCompleted": existing.get("negativePathsCompleted") is True,
    "blockers": errors,
})
# Recompute after optional commitment validation to ensure malformed private fields
# make the public commitment pending and never leak verbatim into qa/.
passed = not errors
pub["status"] = "PASSED" if passed else "PENDING_PRIVATE_REHEARSAL"
pub["sepoliaRehearsal"] = "PASSED" if passed else "PENDING"
pub["blockers"] = errors
write_json(QA / "public-sepolia-rehearsal-evidence.json", pub)
print("Wrote redacted Sepolia evidence commitment; no RPC URL, key, or deployer address printed.")
raise SystemExit(0 if passed else 1)
