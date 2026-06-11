// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../access/GoalOSAccessControl.sol";

contract ProofSeedRegistry is GoalOSAccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    enum SeedStatus {
        None,
        Draft,
        Reviewed,
        Spawned,
        Archived
    }

    struct ProofSeed {
        address sponsor;
        bytes32 seedHash;
        string metadataURI;
        bytes32 category;
        SeedStatus status;
        uint256 createdAt;
        uint256 spawnedJobId;
    }

    IERC20 public immutable agialphaToken;
    address public treasury;
    uint256 public proofSeedFeeAGIALPHA = 50 ether;
    uint256 public nextSeedId = 1;

    mapping(uint256 => ProofSeed) public proofSeeds;

    event ProofSeedCreated(uint256 indexed seedId, address indexed sponsor, bytes32 indexed seedHash, string metadataURI, bytes32 category);
    event ProofSeedStatusUpdated(uint256 indexed seedId, SeedStatus status, bytes32 indexed reasonHash);
    event ProofSeedSpawnedJob(uint256 indexed seedId, uint256 indexed jobId);
    event ProofSeedFeeUpdated(uint256 proofSeedFeeAGIALPHA);
    event TreasuryUpdated(address indexed treasury);

    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
        require(agialphaToken_ != address(0), "SEED_ZERO_AGIALPHA");
        require(treasury_ != address(0), "SEED_ZERO_TREASURY");
        agialphaToken = IERC20(agialphaToken_);
        treasury = treasury_;
    }

    function setProofSeedFee(uint256 proofSeedFeeAGIALPHA_) external onlyAdmin {
        proofSeedFeeAGIALPHA = proofSeedFeeAGIALPHA_;
        emit ProofSeedFeeUpdated(proofSeedFeeAGIALPHA_);
    }

    function setTreasury(address treasury_) external onlyAdmin {
        require(treasury_ != address(0), "SEED_ZERO_TREASURY");
        treasury = treasury_;
        emit TreasuryUpdated(treasury_);
    }

    function createProofSeed(
        bytes32 seedHash,
        string calldata metadataURI,
        bytes32 category
    ) external nonReentrant whenNotPaused returns (uint256 seedId) {
        require(seedHash != bytes32(0), "SEED_ZERO_HASH");
        require(category != bytes32(0), "SEED_ZERO_CATEGORY");

        if (proofSeedFeeAGIALPHA > 0) {
            agialphaToken.safeTransferFrom(msg.sender, treasury, proofSeedFeeAGIALPHA);
        }

        seedId = nextSeedId++;
        proofSeeds[seedId] = ProofSeed(
            msg.sender,
            seedHash,
            metadataURI,
            category,
            SeedStatus.Draft,
            block.timestamp,
            0
        );

        emit ProofSeedCreated(seedId, msg.sender, seedHash, metadataURI, category);
    }

    function markReviewed(uint256 seedId, bytes32 reasonHash) external onlyOperator {
        require(proofSeeds[seedId].createdAt != 0, "SEED_NOT_FOUND");
        proofSeeds[seedId].status = SeedStatus.Reviewed;
        emit ProofSeedStatusUpdated(seedId, SeedStatus.Reviewed, reasonHash);
    }

    function markSpawned(uint256 seedId, uint256 jobId) external onlyOperator {
        ProofSeed storage seed = proofSeeds[seedId];
        require(seed.createdAt != 0, "SEED_NOT_FOUND");
        require(jobId != 0, "SEED_ZERO_JOB");
        seed.status = SeedStatus.Spawned;
        seed.spawnedJobId = jobId;
        emit ProofSeedSpawnedJob(seedId, jobId);
    }

    function archiveSeed(uint256 seedId, bytes32 reasonHash) external onlyOperator {
        require(proofSeeds[seedId].createdAt != 0, "SEED_NOT_FOUND");
        proofSeeds[seedId].status = SeedStatus.Archived;
        emit ProofSeedStatusUpdated(seedId, SeedStatus.Archived, reasonHash);
    }
}
