#!/usr/bin/env python3
"""Import a reviewed manual Mainnet read-only revalidation artifact.

This script is intentionally offline. It validates that the artifact contains a
Stage-B certificate and the evidence files bound by that certificate before
copying public evidence into qa/mainnet-postdeploy. It never talks to Ethereum
and never requests signing material.
"""
from __future__ import annotations
import hashlib, json, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REQUIRED_EVIDENCE={
  'receipt-revalidation.json',
  'runtime-bytecode-readback.json',
  'authority-readback.json',
  'phase-b-configuration-readback.json',
  'verification-evidence.json',
}
CERT='deployment-verification-certificate.json'

def digest_json(path: Path) -> str:
    return hashlib.sha256(json.dumps(json.loads(path.read_text()),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def fail(msg: str) -> None:
    raise SystemExit(f'import-reviewed-evidence refused: {msg}')

def main() -> None:
    if len(sys.argv)!=2:
        fail('usage: npm run mainnet:live:import-reviewed-evidence -- <artifact-directory>')
    src=Path(sys.argv[1]).resolve()
    if not src.is_dir(): fail(f'not a directory: {src}')
    meta_path=src/'workflow-run-metadata.json'
    cert_path=src/'qa/mainnet-postdeploy'/CERT if (src/'qa/mainnet-postdeploy'/CERT).exists() else src/CERT
    evidence_dir=cert_path.parent
    if not cert_path.exists(): fail('missing Stage-B certificate')
    if meta_path.exists():
        meta=json.loads(meta_path.read_text())
        if meta.get('event_name')!='workflow_dispatch': fail('workflow must be manual workflow_dispatch')
        if meta.get('ref_protected') is False: fail('workflow ref must be protected/default branch')
        if not meta.get('source_sha'): fail('missing source SHA')
    cert=json.loads(cert_path.read_text())
    if cert.get('status')!='MAINNET_DEPLOYMENT_VERIFIED': fail('certificate is not favorable Stage-B')
    roots=cert.get('evidenceRoots') or {}
    missing=REQUIRED_EVIDENCE-set(roots)
    if missing: fail('certificate missing evidence roots: '+','.join(sorted(missing)))
    for name in REQUIRED_EVIDENCE:
        p=evidence_dir/name
        if not p.exists(): fail(f'missing evidence file {name}')
        if roots.get(name)!=digest_json(p): fail(f'evidence root mismatch for {name}')
    dest=ROOT/'qa/mainnet-postdeploy'
    dest.mkdir(parents=True,exist_ok=True)
    for name in sorted(REQUIRED_EVIDENCE|{CERT}):
        shutil.copy2(evidence_dir/name,dest/name)
    print('imported reviewed Mainnet read-only evidence artifact')

if __name__=='__main__':
    main()
