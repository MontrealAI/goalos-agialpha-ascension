// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../access/GoalOSAccessControl.sol";

contract TreasuryRouter is GoalOSAccessControl {
    using SafeERC20 for IERC20;

    address public treasury;

    event TreasuryUpdated(address indexed treasury);
    event TokensRouted(address indexed token, address indexed from, address indexed to, uint256 amount, bytes32 reasonHash);

    constructor(address admin, address treasury_) GoalOSAccessControl(admin) {
        require(treasury_ != address(0), "TREASURY_ZERO");
        treasury = treasury_;
        emit TreasuryUpdated(treasury_);
    }

    function setTreasury(address treasury_) external onlyAdmin {
        require(treasury_ != address(0), "TREASURY_ZERO");
        treasury = treasury_;
        emit TreasuryUpdated(treasury_);
    }

    function routeFrom(address token, address from, uint256 amount, bytes32 reasonHash) external onlyOperator {
        IERC20(token).safeTransferFrom(from, treasury, amount);
        emit TokensRouted(token, from, treasury, amount, reasonHash);
    }

    function routeHeld(address token, uint256 amount, bytes32 reasonHash) external onlyOperator {
        IERC20(token).safeTransfer(treasury, amount);
        emit TokensRouted(token, address(this), treasury, amount, reasonHash);
    }
}
