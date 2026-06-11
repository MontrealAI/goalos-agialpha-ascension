import { ethers } from "hardhat";
import { deployGoalOSAGIALPHAAscension } from "./deploy-core";

async function main() {
  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) !== 1) {
    throw new Error(`Wrong network. Expected Ethereum mainnet chainId 1, got ${net.chainId}.`);
  }
  if (process.env.MAINNET_TARGET !== "ethereum") {
    throw new Error("MAINNET_TARGET must be ethereum.");
  }
  await deployGoalOSAGIALPHAAscension();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
