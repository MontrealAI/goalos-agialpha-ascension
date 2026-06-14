import fs from "fs";
import { assertMainnetCanonicalAgialpha, assertNoMainnetMockToken } from "./tokenGuards";

export const MAINNET_CONFIRMATION_PHRASE = "DEPLOY_GOALOS_AGIALPHA_ASCENSION_TO_ETHEREUM_MAINNET";
export const MAINNET_ALLOW_VALUE = "YES_PUBLIC_REPOSITORY_AUTHORIZED_MANUAL_DEPLOYMENT";

export function assertNotCiForMainnet(env: NodeJS.ProcessEnv = process.env) {
  if (env.GITHUB_ACTIONS === "true" || env.CI === "true") throw new Error("Ethereum Mainnet live deployment is forbidden in CI/GitHub Actions; final broadcast is local-only.");
}

export function assertMainnetOperatorEnv(env: NodeJS.ProcessEnv = process.env) {
  assertNotCiForMainnet(env);
  if (env.MAINNET_TARGET !== "ethereum") throw new Error("MAINNET_TARGET must equal ethereum.");
  if (env.MAINNET_DEPLOYMENT_CONFIRMATION !== MAINNET_CONFIRMATION_PHRASE && env.FINAL_DEPLOY_CONFIRMATION !== MAINNET_CONFIRMATION_PHRASE) throw new Error(`Typed confirmation phrase required: ${MAINNET_CONFIRMATION_PHRASE}`);
  if (env.ALLOW_MAINNET_DEPLOYMENT !== MAINNET_ALLOW_VALUE) throw new Error(`ALLOW_MAINNET_DEPLOYMENT must equal ${MAINNET_ALLOW_VALUE} for local Mainnet broadcast.`);
  assertMainnetCanonicalAgialpha(env.AGIALPHA_TOKEN_ADDRESS);
  assertNoMainnetMockToken(env);
}

export function assertMainnetAuthorizationCertificate(path = "qa/mainnet-authorization-certificate.json") {
  if (!fs.existsSync(path)) throw new Error(`Missing Mainnet authorization certificate: ${path}`);
  const cert = JSON.parse(fs.readFileSync(path, "utf8"));
  if ((cert.TECHNICALLY_MAINNET_READY ?? cert.technicallyMainnetReady) !== "YES") throw new Error("TECHNICALLY_MAINNET_READY must be YES.");
  if ((cert.MAINNET_DEPLOYMENT_AUTHORIZED ?? cert.mainnetDeploymentAuthorized) !== "YES") throw new Error("MAINNET_DEPLOYMENT_AUTHORIZED must be YES.");
  if ((cert.ETHEREUM_MAINNET_AUTHORIZED ?? cert.ethereumMainnetAuthorized) !== "YES") throw new Error("ETHEREUM_MAINNET_AUTHORIZED must be YES.");
  if ((cert.MAINNET_DEPLOYED ?? cert.mainnetDeployed) !== "NO") throw new Error("MAINNET_DEPLOYED must remain NO before first real deployment.");
}

export function assertRealMainnetManifest(manifest: any) {
  if (!manifest || manifest.status === "TEMPLATE_NO_DEPLOYMENT") throw new Error("Mainnet verification blocked: template/no-deployment manifest is not a real deployment.");
  if (Number(manifest.chainId) !== 1) throw new Error("Mainnet manifest must have chainId 1.");
  assertMainnetCanonicalAgialpha(manifest.agialphaToken);
  assertNoMainnetMockToken({ MOCK_AGIALPHA_ADDRESS: manifest.mockAgialphaUsed ? "true" : "", DEPLOY_NEW_AGIALPHA_TOKEN: manifest.newAgialphaTokenDeployed ? "true" : "" } as NodeJS.ProcessEnv);
  if (!manifest.contracts || Object.keys(manifest.contracts).length === 0) throw new Error("Mainnet verification blocked: manifest has no deployed contracts.");
  if (!Array.isArray(manifest.transactions) || manifest.transactions.length === 0) throw new Error("Mainnet verification blocked: manifest has no transaction hashes.");
}
