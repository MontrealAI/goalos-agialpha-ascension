// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IProofSubmissionRegistry {
    function builderOf(uint256 submissionId) external view returns (address);

    function approveSubmission(
        uint256 submissionId,
        address reviewer,
        bytes32 rationaleHash,
        string calldata credentialURI,
        bytes32 credentialType
    ) external;

    function rejectSubmission(
        uint256 submissionId,
        address reviewer,
        bytes32 reasonHash,
        bool slashBuilder
    ) external;
}
