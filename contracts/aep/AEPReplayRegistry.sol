// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPReplayRegistry is GoalOSAccessControl {
    enum ReplayVerdict { None, Pass, Fail, Inconclusive, Escalate }
    struct ReplayRecord {
        uint256 proofBundleId;
        bytes32 replayHash;
        bytes32 containerDigestHash;
        bytes32 dependencyPinsHash;
        bytes32 replayResultHash;
        ReplayVerdict verdict;
        string metadataURI;
        address replayer;
        uint256 createdAt;
    }

    uint256 public nextReplayId = 1;
    mapping(uint256 => ReplayRecord) public replays;

    event ReplayRecorded(uint256 indexed replayId, uint256 indexed proofBundleId, ReplayVerdict verdict, bytes32 replayHash, bytes32 replayResultHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function recordReplay(
        uint256 proofBundleId,
        bytes32 replayHash,
        bytes32 containerDigestHash,
        bytes32 dependencyPinsHash,
        bytes32 replayResultHash,
        ReplayVerdict verdict,
        string calldata metadataURI
    ) external onlyOperator returns (uint256 replayId) {
        require(proofBundleId != 0, "AEP_REPLAY_ZERO_BUNDLE");
        require(replayHash != bytes32(0), "AEP_REPLAY_ZERO_HASH");
        require(verdict != ReplayVerdict.None, "AEP_REPLAY_BAD_VERDICT");
        replayId = nextReplayId++;
        replays[replayId] = ReplayRecord(proofBundleId, replayHash, containerDigestHash, dependencyPinsHash, replayResultHash, verdict, metadataURI, msg.sender, block.timestamp);
        emit ReplayRecorded(replayId, proofBundleId, verdict, replayHash, replayResultHash);
    }
}
