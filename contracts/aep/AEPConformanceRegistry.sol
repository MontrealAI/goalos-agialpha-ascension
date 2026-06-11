// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPConformanceRegistry is GoalOSAccessControl {
    enum ConformanceLevel { L0_SCHEMA_VALID, L1_PROOF_EMITTING, L2_EVAL_GATED, L3_ROLLBACKABLE, L4_ATTESTABLE, L5_PRODUCTION_GOVERNED, L6_CROSS_INSTITUTIONAL }
    struct ConformanceRecord {
        bytes32 systemHash;
        ConformanceLevel level;
        bytes32 evidenceDocketHash;
        bytes32 auditorHash;
        bytes32 claimBoundaryHash;
        string metadataURI;
        address signer;
        uint256 createdAt;
        bool active;
    }

    uint256 public nextRecordId = 1;
    mapping(uint256 => ConformanceRecord) public records;

    event ConformanceRecorded(uint256 indexed recordId, bytes32 indexed systemHash, ConformanceLevel level, bytes32 evidenceDocketHash, bytes32 auditorHash, string metadataURI);
    event ConformanceStatusUpdated(uint256 indexed recordId, bool active, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function recordConformance(
        bytes32 systemHash,
        ConformanceLevel level,
        bytes32 evidenceDocketHash,
        bytes32 auditorHash,
        bytes32 claimBoundaryHash,
        string calldata metadataURI
    ) external onlyOperator returns (uint256 recordId) {
        require(systemHash != bytes32(0), "AEP_CONF_ZERO_SYSTEM");
        require(evidenceDocketHash != bytes32(0), "AEP_CONF_ZERO_DOCKET");
        recordId = nextRecordId++;
        records[recordId] = ConformanceRecord(systemHash, level, evidenceDocketHash, auditorHash, claimBoundaryHash, metadataURI, msg.sender, block.timestamp, true);
        emit ConformanceRecorded(recordId, systemHash, level, evidenceDocketHash, auditorHash, metadataURI);
    }

    function setConformanceActive(uint256 recordId, bool active, bytes32 reasonHash) external onlyOperator {
        require(records[recordId].createdAt != 0, "AEP_CONF_NOT_FOUND");
        records[recordId].active = active;
        emit ConformanceStatusUpdated(recordId, active, reasonHash);
    }
}
