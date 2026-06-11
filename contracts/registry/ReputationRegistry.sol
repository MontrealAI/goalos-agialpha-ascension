// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract ReputationRegistry is GoalOSAccessControl {
    struct Reputation {
        uint256 score;
        uint256 approvedProofs;
        uint256 rejectedProofs;
        uint256 credentials;
        uint256 reviewerApprovals;
        uint256 reviewerRejections;
        uint256 disputes;
    }

    mapping(address => Reputation) private _reputationOf;

    event ReputationUpdated(address indexed account, uint256 score, bytes32 indexed reasonHash);
    event ApprovedProofRecorded(address indexed builder, address indexed reviewer, uint256 indexed proofCardId);
    event RejectedProofRecorded(address indexed builder, address indexed reviewer, bytes32 indexed reasonHash);
    event CredentialRecorded(address indexed account, uint256 indexed tokenId);
    event DisputeRecorded(address indexed account, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function reputationOf(address account) external view returns (Reputation memory) {
        return _reputationOf[account];
    }

    function scoreOf(address account) external view returns (uint256) {
        return _reputationOf[account].score;
    }

    function recordApprovedProof(address builder, address reviewer, uint256 proofCardId) external onlyOperator {
        Reputation storage b = _reputationOf[builder];
        b.approvedProofs += 1;
        b.score += 10;

        Reputation storage r = _reputationOf[reviewer];
        r.reviewerApprovals += 1;
        r.score += 2;

        emit ApprovedProofRecorded(builder, reviewer, proofCardId);
        emit ReputationUpdated(builder, b.score, keccak256("APPROVED_PROOF"));
        emit ReputationUpdated(reviewer, r.score, keccak256("REVIEW_APPROVED"));
    }

    function recordRejectedProof(address builder, address reviewer, bytes32 reasonHash) external onlyOperator {
        Reputation storage b = _reputationOf[builder];
        b.rejectedProofs += 1;
        if (b.score > 0) {
            b.score -= 1;
        }

        Reputation storage r = _reputationOf[reviewer];
        r.reviewerRejections += 1;
        r.score += 1;

        emit RejectedProofRecorded(builder, reviewer, reasonHash);
        emit ReputationUpdated(builder, b.score, reasonHash);
        emit ReputationUpdated(reviewer, r.score, keccak256("REVIEW_REJECTED"));
    }

    function recordCredential(address account, uint256 tokenId) external onlyOperator {
        Reputation storage rep = _reputationOf[account];
        rep.credentials += 1;
        rep.score += 5;
        emit CredentialRecorded(account, tokenId);
        emit ReputationUpdated(account, rep.score, keccak256("CREDENTIAL"));
    }

    function recordDispute(address account, bytes32 reasonHash) external onlyOperator {
        Reputation storage rep = _reputationOf[account];
        rep.disputes += 1;
        if (rep.score > 1) {
            rep.score -= 2;
        } else {
            rep.score = 0;
        }
        emit DisputeRecorded(account, reasonHash);
        emit ReputationUpdated(account, rep.score, reasonHash);
    }

    function adjustScore(address account, int256 delta, bytes32 reasonHash) external onlyOperator {
        Reputation storage rep = _reputationOf[account];
        if (delta >= 0) {
            rep.score += uint256(delta);
        } else {
            uint256 reduction = uint256(-delta);
            rep.score = reduction > rep.score ? 0 : rep.score - reduction;
        }
        emit ReputationUpdated(account, rep.score, reasonHash);
    }
}
