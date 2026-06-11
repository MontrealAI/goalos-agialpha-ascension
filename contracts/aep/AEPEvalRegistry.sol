// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPEvalRegistry is GoalOSAccessControl {
    enum EvalVerdict { None, Pass, Fail, Escalate }
    struct EvalSchema { bytes32 schemaHash; string metadataURI; uint256 challengeWindow; bool active; uint256 createdAt; }
    struct EvalAttestation { uint256 proofId; uint256 schemaId; bytes32 baselineHash; bytes32 candidateHash; EvalVerdict verdict; bytes32 resultHash; address evaluator; uint256 createdAt; }

    uint256 public nextSchemaId = 1;
    uint256 public nextEvalId = 1;
    mapping(uint256 => EvalSchema) public schemas;
    mapping(uint256 => EvalAttestation) public evals;

    event EvalSchemaRegistered(uint256 indexed schemaId, bytes32 indexed schemaHash, string metadataURI, uint256 challengeWindow);
    event EvalRecorded(uint256 indexed evalId, uint256 indexed proofId, uint256 indexed schemaId, EvalVerdict verdict, bytes32 resultHash, address evaluator);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function registerEvalSchema(bytes32 schemaHash, string calldata metadataURI, uint256 challengeWindow) external onlyOperator returns (uint256 schemaId) {
        require(schemaHash != bytes32(0), "AEP_EVAL_ZERO_SCHEMA");
        schemaId = nextSchemaId++;
        schemas[schemaId] = EvalSchema(schemaHash, metadataURI, challengeWindow, true, block.timestamp);
        emit EvalSchemaRegistered(schemaId, schemaHash, metadataURI, challengeWindow);
    }

    function recordEval(uint256 proofId, uint256 schemaId, bytes32 baselineHash, bytes32 candidateHash, EvalVerdict verdict, bytes32 resultHash) external onlyOperator returns (uint256 evalId) {
        require(proofId != 0, "AEP_EVAL_ZERO_PROOF");
        require(schemas[schemaId].active, "AEP_EVAL_SCHEMA_INACTIVE");
        require(verdict != EvalVerdict.None, "AEP_EVAL_BAD_VERDICT");
        evalId = nextEvalId++;
        evals[evalId] = EvalAttestation(proofId, schemaId, baselineHash, candidateHash, verdict, resultHash, msg.sender, block.timestamp);
        emit EvalRecorded(evalId, proofId, schemaId, verdict, resultHash, msg.sender);
    }
}
