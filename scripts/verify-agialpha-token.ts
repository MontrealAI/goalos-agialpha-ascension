import { ethers } from "hardhat";

const AGIALPHA_MAINNET = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const erc20Abi = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)"
];

async function main() {
  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) !== 1) {
    throw new Error(`verify:agialpha-token must run on Ethereum mainnet chainId 1; got ${net.chainId}`);
  }

  const configured = process.env.AGIALPHA_TOKEN_ADDRESS || AGIALPHA_MAINNET;
  if (configured.toLowerCase() !== AGIALPHA_MAINNET.toLowerCase()) {
    throw new Error(`AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA_MAINNET}`);
  }

  const code = await ethers.provider.getCode(AGIALPHA_MAINNET);
  if (code === "0x") throw new Error("No contract code found at AGIALPHA mainnet address.");

  const token = new ethers.Contract(AGIALPHA_MAINNET, erc20Abi, ethers.provider);
  const [name, symbol, decimals, totalSupply] = await Promise.all([
    token.name(),
    token.symbol(),
    token.decimals(),
    token.totalSupply()
  ]);

  console.log("AGIALPHA token verified:");
  console.log({ address: AGIALPHA_MAINNET, name, symbol, decimals: Number(decimals), totalSupply: totalSupply.toString() });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
