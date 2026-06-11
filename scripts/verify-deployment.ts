import { ethers } from "hardhat";
import fs from "fs";
import path from "path";

const AGIALPHA_MAINNET = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";

async function codeExists(address: string, label: string) {
  const code = await ethers.provider.getCode(address);
  if (code === "0x") throw new Error(`No code for ${label} at ${address}`);
  console.log(`code OK: ${label} ${address}`);
}

async function main() {
  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) !== 1) throw new Error(`Expected Ethereum mainnet chainId 1; got ${net.chainId}`);

  const manifestPath = path.join(__dirname, "..", "deployments", "ethereum-mainnet.agialpha.latest.json");
  if (!fs.existsSync(manifestPath)) throw new Error(`Missing manifest: ${manifestPath}`);

  const deployment = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  if (deployment.chainId !== 1) throw new Error("Manifest chainId is not 1.");
  if ((deployment.agialphaToken || "").toLowerCase() !== AGIALPHA_MAINNET.toLowerCase()) {
    throw new Error("Manifest AGIALPHA token does not match canonical Ethereum mainnet AGIALPHA address.");
  }

  await codeExists(AGIALPHA_MAINNET, "AGIALPHA");
  for (const [label, address] of Object.entries(deployment.contracts || {})) {
    if (label === "AGIALPHA") continue;
    await codeExists(String(address), label);
  }

  console.log("Deployment verification passed.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
