// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract ReferralRegistry is GoalOSAccessControl {
    mapping(address => address) public referrerOf;
    mapping(address => uint256) public referralCount;
    mapping(address => uint256) public conversionCount;

    event ReferralAssigned(address indexed user, address indexed referrer);
    event ReferralConversion(address indexed user, address indexed referrer, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function assignReferral(address referrer) external whenNotPaused {
        _assignReferral(msg.sender, referrer);
    }

    function assignReferralFor(address user, address referrer) external onlyOperator {
        _assignReferral(user, referrer);
    }

    function recordConversion(address user, bytes32 reasonHash) external onlyOperator {
        address referrer = referrerOf[user];
        if (referrer != address(0)) {
            conversionCount[referrer] += 1;
            emit ReferralConversion(user, referrer, reasonHash);
        }
    }

    function _assignReferral(address user, address referrer) internal {
        require(user != address(0), "REF_ZERO_USER");
        require(referrer != address(0), "REF_ZERO_REFERRER");
        require(referrer != user, "REF_SELF");
        require(referrerOf[user] == address(0), "REF_ALREADY_SET");
        referrerOf[user] = referrer;
        referralCount[referrer] += 1;
        emit ReferralAssigned(user, referrer);
    }
}
