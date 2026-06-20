// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IGoalOSBusinessLifecycle {
    enum BusinessMode { Active, Paused, WindDown, Migrating, Shutdown }
    enum SelectorClass { NEW_OBLIGATION, NORMAL_OPERATION, SETTLEMENT_EXIT, OWNER_RECOVERY, CONFIGURATION, MIGRATION, LIFECYCLE_CONTROL }
    function mode() external view returns (BusinessMode);
    function canCall(bytes4 selector, address caller) external view returns (bool);
}
