// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPProofLedger is GoalOSAccessControl {
    struct ProofRoot {
        uint256 runId;
        bytes32 proofHash;
        bytes32 evidenceRoot;
        bytes32 evalRoot;
        uint256 cost;
        uint256 latency;
        bytes32 signatureBundleHash;
        string evidenceURI;
        address submitter;
        uint256 createdAt;
    }

    uint256 public nextProofId = 1;
    mapping(uint256 => ProofRoot) public proofs;
    event ProofRootAppended(uint256 indexed proofId, uint256 indexed runId, bytes32 indexed proofHash, bytes32 evidenceRoot, bytes32 evalRoot, string evidenceURI);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function appendProofRoot(uint256 runId, bytes32 proofHash, bytes32 evidenceRoot, bytes32 evalRoot, uint256 cost, uint256 latency, bytes32 signatureBundleHash, string calldata evidenceURI) external onlyOperator returns (uint256 proofId) {
        require(runId != 0, "AEP_PROOF_ZERO_RUN");
        require(proofHash != bytes32(0), "AEP_PROOF_ZERO_HASH");
        proofId = nextProofId++;
        proofs[proofId] = ProofRoot(runId, proofHash, evidenceRoot, evalRoot, cost, latency, signatureBundleHash, evidenceURI, msg.sender, block.timestamp);
        emit ProofRootAppended(proofId, runId, proofHash, evidenceRoot, evalRoot, evidenceURI);
    }
}
