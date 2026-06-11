// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPEvidenceDocketRegistry is GoalOSAccessControl {
    struct EvidenceDocket { bytes32 docketHash; bytes32 claimsMatrixHash; bytes32 publicBoundaryHash; bytes32 privateAppendixHash; bytes32 costLedgerHash; bytes32 riskLedgerHash; string publicURI; address creator; uint256 createdAt; bool active; }
    uint256 public nextDocketId = 1;
    mapping(uint256 => EvidenceDocket) public dockets;
    event EvidenceDocketRegistered(uint256 indexed docketId, bytes32 indexed docketHash, string publicURI, bytes32 claimsMatrixHash);
    event EvidenceDocketStatusUpdated(uint256 indexed docketId, bool active, bytes32 indexed reasonHash);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function registerEvidenceDocket(bytes32 docketHash, bytes32 claimsMatrixHash, bytes32 publicBoundaryHash, bytes32 privateAppendixHash, bytes32 costLedgerHash, bytes32 riskLedgerHash, string calldata publicURI) external onlyOperator returns (uint256 docketId) {
        require(docketHash != bytes32(0), "AEP_DOCKET_ZERO_HASH");
        docketId = nextDocketId++;
        dockets[docketId] = EvidenceDocket(docketHash, claimsMatrixHash, publicBoundaryHash, privateAppendixHash, costLedgerHash, riskLedgerHash, publicURI, msg.sender, block.timestamp, true);
        emit EvidenceDocketRegistered(docketId, docketHash, publicURI, claimsMatrixHash);
    }
    function setDocketActive(uint256 docketId, bool active, bytes32 reasonHash) external onlyOperator {
        require(dockets[docketId].createdAt != 0, "AEP_DOCKET_NOT_FOUND");
        dockets[docketId].active = active;
        emit EvidenceDocketStatusUpdated(docketId, active, reasonHash);
    }
}
