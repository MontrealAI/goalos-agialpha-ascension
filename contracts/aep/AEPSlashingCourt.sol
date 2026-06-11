// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

interface IAEPEvaluatorStakingRegistry {
    function slashEvaluator(address evaluator, uint256 amount, bytes32 reasonHash) external;
}

contract AEPSlashingCourt is GoalOSAccessControl {
    enum CaseStatus { None, Open, Resolved, Cancelled }
    enum Resolution { None, NoSlash, Slash, Escalate }
    struct SlashingCase {
        address respondent;
        uint256 requestedSlashAmount;
        bytes32 evidenceHash;
        bytes32 allegationHash;
        CaseStatus status;
        Resolution resolution;
        string metadataURI;
        uint256 createdAt;
        uint256 resolvedAt;
    }

    IAEPEvaluatorStakingRegistry public immutable evaluatorStaking;
    uint256 public nextCaseId = 1;
    mapping(uint256 => SlashingCase) public cases;

    event SlashingCaseOpened(uint256 indexed caseId, address indexed respondent, uint256 requestedSlashAmount, bytes32 evidenceHash, bytes32 allegationHash);
    event SlashingCaseResolved(uint256 indexed caseId, Resolution resolution, uint256 slashAmount, bytes32 reasonHash);
    event SlashingCaseCancelled(uint256 indexed caseId, bytes32 reasonHash);

    constructor(address admin, address evaluatorStaking_) GoalOSAccessControl(admin) {
        require(evaluatorStaking_ != address(0), "SLASH_ZERO_STAKING");
        evaluatorStaking = IAEPEvaluatorStakingRegistry(evaluatorStaking_);
    }

    function openCase(address respondent, uint256 requestedSlashAmount, bytes32 evidenceHash, bytes32 allegationHash, string calldata metadataURI) external onlyOperator returns (uint256 caseId) {
        require(respondent != address(0), "SLASH_ZERO_RESPONDENT");
        require(evidenceHash != bytes32(0), "SLASH_ZERO_EVIDENCE");
        require(allegationHash != bytes32(0), "SLASH_ZERO_ALLEGATION");
        caseId = nextCaseId++;
        cases[caseId] = SlashingCase(respondent, requestedSlashAmount, evidenceHash, allegationHash, CaseStatus.Open, Resolution.None, metadataURI, block.timestamp, 0);
        emit SlashingCaseOpened(caseId, respondent, requestedSlashAmount, evidenceHash, allegationHash);
    }

    function resolveCase(uint256 caseId, Resolution resolution, uint256 slashAmount, bytes32 reasonHash) external onlyOperator {
        SlashingCase storage c = cases[caseId];
        require(c.status == CaseStatus.Open, "SLASH_NOT_OPEN");
        require(resolution != Resolution.None, "SLASH_BAD_RESOLUTION");
        c.status = CaseStatus.Resolved;
        c.resolution = resolution;
        c.resolvedAt = block.timestamp;
        if (resolution == Resolution.Slash) {
            require(slashAmount > 0 && slashAmount <= c.requestedSlashAmount, "SLASH_BAD_AMOUNT");
            evaluatorStaking.slashEvaluator(c.respondent, slashAmount, reasonHash);
        }
        emit SlashingCaseResolved(caseId, resolution, slashAmount, reasonHash);
    }

    function cancelCase(uint256 caseId, bytes32 reasonHash) external onlyOperator {
        SlashingCase storage c = cases[caseId];
        require(c.status == CaseStatus.Open, "SLASH_NOT_OPEN");
        c.status = CaseStatus.Cancelled;
        emit SlashingCaseCancelled(caseId, reasonHash);
    }
}
