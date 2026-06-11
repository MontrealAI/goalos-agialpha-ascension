// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPFalsificationRegistry is GoalOSAccessControl {
    enum FalsificationStatus { None, Reported, Accepted, Rejected, Remediated }
    struct FalsificationRecord {
        bytes32 conditionHash;
        bytes32 evidenceHash;
        bytes32 affectedClaimHash;
        FalsificationStatus status;
        string metadataURI;
        address reporter;
        uint256 createdAt;
        uint256 updatedAt;
    }

    uint256 public nextFalsificationId = 1;
    mapping(uint256 => FalsificationRecord) public records;

    event FalsificationReported(uint256 indexed falsificationId, bytes32 indexed conditionHash, bytes32 evidenceHash, bytes32 affectedClaimHash, string metadataURI);
    event FalsificationStatusUpdated(uint256 indexed falsificationId, FalsificationStatus status, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function reportFalsification(bytes32 conditionHash, bytes32 evidenceHash, bytes32 affectedClaimHash, string calldata metadataURI) external returns (uint256 falsificationId) {
        require(conditionHash != bytes32(0), "FALS_ZERO_CONDITION");
        require(evidenceHash != bytes32(0), "FALS_ZERO_EVIDENCE");
        falsificationId = nextFalsificationId++;
        records[falsificationId] = FalsificationRecord(conditionHash, evidenceHash, affectedClaimHash, FalsificationStatus.Reported, metadataURI, msg.sender, block.timestamp, block.timestamp);
        emit FalsificationReported(falsificationId, conditionHash, evidenceHash, affectedClaimHash, metadataURI);
    }

    function setFalsificationStatus(uint256 falsificationId, FalsificationStatus status, bytes32 reasonHash) external onlyOperator {
        require(records[falsificationId].createdAt != 0, "FALS_NOT_FOUND");
        require(status != FalsificationStatus.None, "FALS_BAD_STATUS");
        records[falsificationId].status = status;
        records[falsificationId].updatedAt = block.timestamp;
        emit FalsificationStatusUpdated(falsificationId, status, reasonHash);
    }
}
