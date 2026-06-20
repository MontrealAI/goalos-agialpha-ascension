// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/BusinessOverrideCore.sol";
import "../interfaces/IGoalOSBusinessLifecycle.sol";

contract GoalOSBusinessLifecycle is BusinessOverrideCore, IGoalOSBusinessLifecycle {
    error GoalOSLifecycleBadTransition(BusinessMode from, BusinessMode to);
    error GoalOSLifecycleShutdownLiabilities(bytes32 accountingRoot);

    BusinessMode public override mode = BusinessMode.Active;
    bytes32 public latestAccountingRoot;
    mapping(bytes4 => SelectorClass) public selectorClass;

    event BusinessModeTransitioned(BusinessMode indexed previousMode, BusinessMode indexed newMode, bytes32 reasonHash, bytes32 evidenceHash);
    event SelectorClassified(bytes4 indexed selector, SelectorClass indexed class_);
    event AccountingRootUpdated(bytes32 indexed accountingRoot);

    constructor(address admin) BusinessOverrideCore(admin) {}

    function classifySelector(bytes4 selector, SelectorClass class_) external onlyOwner {
        selectorClass[selector] = class_;
        emit SelectorClassified(selector, class_);
    }

    function transitionTo(BusinessMode newMode, bytes32 reasonHash, bytes32 evidenceHash, bytes32 accountingRoot, bool liabilitiesResolved) external onlyOwner validOverrideCommitments(reasonHash, evidenceHash) {
        BusinessMode previous = mode;
        if (!_validTransition(previous, newMode)) revert GoalOSLifecycleBadTransition(previous, newMode);
        if (newMode == BusinessMode.Shutdown && !liabilitiesResolved) revert GoalOSLifecycleShutdownLiabilities(accountingRoot);
        mode = newMode;
        latestAccountingRoot = accountingRoot;
        emit AccountingRootUpdated(accountingRoot);
        emit BusinessModeTransitioned(previous, newMode, reasonHash, evidenceHash);
        _executeBusinessOverride(keccak256("GOALOS_LIFECYCLE_TRANSITION"), bytes32(uint256(uint8(newMode))), bytes32(uint256(uint8(previous))), bytes32(uint256(uint8(newMode))), reasonHash, evidenceHash);
    }

    function canCall(bytes4 selector, address caller) external view override returns (bool) {
        caller;
        SelectorClass class_ = selectorClass[selector];
        if (mode == BusinessMode.Active) return true;
        if (mode == BusinessMode.Paused) return class_ == SelectorClass.SETTLEMENT_EXIT || class_ == SelectorClass.OWNER_RECOVERY || class_ == SelectorClass.CONFIGURATION || class_ == SelectorClass.LIFECYCLE_CONTROL;
        if (mode == BusinessMode.WindDown) return class_ == SelectorClass.SETTLEMENT_EXIT || class_ == SelectorClass.OWNER_RECOVERY || class_ == SelectorClass.MIGRATION || class_ == SelectorClass.LIFECYCLE_CONTROL;
        if (mode == BusinessMode.Migrating) return class_ == SelectorClass.SETTLEMENT_EXIT || class_ == SelectorClass.OWNER_RECOVERY || class_ == SelectorClass.MIGRATION || class_ == SelectorClass.LIFECYCLE_CONTROL;
        return class_ == SelectorClass.LIFECYCLE_CONTROL;
    }

    function _validTransition(BusinessMode from, BusinessMode to) internal pure returns (bool) {
        if (from == to || from == BusinessMode.Shutdown) return false;
        if (from == BusinessMode.Active) return to == BusinessMode.Paused || to == BusinessMode.WindDown || to == BusinessMode.Migrating;
        if (from == BusinessMode.Paused) return to == BusinessMode.Active || to == BusinessMode.WindDown || to == BusinessMode.Migrating;
        if (from == BusinessMode.WindDown) return to == BusinessMode.Migrating || to == BusinessMode.Shutdown;
        if (from == BusinessMode.Migrating) return to == BusinessMode.Active || to == BusinessMode.WindDown || to == BusinessMode.Shutdown;
        return false;
    }
}
