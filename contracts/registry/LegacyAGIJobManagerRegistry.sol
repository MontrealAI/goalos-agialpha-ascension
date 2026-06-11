// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract LegacyAGIJobManagerRegistry is GoalOSAccessControl {
    struct LegacyProofRecord {
        uint256 legacyJobId;
        bytes32 legacyEventHash;
        bytes32 proofCardHash;
        string metadataURI;
        bool accepted;
        uint256 createdAt;
    }

    address public immutable legacyAGIJobManager;
    uint256 public nextRecordId = 1;

    mapping(uint256 => LegacyProofRecord) public records;

    event LegacyRecordAdded(
        uint256 indexed recordId,
        uint256 indexed legacyJobId,
        bytes32 indexed legacyEventHash,
        bytes32 proofCardHash,
        string metadataURI,
        bool accepted
    );
    event LegacyRecordUpdated(uint256 indexed recordId, bool accepted, bytes32 indexed reasonHash);

    constructor(address admin, address legacyAGIJobManager_) GoalOSAccessControl(admin) {
        require(legacyAGIJobManager_ != address(0), "LEGACY_ZERO_MANAGER");
        legacyAGIJobManager = legacyAGIJobManager_;
    }

    function addLegacyRecord(
        uint256 legacyJobId,
        bytes32 legacyEventHash,
        bytes32 proofCardHash,
        string calldata metadataURI,
        bool accepted
    ) external onlyOperator returns (uint256 recordId) {
        require(legacyEventHash != bytes32(0), "LEGACY_ZERO_EVENT");
        require(proofCardHash != bytes32(0), "LEGACY_ZERO_PROOF_CARD");

        recordId = nextRecordId++;
        records[recordId] = LegacyProofRecord(
            legacyJobId,
            legacyEventHash,
            proofCardHash,
            metadataURI,
            accepted,
            block.timestamp
        );

        emit LegacyRecordAdded(recordId, legacyJobId, legacyEventHash, proofCardHash, metadataURI, accepted);
    }

    function setLegacyRecordAccepted(uint256 recordId, bool accepted, bytes32 reasonHash) external onlyOperator {
        require(records[recordId].createdAt != 0, "LEGACY_NOT_FOUND");
        records[recordId].accepted = accepted;
        emit LegacyRecordUpdated(recordId, accepted, reasonHash);
    }
}
