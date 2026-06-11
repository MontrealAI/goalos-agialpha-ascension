// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPRolloutRouter is GoalOSAccessControl {
    struct RolloutReceipt { uint256 selectionId; uint16 percentageBps; bytes32 tenantScopeHash; bytes32 monitoringRoot; bytes32 safetyThresholdHash; string metadataURI; address signer; uint256 createdAt; bool active; }
    uint256 public nextRolloutId = 1;
    mapping(uint256 => RolloutReceipt) public rollouts;
    event RolloutRecorded(uint256 indexed rolloutId, uint256 indexed selectionId, uint16 percentageBps, bytes32 tenantScopeHash, bytes32 monitoringRoot);
    event RolloutStatusUpdated(uint256 indexed rolloutId, bool active, bytes32 indexed reasonHash);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function recordRollout(uint256 selectionId, uint16 percentageBps, bytes32 tenantScopeHash, bytes32 monitoringRoot, bytes32 safetyThresholdHash, string calldata metadataURI) external onlyOperator returns (uint256 rolloutId) {
        require(selectionId != 0, "AEP_ROLLOUT_ZERO_SELECTION");
        require(percentageBps <= 10000, "AEP_ROLLOUT_BAD_PERCENT");
        rolloutId = nextRolloutId++;
        rollouts[rolloutId] = RolloutReceipt(selectionId, percentageBps, tenantScopeHash, monitoringRoot, safetyThresholdHash, metadataURI, msg.sender, block.timestamp, true);
        emit RolloutRecorded(rolloutId, selectionId, percentageBps, tenantScopeHash, monitoringRoot);
    }
    function setRolloutActive(uint256 rolloutId, bool active, bytes32 reasonHash) external onlyOperator {
        require(rollouts[rolloutId].createdAt != 0, "AEP_ROLLOUT_NOT_FOUND");
        rollouts[rolloutId].active = active;
        emit RolloutStatusUpdated(rolloutId, active, reasonHash);
    }
}
