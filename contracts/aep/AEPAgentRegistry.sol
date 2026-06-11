// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract AEPAgentRegistry is GoalOSAccessControl {
    enum AgentRole { None, Agent, Node, Validator, Club, Operator, Business }
    struct AgentIdentity {
        address account;
        bytes32 ensNodeHash;
        AgentRole role;
        bytes32 credentialRoot;
        bytes32 reputationRoot;
        string metadataURI;
        bool active;
        uint256 createdAt;
    }

    uint256 public nextAgentId = 1;
    mapping(uint256 => AgentIdentity) public agents;
    mapping(address => uint256) public agentIdOf;

    event AgentRegistered(uint256 indexed agentId, address indexed account, bytes32 indexed ensNodeHash, AgentRole role, string metadataURI);
    event AgentUpdated(uint256 indexed agentId, bytes32 credentialRoot, bytes32 reputationRoot, bool active, string metadataURI);

    constructor(address admin) GoalOSAccessControl(admin) {}

    function registerAgent(address account, bytes32 ensNodeHash, AgentRole role, bytes32 credentialRoot, bytes32 reputationRoot, string calldata metadataURI) external onlyOperator returns (uint256 agentId) {
        require(account != address(0), "AEP_AGENT_ZERO_ACCOUNT");
        require(role != AgentRole.None, "AEP_AGENT_BAD_ROLE");
        require(agentIdOf[account] == 0, "AEP_AGENT_EXISTS");
        agentId = nextAgentId++;
        agents[agentId] = AgentIdentity(account, ensNodeHash, role, credentialRoot, reputationRoot, metadataURI, true, block.timestamp);
        agentIdOf[account] = agentId;
        emit AgentRegistered(agentId, account, ensNodeHash, role, metadataURI);
    }

    function updateAgent(uint256 agentId, bytes32 credentialRoot, bytes32 reputationRoot, bool active, string calldata metadataURI) external onlyOperator {
        require(agents[agentId].account != address(0), "AEP_AGENT_NOT_FOUND");
        AgentIdentity storage a = agents[agentId];
        a.credentialRoot = credentialRoot;
        a.reputationRoot = reputationRoot;
        a.active = active;
        a.metadataURI = metadataURI;
        emit AgentUpdated(agentId, credentialRoot, reputationRoot, active, metadataURI);
    }
}
