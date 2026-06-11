// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IReputationRegistry {
    function recordApprovedProof(address builder, address reviewer, uint256 proofCardId) external;
    function recordRejectedProof(address builder, address reviewer, bytes32 reasonHash) external;
    function recordCredential(address account, uint256 tokenId) external;
    function scoreOf(address account) external view returns (uint256);
}
