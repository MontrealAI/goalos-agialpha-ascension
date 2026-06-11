import fs from "fs";
const AGIALPHA_MAINNET = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";
const ALLOW_VALUE = "YES_FOUNDER_APPROVED_MAINNET_AUTHORIZATION";
const bytes32Keys = ["LEGAL_SIGNOFF_HASH","TAX_SIGNOFF_HASH","SECURITY_REVIEW_HASH","PUBLIC_CLAIMS_REVIEW_HASH","TREASURY_REVIEW_HASH","AGIALPHA_TOKEN_VERIFICATION_HASH","SEPOLIA_REHEARSAL_EVIDENCE_HASH","AUTOMATED_SECURITY_TOOLCHAIN_HASH","INTERNAL_SECURITY_REVIEW_HASH","FOUNDER_APPROVAL_HASH"];
const addressKeys = ["AGIALPHA_TOKEN_ADDRESS","FOUNDER_ADDRESS","TREASURY_ADDRESS","COMMERCIALIZATION_PERFORMANCE_ADMIN","PROOF_REWARDS_ADMIN","LIQUIDITY_ADMIN","SECURITY_ADMIN","COMMUNITY_ADMIN"];
const blockers: string[] = [];
function validBytes32(v = "") { return /^0x[0-9a-fA-F]{64}$/.test(v) && !/^0x(0{64}|1{64}|f{64})$/i.test(v); }
function validAddress(v = "") { return /^0x[0-9a-fA-F]{40}$/.test(v) && !/^0x0{40}$/i.test(v); }
if (process.env.MAINNET_TARGET !== "ethereum") blockers.push("MAINNET_TARGET must equal ethereum");
if (process.env.ALLOW_MAINNET_DEPLOYMENT !== ALLOW_VALUE) blockers.push(`ALLOW_MAINNET_DEPLOYMENT must equal ${ALLOW_VALUE} only after all real gates are complete`);
for (const key of bytes32Keys) if (!validBytes32(process.env[key])) blockers.push(`${key} missing, malformed, or placeholder`);
for (const key of addressKeys) if (!validAddress(process.env[key])) blockers.push(`${key} missing, malformed, or zero address`);
if ((process.env.AGIALPHA_TOKEN_ADDRESS || "").toLowerCase() !== AGIALPHA_MAINNET.toLowerCase()) blockers.push(`AGIALPHA_TOKEN_ADDRESS must equal ${AGIALPHA_MAINNET}`);
if (!process.env.ETHEREUM_MAINNET_RPC_URL && !process.env.MAINNET_RPC_URL) blockers.push("ETHEREUM_MAINNET_RPC_URL or MAINNET_RPC_URL is required for real read-only mainnet verification");
const status = blockers.length ? "NOT_AUTHORIZED" : "PASSED_READ_ONLY";
const report = { status, chain: "ethereum", chainId: 1, agialphaToken: AGIALPHA_MAINNET, blockers, mainnetDeployment: "not executed", generatedAt: new Date().toISOString(), generatedBy: "scripts/preflight-ethereum-mainnet-gates.ts" };
fs.mkdirSync("qa", { recursive: true });
fs.mkdirSync("docs", { recursive: true });
fs.writeFileSync("qa/ETHEREUM_MAINNET_PREFLIGHT.json", JSON.stringify(report, null, 2) + "\n");
fs.writeFileSync("docs/ETHEREUM_MAINNET_PREFLIGHT_REPORT.md", `# Ethereum Mainnet Preflight Report\n\nStatus: **${status}**\n\n## Blockers\n${blockers.map((b) => `- ${b}`).join("\n") || "- None."}\n\nNo Ethereum Mainnet deployment occurred.\n`);
console.log(JSON.stringify(report, null, 2));
if (blockers.length && process.env.STRICT_MAINNET_PREFLIGHT === "1") process.exit(1);
