// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/BusinessOverrideCore.sol";
import "../interfaces/IGoalOSAccounting.sol";
import "../interfaces/IJobRegistry.sol";

contract JobRegistry is BusinessOverrideCore, ReentrancyGuard, IJobRegistry, IGoalOSAccounting {
    using SafeERC20 for IERC20;

    struct Job {
        address sponsor;
        string metadataURI;
        bytes32 metadataHash;
        address rewardToken;
        uint256 rewardAmount;
        uint256 deadline;
        address assignee;
        JobStatus status;
        uint256 submissionId;
        bool rewardPaid;
        uint256 createdAt;
    }

    IERC20 public immutable agialphaToken;
    address public treasury;
    uint256 public postingFeeAGIALPHA = 100 ether;
    uint256 public nextJobId = 1;
    uint256 public maxProtectedLiabilityPerToken;
    uint256 public maxSingleReward;

    bool public rewardTokenAllowlistEnabled = true;

    mapping(uint256 => Job) public jobs;
    mapping(address => bool) public allowedRewardTokens;
    mapping(address => uint256) private _protectedLiability;
    mapping(address => uint256) private _totalInflow;
    mapping(address => uint256) private _totalOutflow;

    event JobPosted(
        uint256 indexed jobId,
        address indexed sponsor,
        string metadataURI,
        bytes32 indexed metadataHash,
        address rewardToken,
        uint256 rewardAmount,
        uint256 deadline
    );
    event JobClaimed(uint256 indexed jobId, address indexed builder);
    event JobSubmitted(uint256 indexed jobId, uint256 indexed submissionId);
    event JobApproved(uint256 indexed jobId);
    event JobRejected(uint256 indexed jobId, bytes32 indexed reasonHash);
    event JobCancelled(uint256 indexed jobId, bytes32 indexed reasonHash);
    event JobExpired(uint256 indexed jobId, bytes32 indexed reasonHash);
    event RewardReleased(uint256 indexed jobId, address indexed builder, address rewardToken, uint256 rewardAmount);
    event RewardRefunded(uint256 indexed jobId, address indexed sponsor, address rewardToken, uint256 rewardAmount, bytes32 indexed reasonHash);
    event PostingFeeUpdated(uint256 postingFeeAGIALPHA);
    event TreasuryUpdated(address treasury);
    event RewardTokenAllowedUpdated(address indexed token, bool allowed);
    event RewardTokenAllowlistModeUpdated(bool enabled);
    event RiskLimitsUpdated(uint256 maxProtectedLiabilityPerToken, uint256 maxSingleReward);
    event BusinessJobResolved(uint256 indexed jobId, bytes32 indexed action, address indexed token, uint256 amount, address recipient, bytes32 reasonHash, bytes32 evidenceHash);

    constructor(address admin, address agialphaToken_, address treasury_) BusinessOverrideCore(admin) {
        require(agialphaToken_ != address(0), "JOB_ZERO_AGIALPHA");
        require(treasury_ != address(0), "JOB_ZERO_TREASURY");
        agialphaToken = IERC20(agialphaToken_);
        treasury = treasury_;
        allowedRewardTokens[agialphaToken_] = true;
        emit RewardTokenAllowedUpdated(agialphaToken_, true);
    }

    function setPostingFee(uint256 postingFeeAGIALPHA_) external onlyAdmin {
        postingFeeAGIALPHA = postingFeeAGIALPHA_;
        emit PostingFeeUpdated(postingFeeAGIALPHA_);
    }

    function setTreasury(address treasury_) external onlyAdmin {
        require(treasury_ != address(0), "JOB_ZERO_TREASURY");
        treasury = treasury_;
        emit TreasuryUpdated(treasury_);
    }

    function setRewardTokenAllowed(address token, bool allowed) external onlyAdmin {
        require(token != address(0), "JOB_ZERO_REWARD_TOKEN");
        allowedRewardTokens[token] = allowed;
        emit RewardTokenAllowedUpdated(token, allowed);
    }

    function setRewardTokenAllowlistEnabled(bool enabled) external onlyAdmin {
        rewardTokenAllowlistEnabled = enabled;
        emit RewardTokenAllowlistModeUpdated(enabled);
    }

    function setRiskLimits(uint256 maxProtectedLiabilityPerToken_, uint256 maxSingleReward_) external onlyAdmin {
        require(maxProtectedLiabilityPerToken_ > 0, "JOB_ZERO_LIABILITY_LIMIT");
        require(maxSingleReward_ > 0, "JOB_ZERO_SINGLE_LIMIT");
        maxProtectedLiabilityPerToken = maxProtectedLiabilityPerToken_;
        maxSingleReward = maxSingleReward_;
        emit RiskLimitsUpdated(maxProtectedLiabilityPerToken_, maxSingleReward_);
    }

    function postJob(
        string calldata metadataURI,
        bytes32 metadataHash,
        address rewardToken,
        uint256 rewardAmount,
        uint256 deadline
    ) external nonReentrant whenNotPaused returns (uint256 jobId) {
        require(metadataHash != bytes32(0), "JOB_ZERO_METADATA_HASH");
        require(deadline > block.timestamp, "JOB_BAD_DEADLINE");
        require(rewardToken != address(0) || rewardAmount == 0, "JOB_BAD_REWARD");

        if (rewardAmount > 0 && rewardTokenAllowlistEnabled) {
            require(allowedRewardTokens[rewardToken], "JOB_REWARD_TOKEN_NOT_ALLOWED");
        }

        if (postingFeeAGIALPHA > 0) {
            agialphaToken.safeTransferFrom(msg.sender, treasury, postingFeeAGIALPHA);
        }

        if (rewardAmount > 0) {
            require(maxSingleReward == 0 || rewardAmount <= maxSingleReward, "JOB_SINGLE_LIMIT");
            require(maxProtectedLiabilityPerToken == 0 || _protectedLiability[rewardToken] + rewardAmount <= maxProtectedLiabilityPerToken, "JOB_TOKEN_LIABILITY_LIMIT");
            uint256 beforeBalance = IERC20(rewardToken).balanceOf(address(this));
            IERC20(rewardToken).safeTransferFrom(msg.sender, address(this), rewardAmount);
            uint256 received = IERC20(rewardToken).balanceOf(address(this)) - beforeBalance;
            require(received == rewardAmount, "JOB_FEE_ON_TRANSFER_UNSUPPORTED");
            _protectedLiability[rewardToken] += rewardAmount;
            _totalInflow[rewardToken] += received;
            require(isSolvent(rewardToken), "JOB_INSOLVENT");
        }

        jobId = nextJobId++;
        jobs[jobId] = Job(
            msg.sender,
            metadataURI,
            metadataHash,
            rewardToken,
            rewardAmount,
            deadline,
            address(0),
            JobStatus.Open,
            0,
            false,
            block.timestamp
        );

        emit JobPosted(jobId, msg.sender, metadataURI, metadataHash, rewardToken, rewardAmount, deadline);
    }

    function markClaimed(uint256 jobId, address builder) external onlyOperator {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Open, "JOB_NOT_OPEN");
        require(block.timestamp <= job.deadline, "JOB_EXPIRED");
        require(builder != address(0), "JOB_ZERO_BUILDER");
        job.assignee = builder;
        job.status = JobStatus.Claimed;
        emit JobClaimed(jobId, builder);
    }

    function markSubmitted(uint256 jobId, uint256 submissionId) external onlyOperator {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Claimed, "JOB_NOT_CLAIMED");
        require(submissionId != 0, "JOB_ZERO_SUBMISSION");
        require(block.timestamp <= job.deadline, "JOB_EXPIRED");
        job.submissionId = submissionId;
        job.status = JobStatus.Submitted;
        emit JobSubmitted(jobId, submissionId);
    }

    function markApproved(uint256 jobId) external onlyOperator {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Submitted, "JOB_NOT_SUBMITTED");
        job.status = JobStatus.Approved;
        emit JobApproved(jobId);
    }

    function markRejected(uint256 jobId, bytes32 reasonHash) external onlyOperator {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Submitted || job.status == JobStatus.Claimed, "JOB_BAD_STATUS");
        job.status = JobStatus.Rejected;
        emit JobRejected(jobId, reasonHash);
    }

    function releaseReward(uint256 jobId, address builder) external onlyOperator nonReentrant {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Approved, "JOB_NOT_APPROVED");
        require(job.assignee == builder, "JOB_NOT_ASSIGNEE");
        require(!job.rewardPaid, "JOB_PAID");
        job.rewardPaid = true;

        if (job.rewardAmount > 0) {
            _protectedLiability[job.rewardToken] -= job.rewardAmount;
            _totalOutflow[job.rewardToken] += job.rewardAmount;
            IERC20(job.rewardToken).safeTransfer(builder, job.rewardAmount);
        }

        emit RewardReleased(jobId, builder, job.rewardToken, job.rewardAmount);
    }

    function refundRejectedReward(uint256 jobId, bytes32 reasonHash) external onlyOperator nonReentrant {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Rejected, "JOB_NOT_REJECTED");
        _refundSponsor(jobId, reasonHash);
    }

    function expireClaimedJob(uint256 jobId, bytes32 reasonHash) external onlyOperator nonReentrant {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Claimed, "JOB_NOT_CLAIMED");
        require(block.timestamp > job.deadline, "JOB_NOT_EXPIRED");
        job.status = JobStatus.Expired;
        _refundSponsor(jobId, reasonHash);
        emit JobExpired(jobId, reasonHash);
    }

    function cancelOpenJob(uint256 jobId, bytes32 reasonHash) external nonReentrant {
        Job storage job = jobs[jobId];
        require(
            msg.sender == job.sponsor || hasRole(DEFAULT_ADMIN_ROLE, msg.sender) || hasRole(OPERATOR_ROLE, msg.sender),
            "JOB_NOT_AUTH"
        );
        require(job.status == JobStatus.Open, "JOB_NOT_OPEN");
        job.status = JobStatus.Cancelled;
        _refundSponsor(jobId, reasonHash);
        emit JobCancelled(jobId, reasonHash);
    }

    function expireOpenJob(uint256 jobId, bytes32 reasonHash) external nonReentrant {
        Job storage job = jobs[jobId];
        require(job.status == JobStatus.Open, "JOB_NOT_OPEN");
        require(block.timestamp > job.deadline, "JOB_NOT_EXPIRED");
        job.status = JobStatus.Expired;
        _refundSponsor(jobId, reasonHash);
        emit JobExpired(jobId, reasonHash);
    }

    function _refundSponsor(uint256 jobId, bytes32 reasonHash) internal {
        Job storage job = jobs[jobId];
        require(!job.rewardPaid, "JOB_REWARD_ALREADY_FINALIZED");
        job.rewardPaid = true;

        if (job.rewardAmount > 0) {
            _protectedLiability[job.rewardToken] -= job.rewardAmount;
            _totalOutflow[job.rewardToken] += job.rewardAmount;
            IERC20(job.rewardToken).safeTransfer(job.sponsor, job.rewardAmount);
        }

        emit RewardRefunded(jobId, job.sponsor, job.rewardToken, job.rewardAmount, reasonHash);
    }

    function ownerResolveJob(uint256 jobId, JobStatus newStatus, address recipient, bytes32 reasonHash, bytes32 evidenceHash) external onlyOwner nonReentrant returns (bytes32 overrideId) {
        Job storage job = jobs[jobId];
        require(job.sponsor != address(0), "JOB_UNKNOWN");
        require(newStatus == JobStatus.Approved || newStatus == JobStatus.Rejected || newStatus == JobStatus.Cancelled || newStatus == JobStatus.Expired, "JOB_BAD_OVERRIDE_STATUS");
        require(!job.rewardPaid, "JOB_REWARD_ALREADY_FINALIZED");
        bytes32 previousHash = keccak256(abi.encode(job));
        job.status = newStatus;
        job.rewardPaid = true;
        address payout = recipient == address(0) ? job.sponsor : recipient;
        if (job.rewardAmount > 0) {
            _protectedLiability[job.rewardToken] -= job.rewardAmount;
            _totalOutflow[job.rewardToken] += job.rewardAmount;
            IERC20(job.rewardToken).safeTransfer(payout, job.rewardAmount);
        }
        bytes32 newHash = keccak256(abi.encode(job));
        overrideId = _executeBusinessOverride(keccak256("GOALOS_JOB_OWNER_RESOLVE"), bytes32(jobId), previousHash, newHash, reasonHash, evidenceHash);
        emit BusinessJobResolved(jobId, keccak256("GOALOS_JOB_OWNER_RESOLVE"), job.rewardToken, job.rewardAmount, payout, reasonHash, evidenceHash);
    }

    function actualBalance(address token) public view returns (uint256) { return IERC20(token).balanceOf(address(this)); }
    function protectedLiability(address token) public view returns (uint256) { return _protectedLiability[token]; }
    function reservedBalance(address token) public pure returns (uint256) { token; return 0; }
    function pendingWithdrawal(address token) public pure returns (uint256) { token; return 0; }
    function freeBalance(address token) public view returns (uint256) { uint256 enc = _protectedLiability[token]; uint256 bal = actualBalance(token); return bal > enc ? bal - enc : 0; }
    function totalInflow(address token) public view returns (uint256) { return _totalInflow[token]; }
    function totalOutflow(address token) public view returns (uint256) { return _totalOutflow[token]; }
    function isSolvent(address token) public view returns (bool) { return actualBalance(token) >= _protectedLiability[token]; }
    function accountingStateHash(address token) public view returns (bytes32) { return keccak256(abi.encode(token, actualBalance(token), _protectedLiability[token], uint256(0), uint256(0), _totalInflow[token], _totalOutflow[token])); }

    function statusOf(uint256 jobId) external view returns (JobStatus) {
        return jobs[jobId].status;
    }

    function assigneeOf(uint256 jobId) external view returns (address) {
        return jobs[jobId].assignee;
    }

    function sponsorOf(uint256 jobId) external view returns (address) {
        return jobs[jobId].sponsor;
    }

    function deadlineOf(uint256 jobId) external view returns (uint256) {
        return jobs[jobId].deadline;
    }
}
