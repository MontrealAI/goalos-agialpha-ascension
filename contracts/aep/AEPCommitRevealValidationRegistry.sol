// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPCommitRevealValidationRegistry is GoalOSAccessControl {
    enum RoundStatus { None, Open, Reveal, Finalized, Cancelled }
    struct ValidationRound {
        bytes32 subjectType;
        uint256 subjectId;
        uint256 commitDeadline;
        uint256 revealDeadline;
        uint256 minReveals;
        uint256 revealCount;
        bytes32 finalResultHash;
        RoundStatus status;
        string metadataURI;
        uint256 createdAt;
    }
    struct RevealRecord { bytes32 verdictHash; uint16 scoreBps; bytes32 evidenceHash; bool revealed; }

    uint256 public nextRoundId = 1;
    mapping(address => bool) public validatorAllowed;
    mapping(uint256 => ValidationRound) public rounds;
    mapping(uint256 => mapping(address => bytes32)) public commitments;
    mapping(uint256 => mapping(address => RevealRecord)) public reveals;

    event ValidatorAllowedUpdated(address indexed validator, bool allowed);
    event ValidationRoundOpened(uint256 indexed roundId, bytes32 indexed subjectType, uint256 indexed subjectId, uint256 commitDeadline, uint256 revealDeadline);
    event VerdictCommitted(uint256 indexed roundId, address indexed validator, bytes32 commitment);
    event VerdictRevealed(uint256 indexed roundId, address indexed validator, bytes32 verdictHash, uint16 scoreBps, bytes32 evidenceHash);
    event ValidationRoundFinalized(uint256 indexed roundId, bytes32 finalResultHash, uint256 revealCount);
    event ValidationRoundCancelled(uint256 indexed roundId, bytes32 reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    modifier onlyAllowedValidator() {
        require(validatorAllowed[msg.sender] || hasRole(DEFAULT_ADMIN_ROLE, msg.sender) || hasRole(OPERATOR_ROLE, msg.sender), "AEP_VAL_NOT_ALLOWED");
        _;
    }

    function setValidatorAllowed(address validator, bool allowed) external onlyOperator {
        require(validator != address(0), "AEP_VAL_ZERO_VALIDATOR");
        validatorAllowed[validator] = allowed;
        emit ValidatorAllowedUpdated(validator, allowed);
    }

    function openValidationRound(
        bytes32 subjectType,
        uint256 subjectId,
        uint256 commitDuration,
        uint256 revealDuration,
        uint256 minReveals,
        string calldata metadataURI
    ) external onlyOperator returns (uint256 roundId) {
        require(subjectType != bytes32(0), "AEP_VAL_ZERO_TYPE");
        require(subjectId != 0, "AEP_VAL_ZERO_SUBJECT");
        require(commitDuration > 0 && revealDuration > 0, "AEP_VAL_BAD_DURATION");
        require(minReveals > 0, "AEP_VAL_ZERO_MIN");
        roundId = nextRoundId++;
        uint256 commitDeadline = block.timestamp + commitDuration;
        uint256 revealDeadline = commitDeadline + revealDuration;
        rounds[roundId] = ValidationRound(subjectType, subjectId, commitDeadline, revealDeadline, minReveals, 0, bytes32(0), RoundStatus.Open, metadataURI, block.timestamp);
        emit ValidationRoundOpened(roundId, subjectType, subjectId, commitDeadline, revealDeadline);
    }

    function commitVerdict(uint256 roundId, bytes32 commitment) external onlyAllowedValidator {
        ValidationRound storage round = rounds[roundId];
        require(round.status == RoundStatus.Open, "AEP_VAL_NOT_OPEN");
        require(block.timestamp <= round.commitDeadline, "AEP_VAL_COMMIT_CLOSED");
        require(commitment != bytes32(0), "AEP_VAL_ZERO_COMMIT");
        require(commitments[roundId][msg.sender] == bytes32(0), "AEP_VAL_ALREADY_COMMITTED");
        commitments[roundId][msg.sender] = commitment;
        emit VerdictCommitted(roundId, msg.sender, commitment);
    }

    function revealVerdict(uint256 roundId, bytes32 verdictHash, uint16 scoreBps, bytes32 evidenceHash, bytes32 salt) external onlyAllowedValidator {
        ValidationRound storage round = rounds[roundId];
        require(round.status == RoundStatus.Open || round.status == RoundStatus.Reveal, "AEP_VAL_BAD_STATUS");
        require(block.timestamp > round.commitDeadline, "AEP_VAL_REVEAL_NOT_STARTED");
        require(block.timestamp <= round.revealDeadline, "AEP_VAL_REVEAL_CLOSED");
        require(!reveals[roundId][msg.sender].revealed, "AEP_VAL_ALREADY_REVEALED");
        require(scoreBps <= 10000, "AEP_VAL_SCORE_GT_10000");
        bytes32 expected = keccak256(abi.encode(roundId, verdictHash, scoreBps, evidenceHash, salt));
        require(commitments[roundId][msg.sender] == expected, "AEP_VAL_BAD_REVEAL");
        round.status = RoundStatus.Reveal;
        round.revealCount += 1;
        reveals[roundId][msg.sender] = RevealRecord(verdictHash, scoreBps, evidenceHash, true);
        emit VerdictRevealed(roundId, msg.sender, verdictHash, scoreBps, evidenceHash);
    }

    function finalizeRound(uint256 roundId, bytes32 finalResultHash) external onlyOperator {
        ValidationRound storage round = rounds[roundId];
        require(round.status == RoundStatus.Open || round.status == RoundStatus.Reveal, "AEP_VAL_BAD_STATUS");
        require(block.timestamp > round.revealDeadline, "AEP_VAL_REVEAL_ACTIVE");
        require(round.revealCount >= round.minReveals, "AEP_VAL_INSUFFICIENT_REVEALS");
        require(finalResultHash != bytes32(0), "AEP_VAL_ZERO_FINAL");
        round.status = RoundStatus.Finalized;
        round.finalResultHash = finalResultHash;
        emit ValidationRoundFinalized(roundId, finalResultHash, round.revealCount);
    }

    function cancelRound(uint256 roundId, bytes32 reasonHash) external onlyOperator {
        ValidationRound storage round = rounds[roundId];
        require(round.createdAt != 0, "AEP_VAL_NOT_FOUND");
        require(round.status != RoundStatus.Finalized, "AEP_VAL_FINALIZED");
        round.status = RoundStatus.Cancelled;
        emit ValidationRoundCancelled(roundId, reasonHash);
    }
}
