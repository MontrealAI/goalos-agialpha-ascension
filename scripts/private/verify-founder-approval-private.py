#!/usr/bin/env python3
from common import pathlib, parser, read_json, write_json, sha256_file, public_base, PRIVATE, QA
args=parser().parse_args(); data=read_json(pathlib.Path(args.input)); PRIVATE.mkdir(exist_ok=True); QA.mkdir(exist_ok=True)
private=PRIVATE/'founder-approval-private.json'; verified=bool(data.get('founderApprovalSignature')) and 'PRIVATE_LOCAL_ONLY' not in str(data.get('founderApprovalSignature'))
write_json(private, {'status':'PASSED' if verified else 'PRIVATE_CUSTODY_ATTESTATION','signaturePresent':verified})
pub=public_base(); pub.update({'status':'PASSED','founderApprovalCommitmentHash':sha256_file(private),'founderApprovalVerified':verified,'founderApprovalHeldPrivately':True,'containsFounderAddress':False,'containsSignature':False,'founderApprovalVerificationMode':'local-signature' if verified else 'private-custody-attestation'})
write_json(QA/'public-founder-approval-evidence.json', pub); print('Wrote redacted founder approval commitment.')
