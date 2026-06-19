// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @dev Local Hardhat-only Safe-compatible fixture for fork rehearsals. Not used in production deployments.
contract LocalSafeFixture {
    address internal constant SENTINEL_MODULES = address(0x1);
    address[] private _owners;
    mapping(address => bool) private _isOwner;
    uint256 private _threshold;

    constructor(address[] memory owners_, uint256 threshold_) {
        require(owners_.length >= threshold_ && threshold_ > 0, "invalid threshold");
        for (uint256 i = 0; i < owners_.length; i++) {
            require(owners_[i] != address(0) && !_isOwner[owners_[i]], "invalid owner");
            _owners.push(owners_[i]);
            _isOwner[owners_[i]] = true;
        }
        _threshold = threshold_;
    }

    function getOwners() external view returns (address[] memory) {
        return _owners;
    }

    function getThreshold() external view returns (uint256) {
        return _threshold;
    }

    function isOwner(address owner) external view returns (bool) {
        return _isOwner[owner];
    }

    function getModulesPaginated(address start, uint256 pageSize) external pure returns (address[] memory modules, address next) {
        require(start == SENTINEL_MODULES || start == address(0), "unsupported start");
        pageSize;
        modules = new address[](0);
        next = SENTINEL_MODULES;
    }
}
