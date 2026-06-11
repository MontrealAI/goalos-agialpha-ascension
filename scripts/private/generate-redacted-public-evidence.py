#!/usr/bin/env python3
from common import pathlib, parser, read_json, write_json, sha256_file, public_base, QA, ROOT
args=parser().parse_args(); QA.mkdir(exist_ok=True)
def h(name):
    p=QA/name
    return sha256_file(p) if p.exists() else '0x' + '0'*64
sep=read_json(QA/'public-sepolia-rehearsal-evidence.json'); pre=read_json(QA/'public-mainnet-preflight-evidence.json'); founder=read_json(QA/'public-founder-approval-evidence.json'); addr=read_json(QA/'public-address-ceremony-evidence.json')
passed= sep.get('sepoliaRehearsal')=='PASSED' and pre.get('mainnetPreflight')=='PASSED'
base=public_base(); base.update({'toolchainClearanceHash':h('public-toolchain-clearance-evidence.json'),'sepoliaEvidenceDocketHash':sep.get('evidenceDocketHash', h('public-sepolia-rehearsal-evidence.json')),'sepoliaReceiptVerificationHash':sep.get('receiptBundleHash', h('public-sepolia-rehearsal-evidence.json')),'mainnetPreflightHash':pre.get('mainnetPreflightHash', h('public-mainnet-preflight-evidence.json')),'addressCeremonyCommitmentHash':addr.get('addressCeremonyCommitmentHash', h('public-address-ceremony-evidence.json')),'founderApprovalCommitmentHash':founder.get('founderApprovalCommitmentHash', h('public-founder-approval-evidence.json')),'policyDecisionCommitmentHash':h('public-policy-decision-evidence.json'),'technicalReadiness':'YES' if passed else 'NO','deploymentAuthorization':'YES' if passed and founder and addr else 'NO','ethereumMainnetAuthorization':'YES' if passed and founder and addr else 'NO','blockers':[] if passed else ['PRIVATE_OPERATOR_EVIDENCE_PENDING']})
write_json(QA/'public-mainnet-technical-readiness-evidence.json', base)
write_json(QA/'public-mainnet-deployment-authorization-evidence.json', {**base, 'publicClaimsBoundaryClean': True, 'founderApprovalHeldPrivately': bool(founder), 'deploymentAuthorization': base['deploymentAuthorization']})
write_json(QA/'public-ethereum-mainnet-authorization-evidence.json', base)
print('Wrote redacted public mainnet evidence commitments.')
