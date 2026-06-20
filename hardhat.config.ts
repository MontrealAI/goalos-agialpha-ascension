import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "@nomicfoundation/hardhat-ledger";
import { loadDeploymentEnv } from "./scripts/config/loadEnv";
loadDeploymentEnv();
if (process.env.HARDHAT_FORK_MAINNET === "1") loadDeploymentEnv("ethereumMainnet");
import { getOptionalLedgerAddress, getOptionalPrivateKey, getOptionalRpcUrl } from "./scripts/config/networkConfig";

const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";
const MAINNET_FORK_RPC_URL = getOptionalRpcUrl("ethereumMainnet") || process.env.PUBLIC_ETHEREUM_MAINNET_RPC_URL;
const ENABLE_MAINNET_FORK = process.env.HARDHAT_FORK_MAINNET === "1" && Boolean(MAINNET_FORK_RPC_URL);
function requireRemoteUrlWhenSelected(networkName: string, envName: string): string {
  const selected = process.argv.includes("--network") && process.argv[process.argv.indexOf("--network") + 1] === networkName;
  const url = getOptionalRpcUrl(envName);
  if (selected && !url) {
    throw new Error(`Missing RPC URL for ${networkName}. Create .private/${envName === "ethereumMainnet" ? "mainnet" : "sepolia"}-operator.env or set the documented PRIVATE_*_RPC_URL locally. GoalOS refuses localhost fallback for named remote networks.`);
  }
  return url || `http://goalos-missing-rpc.invalid/${networkName}`;
}

function accounts(networkName: string): string[] | "remote" {
  const key = getOptionalPrivateKey(networkName);
  return key ? [key] : "remote";
}
function ledgerAccounts(networkName: string): string[] {
  const address = getOptionalLedgerAddress(networkName);
  return address ? [address] : [];
}

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.28",
    settings: {
      optimizer: { enabled: true, runs: 200 },
      viaIR: false
    }
  },
  networks: {
    hardhat: { chainId: ENABLE_MAINNET_FORK ? 1 : 31337, forking: ENABLE_MAINNET_FORK && MAINNET_FORK_RPC_URL ? { url: MAINNET_FORK_RPC_URL } : undefined },
    localhost: { url: getOptionalRpcUrl("localhost") || "http://127.0.0.1:8545", chainId: 31337, accounts: accounts("localhost") },
    sepolia: { url: requireRemoteUrlWhenSelected("sepolia", "ethereumSepolia"), accounts: accounts("ethereumSepolia"), chainId: 11155111 },
    mainnet: { url: requireRemoteUrlWhenSelected("mainnet", "ethereumMainnet"), accounts: accounts("ethereumMainnet"), ledgerAccounts: ledgerAccounts("ethereumMainnet"), chainId: 1 } as any,
    ethereumSepolia: { url: requireRemoteUrlWhenSelected("ethereumSepolia", "ethereumSepolia"), accounts: accounts("ethereumSepolia"), chainId: 11155111 },
    ethereumMainnet: { url: requireRemoteUrlWhenSelected("ethereumMainnet", "ethereumMainnet"), accounts: accounts("ethereumMainnet"), ledgerAccounts: ledgerAccounts("ethereumMainnet"), chainId: 1 } as any
  },
  etherscan: {
    apiKey: {
      mainnet: ETHERSCAN_API_KEY,
      sepolia: ETHERSCAN_API_KEY
    }
  }
};

export default config;
