// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";
import "../interfaces/IProofSubmissionRegistry.sol";

contract ReviewerBondRegistry is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable agialphaToken;
    IProofSubmissionRegistry public immutable proofSubmissionRegistry;
    address public treasury;
    uint256 public reviewerBondAGIALPHA = 100 ether;
    uint256 public reviewChallengePeriod = 7 days;
    bool public allowlistRequired;

    struct ReviewerProfile {
        uint256 bondedAmount;
        string metadataURI;
        bool active;
        bool approved;
        uint256 createdAt;
        uint256 lastReviewAt;
        uint256 reviewCount;
    }

    mapping(address => ReviewerProfile) public reviewers;

    event ReviewerBondUpdated(uint256 reviewerBondAGIALPHA);
    event ReviewChallengePeriodUpdated(uint256 reviewChallengePeriod);
    event AllowlistModeUpdated(bool allowlistRequired);
    event ReviewerApproved(address indexed reviewer, bool approved);
    event ReviewerBonded(address indexed reviewer, uint256 amount, string metadataURI);
    event ReviewerUnbonded(address indexed reviewer, uint256 amount);
    event ReviewerSlashed(address indexed reviewer, uint256 amount, bytes32 indexed reasonHash);
    event SubmissionReviewed(uint256 indexed submissionId, address indexed reviewer, bool approved, bytes32 rationaleHash);

    constructor(address admin, address agialphaToken_, address proofSubmissionRegistry_, address treasury_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "REV_ZERO_AGIALPHA");
        require(proofSubmissionRegistry_ != address(0), "REV_ZERO_SUB");
        require(treasury_ != address(0), "REV_ZERO_TREASURY");
        agialphaToken = IERC20(agialphaToken_);
        proofSubmissionRegistry = IProofSubmissionRegistry(proofSubmissionRegistry_);
        treasury = treasury_;
    }

    function setReviewerBond(uint256 reviewerBondAGIALPHA_) external onlyAdmin {
        reviewerBondAGIALPHA = reviewerBondAGIALPHA_;
        emit ReviewerBondUpdated(reviewerBondAGIALPHA_);
    }

    function setReviewChallengePeriod(uint256 reviewChallengePeriod_) external onlyAdmin {
        require(reviewChallengePeriod_ <= 30 days, "REV_PERIOD_TOO_LONG");
        reviewChallengePeriod = reviewChallengePeriod_;
        emit ReviewChallengePeriodUpdated(reviewChallengePeriod_);
    }

    function setAllowlistRequired(bool required_) external onlyAdmin {
        allowlistRequired = required_;
        emit AllowlistModeUpdated(required_);
    }

    function setReviewerApproved(address reviewer, bool approved) external {
        require(hasRole(REVIEWER_MANAGER_ROLE, msg.sender) || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "REV_NOT_MANAGER");
        reviewers[reviewer].approved = approved;
        emit ReviewerApproved(reviewer, approved);
    }

    function bondAsReviewer(string calldata metadataURI) external nonReentrant whenNotPaused {
        ReviewerProfile storage profile = reviewers[msg.sender];
        require(!profile.active, "REV_ACTIVE");
        uint256 amount = reviewerBondAGIALPHA;
        profile.bondedAmount = amount;
        profile.metadataURI = metadataURI;
        profile.active = true;
        profile.createdAt = block.timestamp;
        if (amount > 0) {
            agialphaToken.safeTransferFrom(msg.sender, address(this), amount);
        }
        emit ReviewerBonded(msg.sender, amount, metadataURI);
    }

    function unbondReviewer() external nonReentrant {
        ReviewerProfile storage profile = reviewers[msg.sender];
        require(profile.active, "REV_NOT_ACTIVE");
        if (profile.lastReviewAt != 0) {
            require(block.timestamp >= profile.lastReviewAt + reviewChallengePeriod, "REV_CHALLENGE_ACTIVE");
        }
        uint256 amount = profile.bondedAmount;
        profile.active = false;
        profile.bondedAmount = 0;
        if (amount > 0) {
            agialphaToken.safeTransfer(msg.sender, amount);
        }
        emit ReviewerUnbonded(msg.sender, amount);
    }

    function reviewSubmission(
        uint256 submissionId,
        bool approve,
        bytes32 rationaleHash,
        string calldata credentialURI,
        bytes32 credentialType,
        bool slashBuilder
    ) external nonReentrant whenNotPaused {
        ReviewerProfile storage profile = reviewers[msg.sender];
        require(profile.active, "REV_NOT_ACTIVE");
        if (allowlistRequired) {
            require(profile.approved, "REV_NOT_APPROVED");
        }
        require(rationaleHash != bytes32(0), "REV_ZERO_RATIONALE");

        address builder = proofSubmissionRegistry.builderOf(submissionId);
        require(builder != msg.sender, "REV_SELF_REVIEW");

        profile.lastReviewAt = block.timestamp;
        profile.reviewCount += 1;

        if (approve) {
            proofSubmissionRegistry.approveSubmission(submissionId, msg.sender, rationaleHash, credentialURI, credentialType);
        } else {
            proofSubmissionRegistry.rejectSubmission(submissionId, msg.sender, rationaleHash, slashBuilder);
        }

        emit SubmissionReviewed(submissionId, msg.sender, approve, rationaleHash);
    }

    function slashReviewer(address reviewer, uint256 amount, bytes32 reasonHash) external onlyOperator nonReentrant {
        ReviewerProfile storage profile = reviewers[reviewer];
        require(profile.bondedAmount >= amount, "REV_AMOUNT");
        profile.bondedAmount -= amount;
        if (amount > 0) {
            agialphaToken.safeTransfer(treasury, amount);
        }
        emit ReviewerSlashed(reviewer, amount, reasonHash);
    }
}
