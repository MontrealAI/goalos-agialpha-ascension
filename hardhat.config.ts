import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const PRIVATE_KEY = process.env.PRIVATE_KEY || "";
const ETHEREUM_SEPOLIA_RPC_URL = process.env.ETHEREUM_SEPOLIA_RPC_URL || "http://127.0.0.1:8545";
const ETHEREUM_MAINNET_RPC_URL = process.env.ETHEREUM_MAINNET_RPC_URL || "http://127.0.0.1:8545";
const MAINNET_FORK_RPC_URL = process.env.MAINNET_RPC_URL || process.env.ETHEREUM_MAINNET_RPC_URL || "";
const ENABLE_MAINNET_FORK = process.env.HARDHAT_FORK_MAINNET === "1" && Boolean(MAINNET_FORK_RPC_URL);
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";
const accounts = PRIVATE_KEY ? [PRIVATE_KEY] : [];

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: { enabled: true, runs: 200 },
      viaIR: false
    }
  },
  networks: {
    hardhat: { chainId: ENABLE_MAINNET_FORK ? 1 : 11155111, forking: ENABLE_MAINNET_FORK ? { url: MAINNET_FORK_RPC_URL } : undefined },
    sepolia: { url: ETHEREUM_SEPOLIA_RPC_URL, accounts: accounts.length ? accounts : "remote", chainId: 11155111 },
    mainnet: { url: ETHEREUM_MAINNET_RPC_URL, accounts: accounts.length ? accounts : "remote", chainId: 1 }
  },
  etherscan: {
    apiKey: {
      mainnet: ETHERSCAN_API_KEY,
      sepolia: ETHERSCAN_API_KEY
    }
  }
};

export default config;
