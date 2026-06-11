// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";
import "../registry/ProofCredentialRegistry.sol";

contract CredentialRevocationRegistry is GoalOSAccessControl {
    ProofCredentialRegistry public immutable credentialRegistry;

    struct RevocationRecord {
        uint256 tokenId;
        address requestedBy;
        bytes32 reasonHash;
        bool executed;
        uint256 createdAt;
    }

    uint256 public nextRevocationId = 1;
    mapping(uint256 => RevocationRecord) public revocations;

    event CredentialRevocationRequested(uint256 indexed revocationId, uint256 indexed tokenId, address indexed requestedBy, bytes32 reasonHash);
    event CredentialRevocationExecuted(uint256 indexed revocationId, uint256 indexed tokenId, bytes32 reasonHash);

    constructor(address admin, address credentialRegistry_) GoalOSAccessControl(admin) {
        require(credentialRegistry_ != address(0), "REVOKE_ZERO_CRED");
        credentialRegistry = ProofCredentialRegistry(credentialRegistry_);
    }

    function requestRevocation(uint256 tokenId, bytes32 reasonHash) external returns (uint256 revocationId) {
        require(reasonHash != bytes32(0), "REVOKE_ZERO_REASON");
        revocationId = nextRevocationId++;
        revocations[revocationId] = RevocationRecord(tokenId, msg.sender, reasonHash, false, block.timestamp);
        emit CredentialRevocationRequested(revocationId, tokenId, msg.sender, reasonHash);
    }

    function executeRevocation(uint256 revocationId) external onlyOperator {
        RevocationRecord storage record = revocations[revocationId];
        require(!record.executed, "REVOKE_DONE");
        record.executed = true;
        credentialRegistry.revokeCredential(record.tokenId, record.reasonHash);
        emit CredentialRevocationExecuted(revocationId, record.tokenId, record.reasonHash);
    }
}
