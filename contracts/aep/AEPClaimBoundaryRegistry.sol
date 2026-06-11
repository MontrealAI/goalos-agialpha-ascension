// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPClaimBoundaryRegistry is GoalOSAccessControl {
    struct ClaimBoundary {
        bytes32 claimHash;
        bytes32 notClaimedHash;
        bytes32 requiredEvidenceHash;
        bytes32 legalReviewHash;
        bytes32 publicCopyHash;
        string metadataURI;
        address signer;
        uint256 createdAt;
        bool active;
    }

    uint256 public nextBoundaryId = 1;
    mapping(uint256 => ClaimBoundary) public boundaries;

    event ClaimBoundaryRegistered(uint256 indexed boundaryId, bytes32 indexed claimHash, bytes32 requiredEvidenceHash, string metadataURI);
    event ClaimBoundaryStatusUpdated(uint256 indexed boundaryId, bool active, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function registerClaimBoundary(
        bytes32 claimHash,
        bytes32 notClaimedHash,
        bytes32 requiredEvidenceHash,
        bytes32 legalReviewHash,
        bytes32 publicCopyHash,
        string calldata metadataURI
    ) external onlyOperator returns (uint256 boundaryId) {
        require(claimHash != bytes32(0), "AEP_CLAIM_ZERO_CLAIM");
        require(requiredEvidenceHash != bytes32(0), "AEP_CLAIM_ZERO_EVIDENCE");
        boundaryId = nextBoundaryId++;
        boundaries[boundaryId] = ClaimBoundary(claimHash, notClaimedHash, requiredEvidenceHash, legalReviewHash, publicCopyHash, metadataURI, msg.sender, block.timestamp, true);
        emit ClaimBoundaryRegistered(boundaryId, claimHash, requiredEvidenceHash, metadataURI);
    }

    function setClaimBoundaryActive(uint256 boundaryId, bool active, bytes32 reasonHash) external onlyOperator {
        require(boundaries[boundaryId].createdAt != 0, "AEP_CLAIM_NOT_FOUND");
        boundaries[boundaryId].active = active;
        emit ClaimBoundaryStatusUpdated(boundaryId, active, reasonHash);
    }
}
