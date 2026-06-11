import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import { getOptionalPrivateKey, getOptionalRpcUrl } from "./scripts/config/networkConfig";

const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";
const MAINNET_FORK_RPC_URL = getOptionalRpcUrl("ethereumMainnet");
const ENABLE_MAINNET_FORK = process.env.HARDHAT_FORK_MAINNET === "1" && Boolean(MAINNET_FORK_RPC_URL);

function accounts(networkName: string): string[] | "remote" {
  const key = getOptionalPrivateKey(networkName);
  return key ? [key] : "remote";
}

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: { enabled: true, runs: 200 },
      viaIR: false
    }
  },
  networks: {
    hardhat: { chainId: ENABLE_MAINNET_FORK ? 1 : 31337, forking: ENABLE_MAINNET_FORK && MAINNET_FORK_RPC_URL ? { url: MAINNET_FORK_RPC_URL } : undefined },
    localhost: { url: getOptionalRpcUrl("localhost") || "http://127.0.0.1:8545", chainId: 31337, accounts: accounts("localhost") },
    sepolia: { url: getOptionalRpcUrl("ethereumSepolia") || "http://127.0.0.1:8545", accounts: accounts("ethereumSepolia"), chainId: 11155111 },
    mainnet: { url: getOptionalRpcUrl("ethereumMainnet") || "http://127.0.0.1:8545", accounts: accounts("ethereumMainnet"), chainId: 1 },
    ethereumSepolia: { url: getOptionalRpcUrl("ethereumSepolia") || "http://127.0.0.1:8545", accounts: accounts("ethereumSepolia"), chainId: 11155111 },
    ethereumMainnet: { url: getOptionalRpcUrl("ethereumMainnet") || "http://127.0.0.1:8545", accounts: accounts("ethereumMainnet"), chainId: 1 }
  },
  etherscan: {
    apiKey: {
      mainnet: ETHERSCAN_API_KEY,
      sepolia: ETHERSCAN_API_KEY
    }
  }
};

export default config;
