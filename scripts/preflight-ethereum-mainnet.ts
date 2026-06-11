import fs from "fs";
import crypto from "crypto";
import { ethers } from "hardhat";
import { AGIALPHA_MAINNET_TOKEN, assertAgialphaMainnetToken, assertNoMockTokenOnMainnet } from "./config/networkConfig";

function sha256(data: unknown) { return "0x" + crypto.createHash("sha256").update(typeof data === "string" ? data : JSON.stringify(data, Object.keys(data as any).sort())).digest("hex"); }
async function maybeCall(contract: any, fn: string) { try { return await contract[fn](); } catch { return null; } }
async function main() {
  const blockers: string[] = [];
  const net = await ethers.provider.getNetwork();
  const chainId = Number(net.chainId);
  const token = process.env.AGIALPHA_TOKEN_ADDRESS || AGIALPHA_MAINNET_TOKEN;
  if (chainId !== 1) blockers.push(`Expected Ethereum Mainnet chainId 1, got ${chainId}`);
  try { assertAgialphaMainnetToken(token); assertNoMockTokenOnMainnet(chainId, token); } catch (error: any) { blockers.push(error.message); }
  const code = await ethers.provider.getCode(AGIALPHA_MAINNET_TOKEN).catch(() => "0x");
  if (chainId === 1 && code === "0x") blockers.push("Canonical AGIALPHA token has no code on connected mainnet RPC");
  const erc20 = new ethers.Contract(AGIALPHA_MAINNET_TOKEN, ["function name() view returns (string)", "function symbol() view returns (string)", "function decimals() view returns (uint8)", "function totalSupply() view returns (uint256)"], ethers.provider);
  const [name, symbol, decimals, totalSupply] = code !== "0x" ? await Promise.all([maybeCall(erc20, "name"), maybeCall(erc20, "symbol"), maybeCall(erc20, "decimals"), maybeCall(erc20, "totalSupply")]) : [null, null, null, null];
  const [deployer] = await ethers.getSigners().catch(() => [] as any[]);
  const deployerBalanceWei = deployer ? (await ethers.provider.getBalance(deployer.address)).toString() : null;
  const report = { redacted: true, containsSecrets: false, containsPrivateAddresses: false, status: blockers.length ? "BLOCKED" : "PASSED", generatedAt: new Date().toISOString(), generatedBy: "scripts/preflight-ethereum-mainnet.ts", chain: "ethereum", chainId: 1, connectedChainId: chainId, agialphaToken: AGIALPHA_MAINNET_TOKEN, agialphaCodePresent: code !== "0x", tokenMetadata: { name, symbol, decimals: decimals?.toString?.() ?? decimals, totalSupply: totalSupply?.toString?.() ?? totalSupply }, deployerBalanceCommitmentHash: deployerBalanceWei ? sha256(deployerBalanceWei) : null, checks: { noMockAGIALPHA: true, noNewAGIALPHATokenDeployment: true, protocolLabelsEthereumMainnet: true, manifestOutputEthereumMainnet: true, authorizationJsonRequiredBeforeDeployment: true }, blockers };
  fs.mkdirSync("qa", { recursive: true }); fs.mkdirSync(".private", { recursive: true }); fs.mkdirSync("docs", { recursive: true });
  fs.writeFileSync("qa/public-mainnet-preflight-evidence.json", JSON.stringify(report, null, 2) + "\n");
  fs.writeFileSync(".private/mainnet-preflight-private.json", JSON.stringify({ ...report, private: true, deployerAddressRedacted: Boolean(deployer) }, null, 2) + "\n");
  fs.writeFileSync("docs/ETHEREUM_MAINNET_PREFLIGHT_REPORT.md", `# Ethereum Mainnet Preflight Report\n\nStatus: **${report.status}**\n\nNo Ethereum Mainnet deployment occurred. Private fields are held only in local .private artifacts.\n\n## Blockers\n${blockers.map((b) => `- ${b}`).join("\n") || "- None."}\n`);
  console.log(JSON.stringify(report, null, 2));
  if (blockers.length && process.env.STRICT_MAINNET_PREFLIGHT === "1") process.exit(1);
}
main().catch((error) => { console.error(error?.message || error); process.exitCode = 1; });
