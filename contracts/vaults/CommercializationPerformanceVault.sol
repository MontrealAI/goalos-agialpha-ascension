// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../access/GoalOSAccessControl.sol";

contract CommercializationPerformanceVault is GoalOSAccessControl {
    using SafeERC20 for IERC20;

    enum TrancheStatus {
        None,
        Proposed,
        Approved,
        Released,
        Cancelled
    }

    struct Tranche {
        address recipient;
        uint256 amount;
        bytes32 milestoneHash;
        bytes32 evidenceHash;
        bytes32 valueHash;
        uint256 releaseAfter;
        uint256 proposedAt;
        uint256 approvedAt;
        address proposer;
        address approver;
        TrancheStatus status;
        string memoURI;
    }

    IERC20 public immutable agialphaToken;
    uint256 public nextTrancheId = 1;
    uint256 public minApprovalDelay = 2 days;
    mapping(uint256 => Tranche) public tranches;

    event TrancheProposed(
        uint256 indexed trancheId,
        address indexed recipient,
        uint256 amount,
        bytes32 indexed milestoneHash,
        bytes32 evidenceHash,
        bytes32 valueHash,
        uint256 releaseAfter,
        string memoURI
    );
    event TrancheApproved(uint256 indexed trancheId, bytes32 indexed approvalHash, address indexed approver);
    event TrancheReleased(uint256 indexed trancheId, address indexed recipient, uint256 amount);
    event TrancheCancelled(uint256 indexed trancheId, bytes32 indexed reasonHash);
    event MinApprovalDelayUpdated(uint256 minApprovalDelay);

    constructor(address admin, address agialphaToken_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "CPV_ZERO_AGIALPHA");
        agialphaToken = IERC20(agialphaToken_);
    }

    function setMinApprovalDelay(uint256 minApprovalDelay_) external onlyAdmin {
        require(minApprovalDelay_ <= 30 days, "CPV_DELAY_TOO_LONG");
        minApprovalDelay = minApprovalDelay_;
        emit MinApprovalDelayUpdated(minApprovalDelay_);
    }

    function proposeTranche(
        address recipient,
        uint256 amount,
        bytes32 milestoneHash,
        bytes32 evidenceHash,
        bytes32 valueHash,
        uint256 releaseAfter,
        string calldata memoURI
    ) external onlyOperator returns (uint256 trancheId) {
        require(recipient != address(0), "CPV_ZERO_RECIPIENT");
        require(amount > 0, "CPV_ZERO_AMOUNT");
        require(milestoneHash != bytes32(0), "CPV_ZERO_MILESTONE");
        require(evidenceHash != bytes32(0), "CPV_ZERO_EVIDENCE");
        require(valueHash != bytes32(0), "CPV_ZERO_VALUE");

        trancheId = nextTrancheId++;
        tranches[trancheId] = Tranche(
            recipient,
            amount,
            milestoneHash,
            evidenceHash,
            valueHash,
            releaseAfter,
            block.timestamp,
            0,
            msg.sender,
            address(0),
            TrancheStatus.Proposed,
            memoURI
        );

        emit TrancheProposed(trancheId, recipient, amount, milestoneHash, evidenceHash, valueHash, releaseAfter, memoURI);
    }

    function approveTranche(uint256 trancheId, bytes32 approvalHash) external onlyAdmin {
        Tranche storage tranche = tranches[trancheId];
        require(tranche.status == TrancheStatus.Proposed, "CPV_NOT_PROPOSED");
        require(approvalHash != bytes32(0), "CPV_ZERO_APPROVAL");
        require(tranche.proposer != msg.sender, "CPV_PROPOSER_CANNOT_APPROVE");
        require(block.timestamp >= tranche.proposedAt + minApprovalDelay, "CPV_APPROVAL_TOO_EARLY");

        tranche.status = TrancheStatus.Approved;
        tranche.approvedAt = block.timestamp;
        tranche.approver = msg.sender;

        emit TrancheApproved(trancheId, approvalHash, msg.sender);
    }

    function releaseTranche(uint256 trancheId) external whenNotPaused {
        require(hasRole(VAULT_MANAGER_ROLE, msg.sender) || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "CPV_NOT_MANAGER");
        Tranche storage tranche = tranches[trancheId];
        require(tranche.status == TrancheStatus.Approved, "CPV_NOT_APPROVED");
        require(block.timestamp >= tranche.releaseAfter, "CPV_TOO_EARLY");
        require(block.timestamp >= tranche.approvedAt + minApprovalDelay, "CPV_RELEASE_DELAY_ACTIVE");

        tranche.status = TrancheStatus.Released;
        agialphaToken.safeTransfer(tranche.recipient, tranche.amount);
        emit TrancheReleased(trancheId, tranche.recipient, tranche.amount);
    }

    function cancelTranche(uint256 trancheId, bytes32 reasonHash) external onlyAdmin {
        Tranche storage tranche = tranches[trancheId];
        require(
            tranche.status == TrancheStatus.Proposed || tranche.status == TrancheStatus.Approved,
            "CPV_BAD_STATUS"
        );
        require(reasonHash != bytes32(0), "CPV_ZERO_REASON");
        tranche.status = TrancheStatus.Cancelled;
        emit TrancheCancelled(trancheId, reasonHash);
    }
}
