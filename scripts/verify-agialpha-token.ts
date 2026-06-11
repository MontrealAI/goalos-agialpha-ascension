import { ethers } from "hardhat";
import fs from "fs";

const AGIALPHA_MAINNET = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const erc20Abi = ["function name() view returns (string)","function symbol() view returns (string)","function decimals() view returns (uint8)","function totalSupply() view returns (uint256)"];
async function writeReport(report: any) {
  fs.mkdirSync("docs", { recursive: true });
  fs.mkdirSync("qa", { recursive: true });
  fs.writeFileSync("qa/AGIALPHA_TOKEN_VERIFICATION.json", JSON.stringify(report, null, 2) + "\n");
  fs.writeFileSync("docs/AGIALPHA_TOKEN_VERIFICATION_REPORT.md", `# AGIALPHA Token Verification Report\n\nStatus: **${report.status}**\n\n\`\`\`json\n${JSON.stringify(report, null, 2)}\n\`\`\`\n`);
}
async function main() {
  if (!process.env.ETHEREUM_MAINNET_RPC_URL) { const report={status:"PENDING_RPC", address:AGIALPHA_MAINNET, blocker:"ETHEREUM_MAINNET_RPC_URL is required for read-only token code verification", mainnetAuthorized:false}; await writeReport(report); console.log(JSON.stringify(report,null,2)); return; }
  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) !== 1) throw new Error(`verify:agialpha-token must run on Ethereum mainnet chainId 1; got ${net.chainId}`);
  const configured = process.env.AGIALPHA_TOKEN_ADDRESS || AGIALPHA_MAINNET;
  if (configured.toLowerCase() !== AGIALPHA_MAINNET.toLowerCase()) throw new Error(`AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA_MAINNET}`);
  const code = await ethers.provider.getCode(AGIALPHA_MAINNET); if (code === "0x") throw new Error("No contract code found at AGIALPHA mainnet address.");
  const token = new ethers.Contract(AGIALPHA_MAINNET, erc20Abi, ethers.provider);
  const [name, symbol, decimals, totalSupply] = await Promise.all([token.name(), token.symbol(), token.decimals(), token.totalSupply()]);
  const report={status:"PASSED", address:AGIALPHA_MAINNET, name, symbol, decimals:Number(decimals), totalSupply:totalSupply.toString(), mainnetAuthorized:false};
  await writeReport(report); console.log(JSON.stringify(report,null,2));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
