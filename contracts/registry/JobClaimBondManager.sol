// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";
import "../interfaces/IJobRegistry.sol";

contract JobClaimBondManager is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable agialphaToken;
    IJobRegistry public immutable jobRegistry;
    address public treasury;
    uint256 public claimBondAGIALPHA = 50 ether;

    struct ClaimBond {
        address builder;
        uint256 amount;
        bool returnedOrSlashed;
        uint256 createdAt;
    }

    mapping(uint256 => ClaimBond) public claimBonds;

    event ClaimBondAmountUpdated(uint256 claimBondAGIALPHA);
    event TreasuryUpdated(address indexed treasury);
    event JobClaimedWithBond(uint256 indexed jobId, address indexed builder, uint256 amount);
    event ClaimBondReleased(uint256 indexed jobId, address indexed builder, uint256 amount);
    event ClaimBondSlashed(uint256 indexed jobId, address indexed builder, uint256 amount, bytes32 indexed reasonHash);
    event ExpiredClaimedJobReclaimed(uint256 indexed jobId, address indexed builder, bytes32 indexed reasonHash);

    constructor(address admin, address agialphaToken_, address jobRegistry_, address treasury_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "CLAIM_ZERO_AGIALPHA");
        require(jobRegistry_ != address(0), "CLAIM_ZERO_JOB_REG");
        require(treasury_ != address(0), "CLAIM_ZERO_TREASURY");
        agialphaToken = IERC20(agialphaToken_);
        jobRegistry = IJobRegistry(jobRegistry_);
        treasury = treasury_;
    }

    function setClaimBond(uint256 claimBondAGIALPHA_) external onlyAdmin {
        claimBondAGIALPHA = claimBondAGIALPHA_;
        emit ClaimBondAmountUpdated(claimBondAGIALPHA_);
    }

    function setTreasury(address treasury_) external onlyAdmin {
        require(treasury_ != address(0), "CLAIM_ZERO_TREASURY");
        treasury = treasury_;
        emit TreasuryUpdated(treasury_);
    }

    function claimJob(uint256 jobId) external nonReentrant whenNotPaused {
        require(jobRegistry.statusOf(jobId) == IJobRegistry.JobStatus.Open, "CLAIM_NOT_OPEN");
        require(claimBonds[jobId].builder == address(0), "CLAIM_EXISTS");
        uint256 amount = claimBondAGIALPHA;
        claimBonds[jobId] = ClaimBond(msg.sender, amount, false, block.timestamp);
        if (amount > 0) {
            agialphaToken.safeTransferFrom(msg.sender, address(this), amount);
        }
        jobRegistry.markClaimed(jobId, msg.sender);
        emit JobClaimedWithBond(jobId, msg.sender, claimBondAGIALPHA);
    }

    function reclaimExpiredClaimedJob(uint256 jobId, bytes32 reasonHash) external nonReentrant {
        require(reasonHash != bytes32(0), "CLAIM_ZERO_REASON");
        require(jobRegistry.statusOf(jobId) == IJobRegistry.JobStatus.Claimed, "CLAIM_NOT_CLAIMED");
        require(block.timestamp > jobRegistry.deadlineOf(jobId), "CLAIM_NOT_EXPIRED");

        ClaimBond storage bond = claimBonds[jobId];
        require(bond.builder != address(0), "CLAIM_NO_BOND");

        _slashClaimBond(jobId, reasonHash);
        jobRegistry.expireClaimedJob(jobId, reasonHash);

        emit ExpiredClaimedJobReclaimed(jobId, bond.builder, reasonHash);
    }

    function releaseClaimBond(uint256 jobId) external onlyOperator nonReentrant {
        _releaseClaimBond(jobId);
    }

    function slashClaimBond(uint256 jobId, bytes32 reasonHash) external onlyOperator nonReentrant {
        _slashClaimBond(jobId, reasonHash);
    }

    function _releaseClaimBond(uint256 jobId) internal {
        ClaimBond storage bond = claimBonds[jobId];
        require(!bond.returnedOrSlashed, "CLAIM_DONE");
        bond.returnedOrSlashed = true;
        if (bond.amount > 0) {
            agialphaToken.safeTransfer(bond.builder, bond.amount);
        }
        emit ClaimBondReleased(jobId, bond.builder, bond.amount);
    }

    function _slashClaimBond(uint256 jobId, bytes32 reasonHash) internal {
        ClaimBond storage bond = claimBonds[jobId];
        require(!bond.returnedOrSlashed, "CLAIM_DONE");
        bond.returnedOrSlashed = true;
        if (bond.amount > 0) {
            agialphaToken.safeTransfer(treasury, bond.amount);
        }
        emit ClaimBondSlashed(jobId, bond.builder, bond.amount, reasonHash);
    }
}
