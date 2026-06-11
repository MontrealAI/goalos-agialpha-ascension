// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";

contract AEPGoalOSCommitRegistry is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    struct GoalOSCommit {
        address sponsor;
        bytes32 commitHash;
        bytes32 successCriteriaHash;
        bytes32 constraintsHash;
        bytes32 authorityHash;
        bytes32 dataBoundaryHash;
        bytes32 rollbackObligationHash;
        bytes32 claimBoundaryHash;
        uint8 riskClass;
        string metadataURI;
        bool active;
        uint256 createdAt;
    }

    IERC20 public immutable agialphaToken;
    address public treasury;
    uint256 public commitFeeAGIALPHA = 25 ether;
    uint256 public nextCommitId = 1;
    mapping(uint256 => GoalOSCommit) public commits;

    event GoalOSCommitCreated(uint256 indexed commitId, address indexed sponsor, bytes32 indexed commitHash, uint8 riskClass, string metadataURI);
    event GoalOSCommitStatusUpdated(uint256 indexed commitId, bool active, bytes32 indexed reasonHash);
    event CommitFeeUpdated(uint256 commitFeeAGIALPHA);

    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "AEP_COMMIT_ZERO_TOKEN");
        require(treasury_ != address(0), "AEP_COMMIT_ZERO_TREASURY");
        agialphaToken = IERC20(agialphaToken_);
        treasury = treasury_;
    }

    function setCommitFee(uint256 commitFeeAGIALPHA_) external onlyAdmin { commitFeeAGIALPHA = commitFeeAGIALPHA_; emit CommitFeeUpdated(commitFeeAGIALPHA_); }

    function createCommit(bytes32 commitHash, bytes32 successCriteriaHash, bytes32 constraintsHash, bytes32 authorityHash, bytes32 dataBoundaryHash, bytes32 rollbackObligationHash, bytes32 claimBoundaryHash, uint8 riskClass, string calldata metadataURI) external nonReentrant whenNotPaused returns (uint256 commitId) {
        require(commitHash != bytes32(0), "AEP_COMMIT_ZERO_HASH");
        if (commitFeeAGIALPHA > 0) agialphaToken.safeTransferFrom(msg.sender, treasury, commitFeeAGIALPHA);
        commitId = nextCommitId++;
        commits[commitId] = GoalOSCommit(msg.sender, commitHash, successCriteriaHash, constraintsHash, authorityHash, dataBoundaryHash, rollbackObligationHash, claimBoundaryHash, riskClass, metadataURI, true, block.timestamp);
        emit GoalOSCommitCreated(commitId, msg.sender, commitHash, riskClass, metadataURI);
    }

    function setCommitActive(uint256 commitId, bool active, bytes32 reasonHash) external onlyOperator {
        require(commits[commitId].createdAt != 0, "AEP_COMMIT_NOT_FOUND");
        commits[commitId].active = active;
        emit GoalOSCommitStatusUpdated(commitId, active, reasonHash);
    }
}
