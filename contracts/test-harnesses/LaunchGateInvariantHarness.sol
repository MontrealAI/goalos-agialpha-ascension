// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {LaunchGateRegistry} from "../registry/LaunchGateRegistry.sol";

/// @title Launch Gate Invariant Harness
/// @author Montreal AI / GoalOS contributors
/// @notice Test-only harness exposing the canonical launch gate set for invariant checks.
/// @dev This contract is never used by deployment scripts and must not be included in Ethereum Mainnet manifests.
contract LaunchGateInvariantHarness is LaunchGateRegistry {
    /// @notice Deploys the harness with the supplied admin.
    /// @param admin Address that receives the default admin/operator roles for tests.
    constructor(address admin) LaunchGateRegistry(admin) {}

    /// @notice Returns the exact core gate IDs required before launch authorization can pass.
    /// @return gateIds Ordered list of canonical core launch-gate identifiers.
    function requiredCoreGateIds() external pure returns (bytes32[] memory gateIds) {
        gateIds = new bytes32[](10);
        gateIds[0] = keccak256("LEGAL_REVIEW");
        gateIds[1] = keccak256("TAX_REVIEW");
        gateIds[2] = keccak256("SECURITY_REVIEW");
        gateIds[3] = keccak256("PUBLIC_CLAIMS_REVIEW");
        gateIds[4] = keccak256("TREASURY_REVIEW");
        gateIds[5] = keccak256("AGIALPHA_TOKEN_VERIFICATION");
        gateIds[6] = keccak256("ETHEREUM_SEPOLIA_REHEARSAL");
        gateIds[7] = keccak256("AUTOMATED_SECURITY_TOOLCHAIN");
        gateIds[8] = keccak256("INTERNAL_SECURITY_REVIEW");
        gateIds[9] = keccak256("FOUNDER_APPROVAL");
    }
}
