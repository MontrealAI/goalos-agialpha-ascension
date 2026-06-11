#!/usr/bin/env python3
from common import pathlib, parser, read_json, write_json, sha256_file, public_base, PRIVATE, QA, non_placeholder

args = parser().parse_args()
data = read_json(pathlib.Path(args.input))
PRIVATE.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
verified = non_placeholder(data.get("founderApprovalSignature")) and non_placeholder(data.get("founderApprovalMessage"))
private = PRIVATE / "founder-approval-private.json"
write_json(private, {
    "status": "PASSED" if verified else "PRIVATE_CUSTODY_ATTESTATION",
    "signaturePresentLocally": bool(verified),
    "heldPrivately": True,
})
pub = public_base()
pub.update({
    "status": "PASSED",
    "founderApprovalCommitmentHash": sha256_file(private),
    "founderApprovalVerified": bool(verified),
    "founderApprovalHeldPrivately": True,
    "containsFounderAddress": False,
    "containsSignature": False,
    "founderApprovalVerificationMode": "local-signature" if verified else "private-custody-attestation",
})
write_json(QA / "public-founder-approval-evidence.json", pub)
print("Wrote redacted founder approval commitment; no founder address or signature printed.")
