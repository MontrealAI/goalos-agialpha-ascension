// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AlphaWorkUnitLedger is GoalOSAccessControl {
    struct AlphaWURecord { address worker; uint256 proofBundleId; uint256 alphaWorkUnits; bytes32 metrologyHash; uint16 qualityBps; uint16 sloBps; uint16 confidenceBps; bytes32 policyHash; uint256 createdAt; }
    uint256 public nextRecordId = 1;
    mapping(uint256 => AlphaWURecord) public records;
    mapping(address => uint256) public totalAlphaWUByWorker;
    event AlphaWorkUnitsRecorded(uint256 indexed recordId, address indexed worker, uint256 indexed proofBundleId, uint256 alphaWorkUnits, bytes32 metrologyHash);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function recordAlphaWorkUnits(address worker, uint256 proofBundleId, uint256 alphaWorkUnits, bytes32 metrologyHash, uint16 qualityBps, uint16 sloBps, uint16 confidenceBps, bytes32 policyHash) external onlyOperator returns (uint256 recordId) {
        require(worker != address(0), "AWU_ZERO_WORKER");
        require(alphaWorkUnits > 0, "AWU_ZERO_AMOUNT");
        recordId = nextRecordId++;
        records[recordId] = AlphaWURecord(worker, proofBundleId, alphaWorkUnits, metrologyHash, qualityBps, sloBps, confidenceBps, policyHash, block.timestamp);
        totalAlphaWUByWorker[worker] += alphaWorkUnits;
        emit AlphaWorkUnitsRecorded(recordId, worker, proofBundleId, alphaWorkUnits, metrologyHash);
    }
}
