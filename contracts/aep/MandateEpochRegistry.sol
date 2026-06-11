// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";

contract MandateEpochRegistry is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;
    enum EpochStatus { None, Open, Committed, Finalized, Disputed, Cancelled }
    struct Mandate { address sponsor; bytes32 mandateHash; bytes32 policyHash; bytes32 scoringRubricHash; bytes32 safetyPolicyHash; string metadataURI; uint256 createdAt; bool active; }
    struct Epoch { uint256 mandateId; uint256 epochNumber; uint256 payoutBudget; bytes32 receiptRoot; bytes32 payoutRoot; bytes32 archiveDeltaRoot; bytes32 quarantineRoot; bytes32 validatorAttestationBundleHash; uint256 challengeWindowEnd; EpochStatus status; string metadataURI; uint256 createdAt; }

    IERC20 public immutable agialphaToken;
    address public treasury;
    uint256 public mandateFeeAGIALPHA = 100 ether;
    uint256 public nextMandateId = 1;
    uint256 public nextEpochId = 1;
    mapping(uint256 => Mandate) public mandates;
    mapping(uint256 => Epoch) public epochs;
    event MandateCreated(uint256 indexed mandateId, address indexed sponsor, bytes32 indexed mandateHash, string metadataURI);
    event EpochOpened(uint256 indexed epochId, uint256 indexed mandateId, uint256 epochNumber, uint256 payoutBudget, string metadataURI);
    event EpochRootsCommitted(uint256 indexed epochId, bytes32 receiptRoot, bytes32 payoutRoot, bytes32 archiveDeltaRoot, bytes32 quarantineRoot, bytes32 validatorAttestationBundleHash);
    event EpochStatusUpdated(uint256 indexed epochId, EpochStatus status, bytes32 indexed reasonHash);

    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "MANDATE_ZERO_TOKEN");
        require(treasury_ != address(0), "MANDATE_ZERO_TREASURY");
        agialphaToken = IERC20(agialphaToken_);
        treasury = treasury_;
    }

    function createMandate(bytes32 mandateHash, bytes32 policyHash, bytes32 scoringRubricHash, bytes32 safetyPolicyHash, string calldata metadataURI) external nonReentrant whenNotPaused returns (uint256 mandateId) {
        require(mandateHash != bytes32(0), "MANDATE_ZERO_HASH");
        if (mandateFeeAGIALPHA > 0) agialphaToken.safeTransferFrom(msg.sender, treasury, mandateFeeAGIALPHA);
        mandateId = nextMandateId++;
        mandates[mandateId] = Mandate(msg.sender, mandateHash, policyHash, scoringRubricHash, safetyPolicyHash, metadataURI, block.timestamp, true);
        emit MandateCreated(mandateId, msg.sender, mandateHash, metadataURI);
    }

    function openEpoch(uint256 mandateId, uint256 epochNumber, uint256 payoutBudget, string calldata metadataURI) external onlyOperator returns (uint256 epochId) {
        require(mandates[mandateId].active, "MANDATE_INACTIVE");
        epochId = nextEpochId++;
        epochs[epochId] = Epoch(mandateId, epochNumber, payoutBudget, bytes32(0), bytes32(0), bytes32(0), bytes32(0), bytes32(0), 0, EpochStatus.Open, metadataURI, block.timestamp);
        emit EpochOpened(epochId, mandateId, epochNumber, payoutBudget, metadataURI);
    }

    function commitEpochRoots(uint256 epochId, bytes32 receiptRoot, bytes32 payoutRoot, bytes32 archiveDeltaRoot, bytes32 quarantineRoot, bytes32 validatorAttestationBundleHash, uint256 challengeWindowEnd) external onlyOperator {
        Epoch storage e = epochs[epochId];
        require(e.createdAt != 0, "EPOCH_NOT_FOUND");
        e.receiptRoot = receiptRoot; e.payoutRoot = payoutRoot; e.archiveDeltaRoot = archiveDeltaRoot; e.quarantineRoot = quarantineRoot; e.validatorAttestationBundleHash = validatorAttestationBundleHash; e.challengeWindowEnd = challengeWindowEnd; e.status = EpochStatus.Committed;
        emit EpochRootsCommitted(epochId, receiptRoot, payoutRoot, archiveDeltaRoot, quarantineRoot, validatorAttestationBundleHash);
    }

    function setEpochStatus(uint256 epochId, EpochStatus status, bytes32 reasonHash) external onlyOperator {
        require(epochs[epochId].createdAt != 0, "EPOCH_NOT_FOUND");
        epochs[epochId].status = status;
        emit EpochStatusUpdated(epochId, status, reasonHash);
    }
}
