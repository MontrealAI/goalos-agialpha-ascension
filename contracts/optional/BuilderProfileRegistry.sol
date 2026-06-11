// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract BuilderProfileRegistry is GoalOSAccessControl {
    struct BuilderProfile { string metadataURI; bytes32 metadataHash; bool active; uint256 createdAt; }
    mapping(address => BuilderProfile) public builders;
    event BuilderRegistered(address indexed builder, string metadataURI, bytes32 indexed metadataHash);
    event BuilderStatusUpdated(address indexed builder, bool active);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function registerBuilder(string calldata metadataURI, bytes32 metadataHash) external {
        builders[msg.sender] = BuilderProfile(metadataURI, metadataHash, true, block.timestamp);
        emit BuilderRegistered(msg.sender, metadataURI, metadataHash);
    }
    function setBuilderStatus(address builder, bool active) external onlyOperator {
        builders[builder].active = active;
        emit BuilderStatusUpdated(builder, active);
    }
}
