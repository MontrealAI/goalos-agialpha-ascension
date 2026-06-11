// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";

contract AEPRewardVault is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable agialphaToken;
    uint256 public nextRewardId = 1;

    struct RewardRecord {
        address recipient;
        uint256 amount;
        uint256 proofBundleId;
        uint256 alphaWorkUnits;
        bytes32 rewardHash;
        string metadataURI;
        address operator;
        uint256 createdAt;
    }

    mapping(uint256 => RewardRecord) public rewards;

    event RewardPaid(uint256 indexed rewardId, address indexed recipient, uint256 amount, uint256 indexed proofBundleId, uint256 alphaWorkUnits, bytes32 rewardHash, string metadataURI);
    event VaultFunded(address indexed from, uint256 amount);

    constructor(address admin, address agialphaToken_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "REWARD_ZERO_TOKEN");
        agialphaToken = IERC20(agialphaToken_);
    }

    function fund(uint256 amount) external nonReentrant {
        require(amount > 0, "REWARD_ZERO_AMOUNT");
        agialphaToken.safeTransferFrom(msg.sender, address(this), amount);
        emit VaultFunded(msg.sender, amount);
    }

    function payReward(address recipient, uint256 amount, uint256 proofBundleId, uint256 alphaWorkUnits, bytes32 rewardHash, string calldata metadataURI) external onlyOperator nonReentrant returns (uint256 rewardId) {
        require(recipient != address(0), "REWARD_ZERO_RECIPIENT");
        require(amount > 0, "REWARD_ZERO_AMOUNT");
        require(rewardHash != bytes32(0), "REWARD_ZERO_HASH");
        rewardId = nextRewardId++;
        rewards[rewardId] = RewardRecord(recipient, amount, proofBundleId, alphaWorkUnits, rewardHash, metadataURI, msg.sender, block.timestamp);
        agialphaToken.safeTransfer(recipient, amount);
        emit RewardPaid(rewardId, recipient, amount, proofBundleId, alphaWorkUnits, rewardHash, metadataURI);
    }
}
