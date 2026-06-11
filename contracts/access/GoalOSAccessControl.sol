// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

abstract contract GoalOSAccessControl is AccessControl, Pausable {
    bytes32 public constant PROTOCOL_ADMIN_ROLE = keccak256("PROTOCOL_ADMIN_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    bytes32 public constant REVIEWER_MANAGER_ROLE = keccak256("REVIEWER_MANAGER_ROLE");
    bytes32 public constant TREASURY_ROLE = keccak256("TREASURY_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant VAULT_MANAGER_ROLE = keccak256("VAULT_MANAGER_ROLE");

    constructor(address admin) {
        require(admin != address(0), "GOALOS_ZERO_ADMIN");
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(PROTOCOL_ADMIN_ROLE, admin);
        _grantRole(OPERATOR_ROLE, admin);
        _grantRole(REVIEWER_MANAGER_ROLE, admin);
        _grantRole(TREASURY_ROLE, admin);
        _grantRole(PAUSER_ROLE, admin);
        _grantRole(VAULT_MANAGER_ROLE, admin);
    }

    modifier onlyAdmin() {
        require(
            hasRole(DEFAULT_ADMIN_ROLE, msg.sender) || hasRole(PROTOCOL_ADMIN_ROLE, msg.sender),
            "GOALOS_NOT_ADMIN"
        );
        _;
    }

    modifier onlyOperator() {
        require(
            hasRole(DEFAULT_ADMIN_ROLE, msg.sender) || hasRole(OPERATOR_ROLE, msg.sender),
            "GOALOS_NOT_OPERATOR"
        );
        _;
    }

    function pause() external {
        require(hasRole(PAUSER_ROLE, msg.sender) || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "GOALOS_NOT_PAUSER");
        _pause();
    }

    function unpause() external {
        require(hasRole(PAUSER_ROLE, msg.sender) || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "GOALOS_NOT_PAUSER");
        _unpause();
    }
}
