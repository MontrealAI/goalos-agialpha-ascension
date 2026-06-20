// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IGoalOSAccounting {
    function actualBalance(address token) external view returns (uint256);
    function protectedLiability(address token) external view returns (uint256);
    function reservedBalance(address token) external view returns (uint256);
    function pendingWithdrawal(address token) external view returns (uint256);
    function freeBalance(address token) external view returns (uint256);
    function totalInflow(address token) external view returns (uint256);
    function totalOutflow(address token) external view returns (uint256);
    function isSolvent(address token) external view returns (bool);
    function accountingStateHash(address token) external view returns (bytes32);
}
