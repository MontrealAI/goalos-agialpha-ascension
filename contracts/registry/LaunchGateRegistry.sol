// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../access/GoalOSAccessControl.sol";

contract LaunchGateRegistry is GoalOSAccessControl {
    struct Gate { bool passed; bytes32 evidenceHash; string evidenceURI; uint256 updatedAt; address reviewer; }
    bytes32 public constant LEGAL_REVIEW = keccak256("LEGAL_REVIEW");
    bytes32 public constant TAX_REVIEW = keccak256("TAX_REVIEW");
    bytes32 public constant SECURITY_REVIEW = keccak256("SECURITY_REVIEW");
    bytes32 public constant PUBLIC_CLAIMS_REVIEW = keccak256("PUBLIC_CLAIMS_REVIEW");
    bytes32 public constant TREASURY_REVIEW = keccak256("TREASURY_REVIEW");
    bytes32 public constant AGIALPHA_TOKEN_VERIFICATION = keccak256("AGIALPHA_TOKEN_VERIFICATION");
    bytes32 public constant ETHEREUM_SEPOLIA_REHEARSAL = keccak256("ETHEREUM_SEPOLIA_REHEARSAL");
    bytes32 public constant EXTERNAL_AUDIT_CLOSURE = keccak256("EXTERNAL_AUDIT_CLOSURE");
    bytes32 public constant FOUNDER_APPROVAL = keccak256("FOUNDER_APPROVAL");
    mapping(bytes32 => Gate) public gateOf;
    event LaunchGateUpdated(bytes32 indexed gateId, bool passed, bytes32 indexed evidenceHash, string evidenceURI, address indexed reviewer);
    constructor(address admin) GoalOSAccessControl(admin) {}
    function setGate(bytes32 gateId, bool passed, bytes32 evidenceHash, string calldata evidenceURI) external onlyOperator {
        require(gateId != bytes32(0), "GATE_ZERO_ID"); require(evidenceHash != bytes32(0), "GATE_ZERO_EVIDENCE");
        gateOf[gateId] = Gate(passed, evidenceHash, evidenceURI, block.timestamp, msg.sender);
        emit LaunchGateUpdated(gateId, passed, evidenceHash, evidenceURI, msg.sender);
    }
    function allCoreGatesPassed() external view returns (bool) {
        return gateOf[LEGAL_REVIEW].passed && gateOf[TAX_REVIEW].passed && gateOf[SECURITY_REVIEW].passed && gateOf[PUBLIC_CLAIMS_REVIEW].passed && gateOf[TREASURY_REVIEW].passed && gateOf[AGIALPHA_TOKEN_VERIFICATION].passed && gateOf[ETHEREUM_SEPOLIA_REHEARSAL].passed && gateOf[EXTERNAL_AUDIT_CLOSURE].passed && gateOf[FOUNDER_APPROVAL].passed;
    }
}
