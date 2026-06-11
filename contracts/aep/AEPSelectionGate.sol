// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPSelectionGate is GoalOSAccessControl {
    enum SelectionDecision { None, Reject, Canary, Promote, Pause, Rollback }
    struct SelectionCertificate {
        uint256 proofId;
        bytes32 artifactId;
        bytes32 candidateVersionHash;
        SelectionDecision decision;
        bytes32 scopeHash;
        bytes32 canaryHash;
        bytes32 rollbackTargetHash;
        uint256 challengeWindowEnd;
        uint256 gateBitmap;
        string metadataURI;
        address signer;
        uint256 createdAt;
    }
    uint256 public constant GATE_PROOF_VALID = 1 << 0;
    uint256 public constant GATE_EVAL_PASS = 1 << 1;
    uint256 public constant GATE_RISK_OK = 1 << 2;
    uint256 public constant GATE_ROLLBACK_READY = 1 << 3;
    uint256 public constant GATE_CANARY_READY = 1 << 4;
    uint256 public constant GATE_SCOPE_AUTHORIZED = 1 << 5;
    uint256 public constant GATE_CHALLENGE_CLEARED = 1 << 6;
    uint256 public nextSelectionId = 1;
    mapping(uint256 => SelectionCertificate) public selections;
    event SelectionCertified(uint256 indexed selectionId, uint256 indexed proofId, bytes32 indexed artifactId, SelectionDecision decision, uint256 gateBitmap, string metadataURI);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function issueSelectionCertificate(uint256 proofId, bytes32 artifactId, bytes32 candidateVersionHash, SelectionDecision decision, bytes32 scopeHash, bytes32 canaryHash, bytes32 rollbackTargetHash, uint256 challengeWindowEnd, uint256 gateBitmap, string calldata metadataURI) external onlyOperator returns (uint256 selectionId) {
        require(proofId != 0, "AEP_SEL_ZERO_PROOF");
        require(artifactId != bytes32(0), "AEP_SEL_ZERO_ARTIFACT");
        require(candidateVersionHash != bytes32(0), "AEP_SEL_ZERO_VERSION");
        require(decision != SelectionDecision.None, "AEP_SEL_BAD_DECISION");
        selectionId = nextSelectionId++;
        selections[selectionId] = SelectionCertificate(proofId, artifactId, candidateVersionHash, decision, scopeHash, canaryHash, rollbackTargetHash, challengeWindowEnd, gateBitmap, metadataURI, msg.sender, block.timestamp);
        emit SelectionCertified(selectionId, proofId, artifactId, decision, gateBitmap, metadataURI);
    }
}
