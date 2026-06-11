import { ethers } from "hardhat";
import fs from "fs";
import { deployGoalOSAGIALPHAAscension } from "./deploy-core";

const AGIALPHA_MAINNET = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const ALLOW_VALUE = "YES_FOUNDER_APPROVED_MAINNET_AUTHORIZATION";
const CONFIRM_PHRASE = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET";

function readAuthorization() {
  const path = "docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json";
  if (!fs.existsSync(path)) throw new Error("Ethereum Mainnet authorization decision JSON is missing.");
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

async function main() {
  const net = await ethers.provider.getNetwork();
  if (Number(net.chainId) !== 1) throw new Error(`Wrong network. Expected Ethereum mainnet chainId 1, got ${net.chainId}.`);
  if (process.env.MAINNET_TARGET !== "ethereum") throw new Error("MAINNET_TARGET must be ethereum.");
  if ((process.env.AGIALPHA_TOKEN_ADDRESS || "").toLowerCase() !== AGIALPHA_MAINNET.toLowerCase()) throw new Error(`AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA_MAINNET}.`);
  if (process.env.ALLOW_MAINNET_DEPLOYMENT !== ALLOW_VALUE) throw new Error(`ALLOW_MAINNET_DEPLOYMENT must equal ${ALLOW_VALUE}.`);
  if (!/^0x[0-9a-fA-F]{64}$/.test(process.env.FOUNDER_APPROVAL_HASH || "")) throw new Error("FOUNDER_APPROVAL_HASH must be a real bytes32 value.");
  if (process.env.MAINNET_DEPLOYMENT_CONFIRMATION !== CONFIRM_PHRASE) throw new Error("Missing typed mainnet deployment confirmation phrase. Do not set this in CI.");
  const authorization = readAuthorization();
  if (authorization.status !== "YES" || authorization.ETHEREUM_MAINNET_AUTHORIZED !== "YES") throw new Error("Ethereum Mainnet authorization decision is not YES.");
  await deployGoalOSAGIALPHAAscension();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
