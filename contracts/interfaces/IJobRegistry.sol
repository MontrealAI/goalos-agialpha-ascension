// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IJobRegistry {
    enum JobStatus {
        None,
        Open,
        Claimed,
        Submitted,
        Approved,
        Rejected,
        Cancelled,
        Expired
    }

    function statusOf(uint256 jobId) external view returns (JobStatus);
    function assigneeOf(uint256 jobId) external view returns (address);
    function sponsorOf(uint256 jobId) external view returns (address);
    function deadlineOf(uint256 jobId) external view returns (uint256);

    function markClaimed(uint256 jobId, address builder) external;
    function markSubmitted(uint256 jobId, uint256 submissionId) external;
    function markApproved(uint256 jobId) external;
    function markRejected(uint256 jobId, bytes32 reasonHash) external;
    function releaseReward(uint256 jobId, address builder) external;

    function refundRejectedReward(uint256 jobId, bytes32 reasonHash) external;
    function expireClaimedJob(uint256 jobId, bytes32 reasonHash) external;
}
