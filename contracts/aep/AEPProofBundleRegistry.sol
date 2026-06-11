// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPProofBundleRegistry is GoalOSAccessControl {
    struct ProofBundle { uint256 jobId; uint256 runId; bytes32 proofBundleHash; bytes32 replayResultHash; bytes32 validatorCommitmentRoot; bytes32 validatorRevealRoot; bytes32 settlementReceiptHash; uint256 alphaWorkUnits; string metadataURI; address submitter; uint256 createdAt; }
    uint256 public nextBundleId = 1;
    mapping(uint256 => ProofBundle) public bundles;
    event ProofBundleRegistered(uint256 indexed bundleId, uint256 indexed jobId, uint256 indexed runId, bytes32 proofBundleHash, uint256 alphaWorkUnits, string metadataURI);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function registerProofBundle(uint256 jobId, uint256 runId, bytes32 proofBundleHash, bytes32 replayResultHash, bytes32 validatorCommitmentRoot, bytes32 validatorRevealRoot, bytes32 settlementReceiptHash, uint256 alphaWorkUnits, string calldata metadataURI) external onlyOperator returns (uint256 bundleId) {
        require(proofBundleHash != bytes32(0), "AEP_BUNDLE_ZERO_HASH");
        bundleId = nextBundleId++;
        bundles[bundleId] = ProofBundle(jobId, runId, proofBundleHash, replayResultHash, validatorCommitmentRoot, validatorRevealRoot, settlementReceiptHash, alphaWorkUnits, metadataURI, msg.sender, block.timestamp);
        emit ProofBundleRegistered(bundleId, jobId, runId, proofBundleHash, alphaWorkUnits, metadataURI);
    }
}
