// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../access/GoalOSAccessControl.sol";

contract TokenReserveVault is GoalOSAccessControl {
    using SafeERC20 for IERC20;

    IERC20 public immutable token;
    string public purpose;

    event VaultRelease(address indexed recipient, uint256 amount, bytes32 indexed reasonHash, string memo);
    event PurposeUpdated(string purpose);

    constructor(address admin, address token_, string memory purpose_) GoalOSAccessControl(admin) {
        require(token_ != address(0), "VAULT_ZERO_TOKEN");
        token = IERC20(token_);
        purpose = purpose_;
    }

    function setPurpose(string calldata purpose_) external onlyAdmin {
        purpose = purpose_;
        emit PurposeUpdated(purpose_);
    }

    function release(address recipient, uint256 amount, bytes32 reasonHash, string calldata memo) external whenNotPaused {
        require(hasRole(VAULT_MANAGER_ROLE, msg.sender) || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "VAULT_NOT_MANAGER");
        require(recipient != address(0), "VAULT_ZERO_RECIPIENT");
        require(reasonHash != bytes32(0), "VAULT_ZERO_REASON");
        token.safeTransfer(recipient, amount);
        emit VaultRelease(recipient, amount, reasonHash, memo);
    }
}
