// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IJobClaimBondManager {
    function releaseClaimBond(uint256 jobId) external;
    function slashClaimBond(uint256 jobId, bytes32 reasonHash) external;
}
