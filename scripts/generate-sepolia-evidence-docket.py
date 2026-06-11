#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, hashlib, datetime
manifest_path=pathlib.Path('deployments/ethereum-sepolia.agialpha.latest.json')
raw_path=pathlib.Path('evidence/sepolia/SEPOLIA_REHEARSAL_RAW.latest.json')
out=pathlib.Path('evidence/sepolia/SEPOLIA_EVIDENCE_DOCKET.latest.json')
out.parent.mkdir(parents=True, exist_ok=True)
if manifest_path.exists(): manifest=json.loads(manifest_path.read_text())
else: manifest={}
raw=json.loads(raw_path.read_text()) if raw_path.exists() else {}

def max_rehearsal_block_number(raw_artifact: dict) -> int:
    block_numbers = []
    for tx in raw_artifact.get('transactions', []):
        try:
            block_numbers.append(int(tx.get('blockNumber') or 0))
        except (TypeError, ValueError):
            pass
    return max(block_numbers, default=0)


def has_public_sepolia_evidence(raw_artifact: dict) -> bool:
    evidence = raw_artifact.get('networkEvidence')
    if evidence == 'PUBLIC_SEPOLIA_RPC':
        return True
    if isinstance(evidence, dict) and evidence.get('publicSepolia') is True and evidence.get('marker') == 'PUBLIC_SEPOLIA_RPC':
        return True
    # Backward-compatible derivation for real Sepolia artifacts produced before
    # networkEvidence was written: public Sepolia transaction blocks are far above
    # local Hardhat/Anvil rehearsal block heights. This prevents valid public
    # Sepolia runs from requiring hand-edited JSON while still keeping local
    # chainId-11155111 runs pending.
    return raw_artifact.get('chainId') == 11155111 and max_rehearsal_block_number(raw_artifact) >= 1_000_000


if raw.get('status') == 'COMPLETED':
    status = 'COMPLETED_PUBLIC_SEPOLIA' if has_public_sepolia_evidence(raw) else 'COMPLETED_LOCAL_CHAINID_11155111_PUBLIC_SEPOLIA_PENDING'
else:
    status = 'PENDING_REAL_REHEARSAL'

docket={
 'schema':'goalos-agialpha-sepolia-evidence-docket-v4.3+',
 'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':status,
 'chainId':raw.get('chainId', manifest.get('chainId')),
 'deployment_manifest':str(manifest_path),
 'contracts':manifest.get('contracts',{}),
 'agialpha_or_mock':raw.get('mockAGIALPHA') or manifest.get('agialphaToken'),
 'proof_work_loop':raw.get('transactions',[]),
 'negative_paths':raw.get('negativePaths',[]),
 'launch_gate_evidence_hash':raw.get('evidenceHash'),
 'all_core_gates_passed':raw.get('observations',{}).get('allCoreGatesPassed'),
 'privacy_boundary':'public-safe transaction hashes, addresses, event references, hashes and URIs only; no private prompts, raw traces, customer data, legal memos, tax memos, or secrets included',
 'mainnet_authorization':'NOT_AUTHORIZED unless all legal/tax/security/public-claims/treasury/token/sepolia/automated-security/internal-security/founder gates are real and accepted'
}
blob=json.dumps(docket,sort_keys=True).encode(); docket['sha256']='0x'+hashlib.sha256(blob).hexdigest()
out.write_text(json.dumps(docket,indent=2)+'\n')
pathlib.Path('docs/ETHEREUM_SEPOLIA_REHEARSAL_REPORT.md').write_text(f"# Ethereum Sepolia Rehearsal Report\n\nStatus: **{status}**\n\nEvidence Docket: `{out}`\n\nEvidence hash: `{docket.get('launch_gate_evidence_hash')}`\n\nDocket SHA-256: `{docket['sha256']}`\n\nBoundary: local chainId-11155111 rehearsal artifacts do not prove public Ethereum Sepolia execution unless the docket status is `COMPLETED_PUBLIC_SEPOLIA`.\n\nMainnet remains **NOT AUTHORIZED** unless all real gates are complete.\n")
print(json.dumps({'status':status,'path':str(out),'sha256':docket['sha256']},indent=2))
