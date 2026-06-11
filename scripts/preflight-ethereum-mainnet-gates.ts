const AGIALPHA_MAINNET = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA".toLowerCase();

const bytes32Keys = [
  "LEGAL_SIGNOFF_HASH",
  "TAX_SIGNOFF_HASH",
  "SECURITY_REVIEW_HASH",
  "PUBLIC_CLAIMS_REVIEW_HASH",
  "AGIALPHA_TOKEN_VERIFICATION_HASH",
  "TREASURY_REVIEW_HASH",
  "SEPOLIA_REHEARSAL_EVIDENCE_HASH",
  "EXTERNAL_AUDIT_CLOSURE_HASH",
  "FOUNDER_APPROVAL_HASH"
];

const addressKeys = [
  "AGIALPHA_TOKEN_ADDRESS",
  "FOUNDER_ADDRESS",
  "TREASURY_ADDRESS",
  "COMMERCIALIZATION_PERFORMANCE_ADMIN",
  "PROOF_REWARDS_ADMIN",
  "LIQUIDITY_ADMIN",
  "SECURITY_ADMIN",
  "COMMUNITY_ADMIN"
];

function requireBytes32(key: string) {
  const value = process.env[key] || "";
  if (!/^0x[0-9a-fA-F]{64}$/.test(value)) throw new Error(`${key} must be a 0x-prefixed 32-byte hash.`);
}

function requireAddress(key: string) {
  const value = process.env[key] || "";
  if (!/^0x[0-9a-fA-F]{40}$/.test(value)) throw new Error(`${key} must be a 0x-prefixed EVM address.`);
}

if (process.env.MAINNET_TARGET !== "ethereum") throw new Error("MAINNET_TARGET must equal ethereum.");
if (process.env.ALLOW_MAINNET_DEPLOYMENT !== "YES_ALL_GATES_APPROVED") throw new Error("ALLOW_MAINNET_DEPLOYMENT must equal YES_ALL_GATES_APPROVED.");

for (const key of bytes32Keys) requireBytes32(key);
for (const key of addressKeys) requireAddress(key);

if ((process.env.AGIALPHA_TOKEN_ADDRESS || "").toLowerCase() !== AGIALPHA_MAINNET) {
  throw new Error(`AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA_MAINNET}.`);
}

if (!process.env.ETHEREUM_MAINNET_RPC_URL) throw new Error("ETHEREUM_MAINNET_RPC_URL is required.");

console.log("Ethereum mainnet AGIALPHA Ascension preflight passed. This does not deploy; it only validates gate environment variables.");
