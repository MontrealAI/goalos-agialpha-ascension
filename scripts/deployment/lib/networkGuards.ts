import { ethers } from "ethers";
import { getExpectedChainId, getOptionalPrivateKey, getOptionalRpcUrl } from "../../config/networkConfig";

export function requireRpc(networkName: string): string {
  const rpc = getOptionalRpcUrl(networkName);
  if (!rpc) throw new Error(`Missing RPC URL for ${networkName}. Set ${networkName.includes("Mainnet") ? "PRIVATE_MAINNET_RPC_URL" : "PRIVATE_SEPOLIA_RPC_URL"}.`);
  return rpc;
}

export function requireDeployerKey(networkName: string): string {
  const key = getOptionalPrivateKey(networkName);
  if (!key) throw new Error(`Missing deployer private key for ${networkName}. Set ${networkName.includes("Mainnet") ? "PRIVATE_MAINNET_DEPLOYER_PRIVATE_KEY" : "PRIVATE_SEPOLIA_DEPLOYER_PRIVATE_KEY"}.`);
  if (!/^0x[0-9a-fA-F]{64}$/.test(key)) throw new Error(`Invalid private-key shape for ${networkName}; expected 0x-prefixed 64 hex characters.`);
  return key;
}

export async function assertExpectedChainId(networkName: string, provider: { getNetwork(): Promise<{ chainId: bigint | number }> }) {
  const expected = getExpectedChainId(networkName);
  const actual = Number((await provider.getNetwork()).chainId);
  if (actual !== expected) throw new Error(`Wrong chain for ${networkName}: expected chainId ${expected}, got ${actual}.`);
}

export async function getWalletReadiness(networkName: string) {
  const rpc = requireRpc(networkName);
  const key = requireDeployerKey(networkName);
  const provider = new ethers.JsonRpcProvider(rpc);
  await assertExpectedChainId(networkName, provider);
  const wallet = new ethers.Wallet(key, provider);
  return { address: wallet.address, balanceWei: await provider.getBalance(wallet.address), nonce: await provider.getTransactionCount(wallet.address) };
}
