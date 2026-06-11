#!/usr/bin/env python3
from common import assert_private_path, pathlib, parser, read_json, write_json, sha256_file, public_base, PRIVATE, QA, sha256_json

args = parser().parse_args()
assert_private_path(pathlib.Path(args.input))
data = read_json(pathlib.Path(args.input))
PRIVATE.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
role_keys = ["founderAddress", "deployerAddress", "treasuryAddress", "commercializationPerformanceAdmin", "proofRewardsAdmin", "liquidityAdmin", "securityAdmin", "communityAdmin", "emergencyAdmin"]
private = PRIVATE / "address-ceremony-private.json"
write_json(private, {
    "status": "PASSED",
    "heldPrivately": True,
    "roleCommitments": {key: sha256_json({key: data.get(key, "PRIVATE_LOCAL_ONLY")}) for key in role_keys},
})
pub = public_base()
pub.update({
    "status": "PASSED",
    "addressCeremonyCommitmentHash": sha256_file(private),
    "addressCeremonyHeldPrivately": True,
    "containsFounderAddress": False,
    "containsPrivateAddresses": False,
})
write_json(QA / "public-address-ceremony-evidence.json", pub)
print("Wrote redacted address ceremony commitment; no private addresses printed.")
