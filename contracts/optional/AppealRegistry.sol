// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AppealRegistry is GoalOSAccessControl {
    enum AppealStatus { None, Open, Accepted, Rejected }

    struct Appeal {
        uint256 disputeId;
        address appellant;
        bytes32 appealHash;
        AppealStatus status;
        uint256 createdAt;
        bytes32 decisionHash;
    }

    uint256 public nextAppealId = 1;
    mapping(uint256 => Appeal) public appeals;

    event AppealOpened(uint256 indexed appealId, uint256 indexed disputeId, address indexed appellant, bytes32 appealHash);
    event AppealDecided(uint256 indexed appealId, AppealStatus status, bytes32 decisionHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function openAppeal(uint256 disputeId, bytes32 appealHash) external returns (uint256 appealId) {
        require(appealHash != bytes32(0), "APPEAL_ZERO_HASH");
        appealId = nextAppealId++;
        appeals[appealId] = Appeal(disputeId, msg.sender, appealHash, AppealStatus.Open, block.timestamp, bytes32(0));
        emit AppealOpened(appealId, disputeId, msg.sender, appealHash);
    }

    function decideAppeal(uint256 appealId, bool accepted, bytes32 decisionHash) external onlyOperator {
        Appeal storage appeal = appeals[appealId];
        require(appeal.status == AppealStatus.Open, "APPEAL_NOT_OPEN");
        appeal.status = accepted ? AppealStatus.Accepted : AppealStatus.Rejected;
        appeal.decisionHash = decisionHash;
        emit AppealDecided(appealId, appeal.status, decisionHash);
    }
}
