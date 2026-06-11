import { ethers } from "ethers";

export const EXPECTED_ETHEREUM_MAINNET_CHAIN_ID = 1;
export const EXPECTED_ETHEREUM_SEPOLIA_CHAIN_ID = 11155111;
export const AGIALPHA_MAINNET_TOKEN = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const NETWORKS: Record<string, { chainId: number; rpcEnv: string[]; keyEnv: string[] }> = {
  ethereumSepolia: { chainId: EXPECTED_ETHEREUM_SEPOLIA_CHAIN_ID, rpcEnv: ["PRIVATE_SEPOLIA_RPC_URL", "SEPOLIA_RPC_URL", "ETHEREUM_SEPOLIA_RPC_URL"], keyEnv: ["PRIVATE_SEPOLIA_DEPLOYER_PRIVATE_KEY", "SEPOLIA_DEPLOYER_PRIVATE_KEY", "PRIVATE_DEPLOYER_PRIVATE_KEY", "DEPLOYER_PRIVATE_KEY", "PRIVATE_KEY"] },
  sepolia: { chainId: EXPECTED_ETHEREUM_SEPOLIA_CHAIN_ID, rpcEnv: ["PRIVATE_SEPOLIA_RPC_URL", "SEPOLIA_RPC_URL", "ETHEREUM_SEPOLIA_RPC_URL"], keyEnv: ["PRIVATE_SEPOLIA_DEPLOYER_PRIVATE_KEY", "SEPOLIA_DEPLOYER_PRIVATE_KEY", "PRIVATE_DEPLOYER_PRIVATE_KEY", "DEPLOYER_PRIVATE_KEY", "PRIVATE_KEY"] },
  ethereumMainnet: { chainId: EXPECTED_ETHEREUM_MAINNET_CHAIN_ID, rpcEnv: ["PRIVATE_MAINNET_RPC_URL", "MAINNET_RPC_URL", "ETHEREUM_MAINNET_RPC_URL"], keyEnv: ["PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY", "MAINNET_DEPLOYER_PRIVATE_KEY", "PRIVATE_DEPLOYER_PRIVATE_KEY", "DEPLOYER_PRIVATE_KEY", "PRIVATE_KEY"] },
  mainnet: { chainId: EXPECTED_ETHEREUM_MAINNET_CHAIN_ID, rpcEnv: ["PRIVATE_MAINNET_RPC_URL", "MAINNET_RPC_URL", "ETHEREUM_MAINNET_RPC_URL"], keyEnv: ["PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY", "MAINNET_DEPLOYER_PRIVATE_KEY", "PRIVATE_DEPLOYER_PRIVATE_KEY", "DEPLOYER_PRIVATE_KEY", "PRIVATE_KEY"] },
  hardhat: { chainId: 31337, rpcEnv: [], keyEnv: [] },
  localhost: { chainId: 31337, rpcEnv: ["LOCALHOST_RPC_URL"], keyEnv: ["LOCALHOST_PRIVATE_KEY"] }
};

function firstEnv(names: string[]): string | undefined {
  for (const name of names) {
    const value = process.env[name]?.trim();
    if (value) return value;
  }
  return undefined;
}

function normalized(name: string) { return NETWORKS[name] || NETWORKS[name.replace(/^ethereum-/, "ethereum")]; }

export function getOptionalRpcUrl(networkName: string): string | undefined { return firstEnv(normalized(networkName)?.rpcEnv || []); }
export function getRequiredRpcUrl(networkName: string): string {
  const value = getOptionalRpcUrl(networkName);
  if (!value) throw new Error(`Missing private RPC URL for ${networkName}. Load it locally; public CI must not provide it.`);
  return value;
}
export function getOptionalPrivateKey(networkName: string): string | undefined { return firstEnv(normalized(networkName)?.keyEnv || []); }
export function getRequiredPrivateKey(networkName: string): string {
  const value = getOptionalPrivateKey(networkName);
  if (!value) throw new Error(`Missing deployer private key for ${networkName}. Load it locally; never commit it.`);
  if (!/^0x[0-9a-fA-F]{64}$/.test(value)) throw new Error(`Invalid private-key shape for ${networkName}.`);
  return value;
}
export function getExpectedChainId(networkName: string): number {
  const cfg = normalized(networkName);
  if (!cfg) throw new Error(`Unsupported network ${networkName}`);
  return cfg.chainId;
}
export async function assertExpectedChain(networkName: string, provider: { getNetwork(): Promise<{ chainId: bigint | number }> }) {
  const actual = Number((await provider.getNetwork()).chainId);
  const expected = getExpectedChainId(networkName);
  if (actual !== expected) throw new Error(`Wrong chain for ${networkName}: expected ${expected}, got ${actual}.`);
}

export async function assertEthereumMainnet(provider: { getNetwork(): Promise<{ chainId: bigint | number }> }) {
  await assertExpectedChain("ethereumMainnet", provider);
}
export async function assertEthereumSepolia(provider: { getNetwork(): Promise<{ chainId: bigint | number }> }) {
  await assertExpectedChain("ethereumSepolia", provider);
}
export function assertNoGitHubActionsMainnetDeployment() {
  if (process.env.GITHUB_ACTIONS === "true" || process.env.CI === "true") {
    throw new Error("Ethereum Mainnet deployment is forbidden from GitHub Actions/CI; use the private local wrapper.");
  }
}

export function maskSecret(value: string | undefined): string { return value ? `${value.slice(0, 4)}…${value.slice(-4)}` : "<unset>"; }
export function assertNoMockTokenOnMainnet(chainId: number, tokenAddress: string) {
  if (chainId === 1 && tokenAddress.toLowerCase() !== AGIALPHA_MAINNET_TOKEN.toLowerCase()) throw new Error("Ethereum Mainnet deployment must use the canonical AGIALPHA token; MockAGIALPHA is forbidden.");
}
export function assertAgialphaMainnetToken(tokenAddress: string) {
  if (!ethers.isAddress(tokenAddress) || tokenAddress.toLowerCase() !== AGIALPHA_MAINNET_TOKEN.toLowerCase()) throw new Error(`AGIALPHA token must equal ${AGIALPHA_MAINNET_TOKEN}.`);
}
export function assertNoSecretLogging() {
  for (const [key, value] of Object.entries(process.env)) {
    if (!value) continue;
    if (/(PRIVATE_KEY|RPC_URL|ETHERSCAN_API_KEY|SIGNATURE|MNEMONIC|SEED)/i.test(key) && process.argv.join(" ").includes(value)) {
      throw new Error(`Refusing to continue: sensitive value for ${key} appears in command arguments.`);
    }
  }
}
