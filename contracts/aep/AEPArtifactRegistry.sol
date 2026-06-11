// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPArtifactRegistry is GoalOSAccessControl {
    enum ArtifactStatus { None, Draft, Candidate, Canary, Active, Rejected, RolledBack, Deprecated }
    struct ArtifactVersion {
        bytes32 artifactId;
        bytes32 versionHash;
        bytes32 artifactClass;
        bytes32 scopeHash;
        bytes32 rollbackTargetHash;
        ArtifactStatus status;
        string metadataURI;
        address author;
        uint256 createdAt;
    }

    uint256 public nextVersionId = 1;
    mapping(uint256 => ArtifactVersion) public versions;
    mapping(bytes32 => uint256[]) private versionsByArtifact;

    event ArtifactVersionRegistered(uint256 indexed versionId, bytes32 indexed artifactId, bytes32 indexed versionHash, bytes32 artifactClass, ArtifactStatus status, string metadataURI);
    event ArtifactStatusUpdated(uint256 indexed versionId, ArtifactStatus status, bytes32 indexed reasonHash);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function registerArtifactVersion(bytes32 artifactId, bytes32 versionHash, bytes32 artifactClass, bytes32 scopeHash, bytes32 rollbackTargetHash, string calldata metadataURI) external onlyOperator returns (uint256 versionId) {
        require(artifactId != bytes32(0), "AEP_ART_ZERO_ID");
        require(versionHash != bytes32(0), "AEP_ART_ZERO_VERSION");
        versionId = nextVersionId++;
        versions[versionId] = ArtifactVersion(artifactId, versionHash, artifactClass, scopeHash, rollbackTargetHash, ArtifactStatus.Candidate, metadataURI, msg.sender, block.timestamp);
        versionsByArtifact[artifactId].push(versionId);
        emit ArtifactVersionRegistered(versionId, artifactId, versionHash, artifactClass, ArtifactStatus.Candidate, metadataURI);
    }

    function setArtifactStatus(uint256 versionId, ArtifactStatus status, bytes32 reasonHash) external onlyOperator {
        require(versions[versionId].versionHash != bytes32(0), "AEP_ART_NOT_FOUND");
        versions[versionId].status = status;
        emit ArtifactStatusUpdated(versionId, status, reasonHash);
    }

    function versionIdsOf(bytes32 artifactId) external view returns (uint256[] memory) { return versionsByArtifact[artifactId]; }
}
