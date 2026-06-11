// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../access/GoalOSAccessControl.sol";
import "../interfaces/IReputationRegistry.sol";

contract PremiumAccessRegistry is GoalOSAccessControl {
    IERC20 public immutable agialphaToken;
    IReputationRegistry public immutable reputationRegistry;

    struct AccessTier {
        uint256 minReputation;
        uint256 minAGIALPHABalance;
        bool active;
    }

    mapping(bytes32 => AccessTier) public accessTiers;

    event AccessTierUpdated(bytes32 indexed tierId, uint256 minReputation, uint256 minAGIALPHABalance, bool active);

    constructor(address admin, address agialphaToken_, address reputationRegistry_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "ACCESS_ZERO_AGIALPHA");
        require(reputationRegistry_ != address(0), "ACCESS_ZERO_REP");
        agialphaToken = IERC20(agialphaToken_);
        reputationRegistry = IReputationRegistry(reputationRegistry_);
    }

    function setAccessTier(bytes32 tierId, uint256 minReputation, uint256 minAGIALPHABalance, bool active) external onlyOperator {
        accessTiers[tierId] = AccessTier(minReputation, minAGIALPHABalance, active);
        emit AccessTierUpdated(tierId, minReputation, minAGIALPHABalance, active);
    }

    function canAccess(address account, bytes32 tierId) external view returns (bool) {
        AccessTier memory tier = accessTiers[tierId];
        if (!tier.active) return false;
        if (agialphaToken.balanceOf(account) < tier.minAGIALPHABalance) return false;
        return reputationRegistry.scoreOf(account) >= tier.minReputation;
    }
}
