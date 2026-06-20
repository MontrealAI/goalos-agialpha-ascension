// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/BusinessOverrideCore.sol";

contract GoalOSDeploymentDirectory is BusinessOverrideCore {
    enum ReleaseStatus { Draft, Active, Superseded, RolledBack, Shutdown }
    struct ReleaseRecord { bytes32 releaseId; bytes32 bytecodeRoot; bytes32 configurationRoot; bytes32 authorityRoot; bytes32 accountingRoot; bytes32 lifecycleRoot; bytes32 canaryRoot; address predecessor; address successor; ReleaseStatus status; uint256 recordedAt; }
    mapping(bytes32 => ReleaseRecord) public releases;
    event ReleaseRecorded(bytes32 indexed releaseId, ReleaseStatus indexed status, address predecessor, address successor);
    constructor(address admin) BusinessOverrideCore(admin) {}
    function recordRelease(ReleaseRecord calldata record, bytes32 reasonHash, bytes32 evidenceHash) external onlyOwner validOverrideCommitments(reasonHash, evidenceHash) {
        require(record.releaseId != bytes32(0), "DIRECTORY_ZERO_RELEASE");
        require(releases[record.releaseId].recordedAt == 0, "DIRECTORY_EXISTS");
        ReleaseRecord memory stored = record; stored.recordedAt = block.timestamp; releases[record.releaseId] = stored;
        emit ReleaseRecorded(record.releaseId, record.status, record.predecessor, record.successor);
        _executeBusinessOverride(keccak256("GOALOS_DIRECTORY_RECORD_RELEASE"), record.releaseId, bytes32(0), keccak256(abi.encode(stored)), reasonHash, evidenceHash);
    }
}
