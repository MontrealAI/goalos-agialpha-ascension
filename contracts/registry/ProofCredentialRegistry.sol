// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "../access/GoalOSAccessControl.sol";

interface IERC5192 {
    event Locked(uint256 tokenId);
    event Unlocked(uint256 tokenId);
    function locked(uint256 tokenId) external view returns (bool);
}

contract ProofCredentialRegistry is ERC721, IERC5192, GoalOSAccessControl {
    struct Credential {
        uint256 proofCardId;
        bytes32 proofCardHash;
        bytes32 credentialType;
        string metadataURI;
        uint256 issuedAt;
        bool revoked;
    }

    uint256 public nextTokenId = 1;
    mapping(uint256 => Credential) public credentials;

    event ProofCredentialIssued(
        uint256 indexed tokenId,
        address indexed account,
        uint256 indexed proofCardId,
        bytes32 proofCardHash,
        bytes32 credentialType,
        string metadataURI
    );
    event ProofCredentialRevoked(uint256 indexed tokenId, bytes32 indexed reasonHash);

    constructor(address admin) ERC721("GoalOS Proof Credential", "GOPC") GoalOSAccessControl(admin) {}

    function issueCredential(
        address to,
        uint256 proofCardId,
        bytes32 proofCardHash,
        bytes32 credentialType,
        string calldata metadataURI
    ) external onlyOperator returns (uint256 tokenId) {
        require(to != address(0), "CRED_ZERO_TO");
        tokenId = nextTokenId++;
        _safeMint(to, tokenId);
        credentials[tokenId] = Credential(proofCardId, proofCardHash, credentialType, metadataURI, block.timestamp, false);
        emit ProofCredentialIssued(tokenId, to, proofCardId, proofCardHash, credentialType, metadataURI);
        emit Locked(tokenId);
    }

    function revokeCredential(uint256 tokenId, bytes32 reasonHash) external onlyOperator {
        require(_exists(tokenId), "CRED_NOT_FOUND");
        credentials[tokenId].revoked = true;
        emit ProofCredentialRevoked(tokenId, reasonHash);
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "CRED_NOT_FOUND");
        return credentials[tokenId].metadataURI;
    }

    function locked(uint256 tokenId) external view override returns (bool) {
        require(_exists(tokenId), "CRED_NOT_FOUND");
        return true;
    }

    function _beforeTokenTransfer(address from, address to, uint256 tokenId, uint256 batchSize) internal override {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
        require(from == address(0) || to == address(0), "CRED_SOULBOUND");
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, GoalOSAccessControl)
        returns (bool)
    {
        return interfaceId == type(IERC5192).interfaceId || super.supportsInterface(interfaceId);
    }
}
