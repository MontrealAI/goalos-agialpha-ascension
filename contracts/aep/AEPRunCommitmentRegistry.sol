// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPRunCommitmentRegistry is GoalOSAccessControl {
    enum RunStatus { None, Committed, Executed, Cancelled }
    struct RunCommitment {
        uint256 goalOSCommitId;
        bytes32 runCommitmentHash;
        bytes32 planGraphHash;
        bytes32 artifactVersionRoot;
        bytes32 toolPermissionRoot;
        bytes32 contextRoot;
        bytes32 policyRoot;
        bytes32 runtimeEnvironmentHash;
        uint256 budgetLimit;
        uint256 latencyLimit;
        RunStatus status;
        string metadataURI;
        address signer;
        uint256 createdAt;
    }

    uint256 public nextRunId = 1;
    mapping(uint256 => RunCommitment) public runs;
    event RunCommitted(uint256 indexed runId, uint256 indexed goalOSCommitId, bytes32 indexed runCommitmentHash, string metadataURI);
    event RunStatusUpdated(uint256 indexed runId, RunStatus status, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function commitRun(uint256 goalOSCommitId, bytes32 runCommitmentHash, bytes32 planGraphHash, bytes32 artifactVersionRoot, bytes32 toolPermissionRoot, bytes32 contextRoot, bytes32 policyRoot, bytes32 runtimeEnvironmentHash, uint256 budgetLimit, uint256 latencyLimit, string calldata metadataURI) external onlyOperator returns (uint256 runId) {
        require(goalOSCommitId != 0, "AEP_RUN_ZERO_COMMIT");
        require(runCommitmentHash != bytes32(0), "AEP_RUN_ZERO_HASH");
        runId = nextRunId++;
        runs[runId] = RunCommitment(goalOSCommitId, runCommitmentHash, planGraphHash, artifactVersionRoot, toolPermissionRoot, contextRoot, policyRoot, runtimeEnvironmentHash, budgetLimit, latencyLimit, RunStatus.Committed, metadataURI, msg.sender, block.timestamp);
        emit RunCommitted(runId, goalOSCommitId, runCommitmentHash, metadataURI);
    }

    function setRunStatus(uint256 runId, RunStatus status, bytes32 reasonHash) external onlyOperator {
        require(runs[runId].createdAt != 0, "AEP_RUN_NOT_FOUND");
        runs[runId].status = status;
        emit RunStatusUpdated(runId, status, reasonHash);
    }
}
