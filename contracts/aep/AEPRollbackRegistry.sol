// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPRollbackRegistry is GoalOSAccessControl {
    struct RollbackReceipt { uint256 selectionId; uint256 rolloutId; bytes32 rollbackTargetHash; bytes32 triggerHash; bytes32 incidentRoot; string metadataURI; address signer; uint256 createdAt; }
    uint256 public nextRollbackId = 1;
    mapping(uint256 => RollbackReceipt) public rollbacks;
    event RollbackRecorded(uint256 indexed rollbackId, uint256 indexed selectionId, uint256 indexed rolloutId, bytes32 rollbackTargetHash, bytes32 incidentRoot);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function recordRollback(uint256 selectionId, uint256 rolloutId, bytes32 rollbackTargetHash, bytes32 triggerHash, bytes32 incidentRoot, string calldata metadataURI) external onlyOperator returns (uint256 rollbackId) {
        require(selectionId != 0, "AEP_RB_ZERO_SELECTION");
        require(rollbackTargetHash != bytes32(0), "AEP_RB_ZERO_TARGET");
        rollbackId = nextRollbackId++;
        rollbacks[rollbackId] = RollbackReceipt(selectionId, rolloutId, rollbackTargetHash, triggerHash, incidentRoot, metadataURI, msg.sender, block.timestamp);
        emit RollbackRecorded(rollbackId, selectionId, rolloutId, rollbackTargetHash, incidentRoot);
    }
}
