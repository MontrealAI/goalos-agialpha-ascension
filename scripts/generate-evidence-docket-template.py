from __future__ import annotations
import json, datetime, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "SEPOLIA_EVIDENCE_DOCKET_TEMPLATE_v4_2.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def now():
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')

docket = {
    "schema": "goalos.agialpha.ascension.evidence_docket.v4.2",
    "package": "GoalOS_AGIALPHA_Ascension_Ethereum_Mainnet_Implementation_v4_2_EVIDENCE_READY_AUDIT_CANDIDATE",
    "generatedAtUtc": now(),
    "network": "ethereum-sepolia",
    "status": "draft",
    "rootDoctrine": "GoalOS sets aim; AGIALPHA coordinates proof work; AEP-001 defines evidence; Proof Gradient decides what may evolve.",
    "publicBoundary": "Evidence docket only. Not externally audited. Ethereum Mainnet not authorized. Not legal, tax, investment, or security approval.",
    "contracts": {
        "AGIALPHA_or_MockAGIALPHA": "TO_FILL",
        "JobRegistry": "TO_FILL",
        "JobClaimBondManager": "TO_FILL",
        "ProofSubmissionRegistry": "TO_FILL",
        "ReviewerBondRegistry": "TO_FILL",
        "ProofCardRegistry": "TO_FILL",
        "ProofCredentialRegistry": "TO_FILL",
        "ReputationRegistry": "TO_FILL",
        "AEPSelectionGate": "TO_FILL",
        "AEPEvidenceDocketRegistry": "TO_FILL"
    },
    "transactions": {
        "deployment": [],
        "sponsorPostsMission": "TO_FILL",
        "builderClaimsMission": "TO_FILL",
        "builderSubmitsProof": "TO_FILL",
        "reviewerBonds": "TO_FILL",
        "reviewerApproves": "TO_FILL",
        "proofCardRegistered": "TO_FILL",
        "credentialIssued": "TO_FILL",
        "reputationUpdated": "TO_FILL",
        "rewardAndBondsSettled": "TO_FILL"
    },
    "gateEvidence": {
        "compileLogSha256": "TO_FILL",
        "testLogSha256": "TO_FILL",
        "staticQaReportSha256": "TO_FILL",
        "deploymentJsonSha256": "TO_FILL",
        "automatedSecurityToolchainSha256": "PENDING",
        "internalSecurityReviewSha256": "PENDING",
        "legalMemoSha256": "PENDING",
        "taxMemoSha256": "PENDING",
        "claimsReviewSha256": "PENDING",
        "governanceRoleCeremonySha256": "PENDING",
        "founderApprovalSha256": "PENDING"
    },
    "proofLoop": [
        "Sponsor posts proof mission",
        "Builder claims mission",
        "Builder submits proof",
        "Reviewer validates proof",
        "Proof Card registers",
        "Credential issues",
        "Reputation updates",
        "Rewards and bonds settle"
    ],
    "mainnetDecision": "NOT_AUTHORIZED",
    "notes": [
        "Fill this after real Ethereum Sepolia execution.",
        "Do not copy private workflow evidence into this public docket.",
        "Use hashes/URIs for public-safe proof anchors."
    ]
}
text=json.dumps(docket, indent=2, sort_keys=True)+"\n"
OUT.write_text(text, encoding="utf-8")
print(json.dumps({"status":"EVIDENCE_DOCKET_TEMPLATE_WRITTEN","path":str(OUT.relative_to(ROOT)),"sha256":hashlib.sha256(text.encode()).hexdigest()}, indent=2))
