// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";
import "../interfaces/IReputationRegistry.sol";

contract DisputeRegistry is GoalOSAccessControl {
    enum DisputeStatus { None, Open, Resolved, Rejected }

    struct Dispute {
        uint256 jobId;
        uint256 submissionId;
        address openedBy;
        bytes32 reasonHash;
        DisputeStatus status;
        uint256 createdAt;
        bytes32 resolutionHash;
    }

    IReputationRegistry public reputationRegistry;
    uint256 public nextDisputeId = 1;
    mapping(uint256 => Dispute) public disputes;

    event DisputeOpened(uint256 indexed disputeId, uint256 indexed jobId, uint256 indexed submissionId, address openedBy, bytes32 reasonHash);
    event DisputeResolved(uint256 indexed disputeId, DisputeStatus status, bytes32 resolutionHash);

    constructor(address admin, address reputationRegistry_) GoalOSAccessControl(admin) {
        reputationRegistry = IReputationRegistry(reputationRegistry_);
    }

    function openDispute(uint256 jobId, uint256 submissionId, bytes32 reasonHash) external returns (uint256 disputeId) {
        require(reasonHash != bytes32(0), "DISPUTE_ZERO_REASON");
        disputeId = nextDisputeId++;
        disputes[disputeId] = Dispute(jobId, submissionId, msg.sender, reasonHash, DisputeStatus.Open, block.timestamp, bytes32(0));
        emit DisputeOpened(disputeId, jobId, submissionId, msg.sender, reasonHash);
    }

    function resolveDispute(uint256 disputeId, bool accepted, bytes32 resolutionHash) external onlyOperator {
        Dispute storage dispute = disputes[disputeId];
        require(dispute.status == DisputeStatus.Open, "DISPUTE_NOT_OPEN");
        dispute.status = accepted ? DisputeStatus.Resolved : DisputeStatus.Rejected;
        dispute.resolutionHash = resolutionHash;
        if (!accepted && address(reputationRegistry) != address(0)) {
            // Optional reputation effect can be routed through an operator in future versions.
        }
        emit DisputeResolved(disputeId, dispute.status, resolutionHash);
    }
}
