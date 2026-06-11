// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";
import "../interfaces/IJobRegistry.sol";
import "../interfaces/IJobClaimBondManager.sol";
import "../interfaces/IReputationRegistry.sol";
import "./ProofCardRegistry.sol";
import "./ProofCredentialRegistry.sol";

contract ProofSubmissionRegistry is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    enum SubmissionStatus {
        None,
        Pending,
        Approved,
        Rejected
    }

    struct ProofSubmission {
        uint256 jobId;
        address builder;
        string metadataURI;
        bytes32 proofHash;
        bytes32 proofCardHash;
        uint256 proofBondAmount;
        uint256 proofCardFeeAmount;
        uint256 credentialFeeAmount;
        SubmissionStatus status;
        address reviewer;
        uint256 proofCardId;
        uint256 credentialTokenId;
        uint256 createdAt;
        uint256 reviewedAt;
    }

    IERC20 public immutable agialphaToken;
    IJobRegistry public immutable jobRegistry;
    IJobClaimBondManager public immutable claimBondManager;
    ProofCardRegistry public immutable proofCardRegistry;
    ProofCredentialRegistry public immutable credentialRegistry;
    IReputationRegistry public immutable reputationRegistry;
    address public treasury;

    uint256 public proofBondAGIALPHA = 25 ether;
    uint256 public proofCardRegistryFeeAGIALPHA = 5 ether;
    uint256 public credentialMintFeeAGIALPHA = 5 ether;
    uint256 public nextSubmissionId = 1;

    mapping(uint256 => ProofSubmission) public submissions;

    event ProofBondUpdated(uint256 proofBondAGIALPHA);
    event ProofActionFeesUpdated(uint256 proofCardRegistryFeeAGIALPHA, uint256 credentialMintFeeAGIALPHA);
    event TreasuryUpdated(address indexed treasury);
    event ProofSubmitted(uint256 indexed submissionId, uint256 indexed jobId, address indexed builder, bytes32 proofHash, bytes32 proofCardHash);
    event ProofActionFeesPaid(uint256 indexed submissionId, address indexed builder, uint256 proofCardRegistryFeeAGIALPHA, uint256 credentialMintFeeAGIALPHA);
    event ProofApproved(uint256 indexed submissionId, uint256 indexed jobId, address indexed builder, address reviewer, uint256 proofCardId, uint256 credentialTokenId);
    event ProofRejected(uint256 indexed submissionId, uint256 indexed jobId, address indexed builder, address reviewer, bytes32 reasonHash, bool slashed);

    constructor(
        address admin,
        address agialphaToken_,
        address jobRegistry_,
        address claimBondManager_,
        address proofCardRegistry_,
        address credentialRegistry_,
        address reputationRegistry_,
        address treasury_
    ) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "SUB_ZERO_AGIALPHA");
        require(jobRegistry_ != address(0), "SUB_ZERO_JOB");
        require(claimBondManager_ != address(0), "SUB_ZERO_CLAIM");
        require(proofCardRegistry_ != address(0), "SUB_ZERO_PC");
        require(credentialRegistry_ != address(0), "SUB_ZERO_CRED");
        require(reputationRegistry_ != address(0), "SUB_ZERO_REP");
        require(treasury_ != address(0), "SUB_ZERO_TREASURY");

        agialphaToken = IERC20(agialphaToken_);
        jobRegistry = IJobRegistry(jobRegistry_);
        claimBondManager = IJobClaimBondManager(claimBondManager_);
        proofCardRegistry = ProofCardRegistry(proofCardRegistry_);
        credentialRegistry = ProofCredentialRegistry(credentialRegistry_);
        reputationRegistry = IReputationRegistry(reputationRegistry_);
        treasury = treasury_;
    }

    function builderOf(uint256 submissionId) external view returns (address) {
        return submissions[submissionId].builder;
    }

    function setProofBond(uint256 proofBondAGIALPHA_) external onlyAdmin {
        require(proofBondAGIALPHA_ >= proofCardRegistryFeeAGIALPHA + credentialMintFeeAGIALPHA, "SUB_BOND_LT_FEES");
        proofBondAGIALPHA = proofBondAGIALPHA_;
        emit ProofBondUpdated(proofBondAGIALPHA_);
    }

    function setProofActionFees(uint256 proofCardRegistryFeeAGIALPHA_, uint256 credentialMintFeeAGIALPHA_) external onlyAdmin {
        require(proofCardRegistryFeeAGIALPHA_ + credentialMintFeeAGIALPHA_ <= proofBondAGIALPHA, "SUB_FEES_GT_BOND");
        proofCardRegistryFeeAGIALPHA = proofCardRegistryFeeAGIALPHA_;
        credentialMintFeeAGIALPHA = credentialMintFeeAGIALPHA_;
        emit ProofActionFeesUpdated(proofCardRegistryFeeAGIALPHA_, credentialMintFeeAGIALPHA_);
    }

    function setTreasury(address treasury_) external onlyAdmin {
        require(treasury_ != address(0), "SUB_ZERO_TREASURY");
        treasury = treasury_;
        emit TreasuryUpdated(treasury_);
    }

    function submitProof(
        uint256 jobId,
        string calldata metadataURI,
        bytes32 proofHash,
        bytes32 proofCardHash
    ) external nonReentrant whenNotPaused returns (uint256 submissionId) {
        require(jobRegistry.statusOf(jobId) == IJobRegistry.JobStatus.Claimed, "SUB_NOT_CLAIMED");
        require(jobRegistry.assigneeOf(jobId) == msg.sender, "SUB_NOT_ASSIGNEE");
        require(block.timestamp <= jobRegistry.deadlineOf(jobId), "SUB_EXPIRED");
        require(proofHash != bytes32(0), "SUB_ZERO_PROOF");
        require(proofCardHash != bytes32(0), "SUB_ZERO_CARD");
        require(proofBondAGIALPHA >= proofCardRegistryFeeAGIALPHA + credentialMintFeeAGIALPHA, "SUB_BOND_LT_FEES");

        if (proofBondAGIALPHA > 0) {
            agialphaToken.safeTransferFrom(msg.sender, address(this), proofBondAGIALPHA);
        }

        submissionId = nextSubmissionId++;
        submissions[submissionId] = ProofSubmission(
            jobId,
            msg.sender,
            metadataURI,
            proofHash,
            proofCardHash,
            proofBondAGIALPHA,
            proofCardRegistryFeeAGIALPHA,
            credentialMintFeeAGIALPHA,
            SubmissionStatus.Pending,
            address(0),
            0,
            0,
            block.timestamp,
            0
        );

        jobRegistry.markSubmitted(jobId, submissionId);
        emit ProofSubmitted(submissionId, jobId, msg.sender, proofHash, proofCardHash);
    }

    function approveSubmission(
        uint256 submissionId,
        address reviewer,
        bytes32 rationaleHash,
        string calldata credentialURI,
        bytes32 credentialType
    ) external onlyOperator nonReentrant {
        ProofSubmission storage sub = submissions[submissionId];
        require(sub.status == SubmissionStatus.Pending, "SUB_NOT_PENDING");
        require(reviewer != address(0), "SUB_ZERO_REVIEWER");
        require(reviewer != sub.builder, "SUB_SELF_REVIEW");
        require(rationaleHash != bytes32(0), "SUB_ZERO_RATIONALE");

        sub.status = SubmissionStatus.Approved;
        sub.reviewer = reviewer;
        sub.reviewedAt = block.timestamp;

        jobRegistry.markApproved(sub.jobId);
        jobRegistry.releaseReward(sub.jobId, sub.builder);

        uint256 actionFees = sub.proofCardFeeAmount + sub.credentialFeeAmount;
        require(sub.proofBondAmount >= actionFees, "SUB_BOND_LT_FEES");

        if (actionFees > 0) {
            agialphaToken.safeTransfer(treasury, actionFees);
            emit ProofActionFeesPaid(submissionId, sub.builder, sub.proofCardFeeAmount, sub.credentialFeeAmount);
        }

        uint256 bondReturn = sub.proofBondAmount - actionFees;
        if (bondReturn > 0) {
            agialphaToken.safeTransfer(sub.builder, bondReturn);
        }

        claimBondManager.releaseClaimBond(sub.jobId);

        uint256 proofCardId = proofCardRegistry.registerProofCard(
            sub.jobId,
            submissionId,
            sub.builder,
            reviewer,
            sub.proofHash,
            sub.proofCardHash,
            sub.metadataURI
        );

        uint256 tokenId = credentialRegistry.issueCredential(
            sub.builder,
            proofCardId,
            sub.proofCardHash,
            credentialType,
            credentialURI
        );

        reputationRegistry.recordApprovedProof(sub.builder, reviewer, proofCardId);
        reputationRegistry.recordCredential(sub.builder, tokenId);

        sub.proofCardId = proofCardId;
        sub.credentialTokenId = tokenId;

        emit ProofApproved(submissionId, sub.jobId, sub.builder, reviewer, proofCardId, tokenId);
    }

    function rejectSubmission(
        uint256 submissionId,
        address reviewer,
        bytes32 reasonHash,
        bool slashBuilder
    ) external onlyOperator nonReentrant {
        ProofSubmission storage sub = submissions[submissionId];
        require(sub.status == SubmissionStatus.Pending, "SUB_NOT_PENDING");
        require(reviewer != address(0), "SUB_ZERO_REVIEWER");
        require(reviewer != sub.builder, "SUB_SELF_REVIEW");
        require(reasonHash != bytes32(0), "SUB_ZERO_REASON");

        sub.status = SubmissionStatus.Rejected;
        sub.reviewer = reviewer;
        sub.reviewedAt = block.timestamp;

        jobRegistry.markRejected(sub.jobId, reasonHash);
        jobRegistry.refundRejectedReward(sub.jobId, reasonHash);

        if (slashBuilder) {
            if (sub.proofBondAmount > 0) {
                agialphaToken.safeTransfer(treasury, sub.proofBondAmount);
            }
            claimBondManager.slashClaimBond(sub.jobId, reasonHash);
        } else {
            if (sub.proofBondAmount > 0) {
                agialphaToken.safeTransfer(sub.builder, sub.proofBondAmount);
            }
            claimBondManager.releaseClaimBond(sub.jobId);
        }

        reputationRegistry.recordRejectedProof(sub.builder, reviewer, reasonHash);

        emit ProofRejected(submissionId, sub.jobId, sub.builder, reviewer, reasonHash, slashBuilder);
    }
}
