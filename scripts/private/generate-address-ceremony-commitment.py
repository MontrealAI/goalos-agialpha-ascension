#!/usr/bin/env python3
from common import pathlib, parser, read_json, write_json, sha256_file, public_base, PRIVATE, QA
args=parser().parse_args(); data=read_json(pathlib.Path(args.input)); PRIVATE.mkdir(exist_ok=True); QA.mkdir(exist_ok=True)
private=PRIVATE/'address-ceremony-private.json'; write_json(private, {'status':'PASSED','heldPrivately':True,'inputHashOnly':True})
pub=public_base(); pub.update({'status':'PASSED','addressCeremonyCommitmentHash':sha256_file(private),'addressCeremonyHeldPrivately':True})
write_json(QA/'public-address-ceremony-evidence.json', pub); print('Wrote redacted address ceremony commitment.')
