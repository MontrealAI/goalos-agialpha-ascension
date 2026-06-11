// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";

contract AEPEvaluatorStakingRegistry is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    struct EvaluatorStake {
        uint256 amount;
        uint256 unlockAt;
        string metadataURI;
        bool active;
        uint256 createdAt;
        uint256 updatedAt;
    }

    IERC20 public immutable agialphaToken;
    address public treasury;
    uint256 public minEvaluatorStakeAGIALPHA = 100 ether;
    uint256 public unstakeDelay = 7 days;
    mapping(address => EvaluatorStake) public stakes;

    event EvaluatorStaked(address indexed evaluator, uint256 amount, string metadataURI);
    event UnstakeRequested(address indexed evaluator, uint256 unlockAt);
    event EvaluatorUnstaked(address indexed evaluator, uint256 amount);
    event EvaluatorSlashed(address indexed evaluator, uint256 amount, address indexed treasury, bytes32 reasonHash);
    event MinStakeUpdated(uint256 minEvaluatorStakeAGIALPHA);
    event UnstakeDelayUpdated(uint256 unstakeDelay);
    event TreasuryUpdated(address indexed treasury);

    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "EVAL_STAKE_ZERO_TOKEN");
        require(treasury_ != address(0), "EVAL_STAKE_ZERO_TREASURY");
        agialphaToken = IERC20(agialphaToken_);
        treasury = treasury_;
    }

    function setMinEvaluatorStake(uint256 minEvaluatorStakeAGIALPHA_) external onlyAdmin { minEvaluatorStakeAGIALPHA = minEvaluatorStakeAGIALPHA_; emit MinStakeUpdated(minEvaluatorStakeAGIALPHA_); }
    function setUnstakeDelay(uint256 unstakeDelay_) external onlyAdmin { require(unstakeDelay_ <= 30 days, "EVAL_STAKE_DELAY_TOO_LONG"); unstakeDelay = unstakeDelay_; emit UnstakeDelayUpdated(unstakeDelay_); }
    function setTreasury(address treasury_) external onlyAdmin { require(treasury_ != address(0), "EVAL_STAKE_ZERO_TREASURY"); treasury = treasury_; emit TreasuryUpdated(treasury_); }

    function stake(uint256 amount, string calldata metadataURI) external nonReentrant whenNotPaused {
        require(amount > 0, "EVAL_STAKE_ZERO_AMOUNT");
        EvaluatorStake storage s = stakes[msg.sender];
        agialphaToken.safeTransferFrom(msg.sender, address(this), amount);
        s.amount += amount;
        s.metadataURI = metadataURI;
        s.active = s.amount >= minEvaluatorStakeAGIALPHA;
        if (s.createdAt == 0) s.createdAt = block.timestamp;
        s.updatedAt = block.timestamp;
        s.unlockAt = 0;
        emit EvaluatorStaked(msg.sender, amount, metadataURI);
    }

    function requestUnstake() external nonReentrant {
        EvaluatorStake storage s = stakes[msg.sender];
        require(s.amount > 0, "EVAL_STAKE_NONE");
        s.unlockAt = block.timestamp + unstakeDelay;
        s.active = false;
        emit UnstakeRequested(msg.sender, s.unlockAt);
    }

    function unstake() external nonReentrant {
        EvaluatorStake storage s = stakes[msg.sender];
        require(s.amount > 0, "EVAL_STAKE_NONE");
        require(s.unlockAt != 0 && block.timestamp >= s.unlockAt, "EVAL_STAKE_LOCKED");
        uint256 amount = s.amount;
        s.amount = 0; s.unlockAt = 0; s.active = false; s.updatedAt = block.timestamp;
        agialphaToken.safeTransfer(msg.sender, amount);
        emit EvaluatorUnstaked(msg.sender, amount);
    }

    function slashEvaluator(address evaluator, uint256 amount, bytes32 reasonHash) external onlyOperator nonReentrant {
        EvaluatorStake storage s = stakes[evaluator];
        require(amount > 0, "EVAL_STAKE_ZERO_SLASH");
        require(s.amount >= amount, "EVAL_STAKE_SLASH_GT_AMOUNT");
        s.amount -= amount;
        s.active = s.amount >= minEvaluatorStakeAGIALPHA;
        s.updatedAt = block.timestamp;
        agialphaToken.safeTransfer(treasury, amount);
        emit EvaluatorSlashed(evaluator, amount, treasury, reasonHash);
    }
}
