import { ethers } from "ethers";
import { AGIALPHA_MAINNET_TOKEN } from "../../config/networkConfig";

export function assertMainnetCanonicalAgialpha(token: string | undefined) {
  if (!token) throw new Error(`AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA_MAINNET_TOKEN}.`);
  if (!ethers.isAddress(token) || token.toLowerCase() !== AGIALPHA_MAINNET_TOKEN.toLowerCase()) {
    throw new Error(`Ethereum Mainnet requires canonical AGIALPHA token ${AGIALPHA_MAINNET_TOKEN}; MockAGIALPHA is forbidden.`);
  }
}

export function assertNoMainnetMockToken(env: NodeJS.ProcessEnv = process.env) {
  if (env.MOCK_AGIALPHA_ADDRESS) throw new Error("MOCK_AGIALPHA_ADDRESS must not be set for Ethereum Mainnet; MockAGIALPHA is forbidden.");
  if ((env.DEPLOY_NEW_AGIALPHA_TOKEN || "").toLowerCase() === "true") throw new Error("DEPLOY_NEW_AGIALPHA_TOKEN=true is forbidden on Ethereum Mainnet.");
}
