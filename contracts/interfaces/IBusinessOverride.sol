// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IBusinessOverride {
    event BusinessOverrideExecuted(
        bytes32 indexed overrideId,
        bytes32 indexed action,
        bytes32 indexed subjectId,
        address executor,
        bytes32 previousStateHash,
        bytes32 newStateHash,
        bytes32 reasonHash,
        bytes32 evidenceHash,
        uint256 nonce,
        uint256 timestamp
    );
}
