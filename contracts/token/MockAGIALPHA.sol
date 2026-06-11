// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

contract MockAGIALPHA is ERC20Permit {
    uint256 public constant INITIAL_SUPPLY = 1_000_000_000 ether;

    constructor(address receiver) ERC20("Mock AGI ALPHA AGENT", "mAGIALPHA") ERC20Permit("Mock AGI ALPHA AGENT") {
        require(receiver != address(0), "MOCK_ZERO_RECEIVER");
        _mint(receiver, INITIAL_SUPPLY);
    }
}
