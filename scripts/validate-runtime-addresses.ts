import { ethers } from "ethers";

export type RuntimeAddressMode =
  | "RUNTIME_ADDRESS_PROMPT_MODE"
  | "SAFE_GOVERNANCE"
  | "LEDGER_EOA";

export type RuntimeAddresses = {
  governanceOwner: string;
  operationsAddress: string;
  founder: string;
  treasury: string;
  commercializationAdmin: string;
  proofRewardsAdmin: string;
  liquidityAdmin: string;
  securityAdmin: string;
  communityAdmin: string;
};

const ENV_MAP: Record<keyof RuntimeAddresses, string> = {
  governanceOwner: "GOVERNANCE_OWNER_ADDRESS",
  operationsAddress: "OPERATIONS_ADDRESS",
  founder: "FOUNDER_ADDRESS",
  treasury: "TREASURY_ADDRESS",
  commercializationAdmin: "COMMERCIALIZATION_PERFORMANCE_ADMIN",
  proofRewardsAdmin: "PROOF_REWARDS_ADMIN",
  liquidityAdmin: "LIQUIDITY_ADMIN",
  securityAdmin: "SECURITY_ADMIN",
  communityAdmin: "COMMUNITY_ADMIN",
};

function requireValidAddress(label: string, value: string | undefined): string {
  if (!value || !ethers.isAddress(value) || value === ethers.ZeroAddress) {
    throw new Error(`Invalid runtime ${label} address. Provide it locally at deployment time; do not commit it.`);
  }
  return ethers.getAddress(value);
}

export function runtimeAddressMode(): RuntimeAddressMode {
  if (process.env.SINGLE_DEPLOYER_INITIAL_ADMIN_MODE === "true") {
    throw new Error("Mainnet deployment blocked: SINGLE_DEPLOYER_INITIAL_ADMIN_MODE=true is retired. Use GOVERNANCE_OWNER_ADDRESS, GOVERNANCE_OWNER_KIND, OPERATIONS_ADDRESS, and vault owner addresses from a private authority policy.");
  }
  if (process.env.GOVERNANCE_OWNER_KIND === "SAFE") return "SAFE_GOVERNANCE";
  if (process.env.GOVERNANCE_OWNER_KIND === "LEDGER_EOA") {
    if (process.env.ALLOW_SINGLE_LEDGER_EOA_GOVERNANCE !== "I_ACCEPT_SINGLE_KEY_AND_RECOVERY_RISK") {
      throw new Error("LEDGER_EOA governance requires ALLOW_SINGLE_LEDGER_EOA_GOVERNANCE=I_ACCEPT_SINGLE_KEY_AND_RECOVERY_RISK.");
    }
    return "LEDGER_EOA";
  }
  return "RUNTIME_ADDRESS_PROMPT_MODE";
}

export function loadRuntimeAddresses(deployerAddress: string): { mode: RuntimeAddressMode; addresses: RuntimeAddresses } {
  const deployer = requireValidAddress("deployer", deployerAddress);
  if (!process.env.GOVERNANCE_OWNER_KIND) {
    throw new Error("Mainnet deployment blocked: GOVERNANCE_OWNER_KIND must be SAFE or LEDGER_EOA.");
  }
  const mode = runtimeAddressMode();
  const addresses = Object.fromEntries(
    Object.entries(ENV_MAP).map(([key, envName]) => [key, requireValidAddress(envName, process.env[envName])])
  ) as RuntimeAddresses;
  for (const [key, value] of Object.entries(addresses) as [keyof RuntimeAddresses, string][]) {
    if (value === deployer) {
      throw new Error(`Mainnet deployment blocked: ${ENV_MAP[key]} must not equal the disposable deployer. Use GOVERNANCE_OWNER_ADDRESS, OPERATIONS_ADDRESS, and policy-declared vault owners.`);
    }
  }
  return { mode, addresses };
}

export function applyRuntimeAddressesToEnv(deployerAddress: string): RuntimeAddressMode {
  const { mode, addresses } = loadRuntimeAddresses(deployerAddress);
  for (const [key, envName] of Object.entries(ENV_MAP) as [keyof RuntimeAddresses, string][]) {
    process.env[envName] = addresses[key];
  }
  return mode;
}
