// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract ProofCardRegistry is GoalOSAccessControl {
    struct ProofCard {
        uint256 jobId;
        uint256 submissionId;
        address builder;
        address reviewer;
        bytes32 proofHash;
        bytes32 proofCardHash;
        string metadataURI;
        bool revoked;
        uint256 createdAt;
    }

    uint256 public nextProofCardId = 1;
    mapping(uint256 => ProofCard) public proofCards;

    event ProofCardRegistered(
        uint256 indexed proofCardId,
        uint256 indexed jobId,
        uint256 indexed submissionId,
        address builder,
        address reviewer,
        bytes32 proofCardHash,
        string metadataURI
    );
    event ProofCardRevoked(uint256 indexed proofCardId, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function registerProofCard(
        uint256 jobId,
        uint256 submissionId,
        address builder,
        address reviewer,
        bytes32 proofHash,
        bytes32 proofCardHash,
        string calldata metadataURI
    ) external onlyOperator returns (uint256 proofCardId) {
        require(builder != address(0), "PC_ZERO_BUILDER");
        require(reviewer != address(0), "PC_ZERO_REVIEWER");
        require(proofCardHash != bytes32(0), "PC_ZERO_HASH");

        proofCardId = nextProofCardId++;
        proofCards[proofCardId] = ProofCard(
            jobId,
            submissionId,
            builder,
            reviewer,
            proofHash,
            proofCardHash,
            metadataURI,
            false,
            block.timestamp
        );

        emit ProofCardRegistered(proofCardId, jobId, submissionId, builder, reviewer, proofCardHash, metadataURI);
    }

    function revokeProofCard(uint256 proofCardId, bytes32 reasonHash) external onlyOperator {
        require(proofCards[proofCardId].createdAt != 0, "PC_NOT_FOUND");
        proofCards[proofCardId].revoked = true;
        emit ProofCardRevoked(proofCardId, reasonHash);
    }
}
