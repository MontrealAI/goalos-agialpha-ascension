// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract SponsorRegistry is GoalOSAccessControl {
    struct SponsorProfile { string metadataURI; bytes32 metadataHash; bool active; uint256 createdAt; }
    mapping(address => SponsorProfile) public sponsors;
    event SponsorRegistered(address indexed sponsor, string metadataURI, bytes32 indexed metadataHash);
    event SponsorStatusUpdated(address indexed sponsor, bool active);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function registerSponsor(string calldata metadataURI, bytes32 metadataHash) external {
        sponsors[msg.sender] = SponsorProfile(metadataURI, metadataHash, true, block.timestamp);
        emit SponsorRegistered(msg.sender, metadataURI, metadataHash);
    }
    function setSponsorStatus(address sponsor, bool active) external onlyOperator {
        sponsors[sponsor].active = active;
        emit SponsorStatusUpdated(sponsor, active);
    }
}
