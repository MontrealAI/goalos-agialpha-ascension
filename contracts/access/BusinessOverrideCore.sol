// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./GoalOSAccessControl.sol";
import "../interfaces/IBusinessOverride.sol";

abstract contract BusinessOverrideCore is GoalOSAccessControl, IBusinessOverride {
    error GoalOSOverrideMissingCommitment();
    error GoalOSOverrideReplay(bytes32 overrideId);

    uint256 public businessOverrideNonce;
    mapping(bytes32 => bool) public businessOverrideUsed;

    constructor(address admin) GoalOSAccessControl(admin) {}

    modifier validOverrideCommitments(bytes32 reasonHash, bytes32 evidenceHash) {
        if (reasonHash == bytes32(0) || evidenceHash == bytes32(0)) revert GoalOSOverrideMissingCommitment();
        _;
    }

    function _executeBusinessOverride(
        bytes32 action,
        bytes32 subjectId,
        bytes32 previousStateHash,
        bytes32 newStateHash,
        bytes32 reasonHash,
        bytes32 evidenceHash
    ) internal onlyOwner validOverrideCommitments(reasonHash, evidenceHash) returns (bytes32 overrideId) {
        uint256 nonce = ++businessOverrideNonce;
        overrideId = keccak256(abi.encode(block.chainid, address(this), action, subjectId, msg.sender, nonce));
        if (businessOverrideUsed[overrideId]) revert GoalOSOverrideReplay(overrideId);
        businessOverrideUsed[overrideId] = true;
        emit BusinessOverrideExecuted(overrideId, action, subjectId, msg.sender, previousStateHash, newStateHash, reasonHash, evidenceHash, nonce, block.timestamp);
    }
}
