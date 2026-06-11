// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract ProtocolConfigRegistry is GoalOSAccessControl {
    struct ConfigRecord {
        bytes32 valueHash;
        string uri;
        uint256 updatedAt;
        address updatedBy;
    }

    mapping(bytes32 => ConfigRecord) public configOf;

    event ConfigUpdated(bytes32 indexed key, bytes32 indexed valueHash, string uri, address indexed updatedBy);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function setConfig(bytes32 key, bytes32 valueHash, string calldata uri) external onlyOperator {
        require(key != bytes32(0), "CONFIG_ZERO_KEY");
        require(valueHash != bytes32(0), "CONFIG_ZERO_VALUE");
        configOf[key] = ConfigRecord(valueHash, uri, block.timestamp, msg.sender);
        emit ConfigUpdated(key, valueHash, uri, msg.sender);
    }

    function getConfig(bytes32 key) external view returns (bytes32 valueHash, string memory uri, uint256 updatedAt, address updatedBy) {
        ConfigRecord memory record = configOf[key];
        return (record.valueHash, record.uri, record.updatedAt, record.updatedBy);
    }
}
