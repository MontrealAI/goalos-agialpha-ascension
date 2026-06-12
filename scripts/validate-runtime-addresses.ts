import { ethers } from "ethers";

export type RuntimeAddressMode =
  | "SINGLE_DEPLOYER_INITIAL_ADMIN_MODE"
  | "RUNTIME_ADDRESS_PROMPT_MODE"
  | "MULTISIG_RUNTIME_MODE";

export type RuntimeAddresses = {
  founder: string;
  treasury: string;
  commercializationAdmin: string;
  proofRewardsAdmin: string;
  liquidityAdmin: string;
  securityAdmin: string;
  communityAdmin: string;
};

const ENV_MAP: Record<keyof RuntimeAddresses, string> = {
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
  if (process.env.SINGLE_DEPLOYER_INITIAL_ADMIN_MODE === "true") return "SINGLE_DEPLOYER_INITIAL_ADMIN_MODE";
  if (process.env.MULTISIG_RUNTIME_MODE === "true") return "MULTISIG_RUNTIME_MODE";
  return "RUNTIME_ADDRESS_PROMPT_MODE";
}

export function loadRuntimeAddresses(deployerAddress: string): { mode: RuntimeAddressMode; addresses: RuntimeAddresses } {
  const mode = runtimeAddressMode();
  if (mode === "SINGLE_DEPLOYER_INITIAL_ADMIN_MODE") {
    const deployer = requireValidAddress("single deployer", deployerAddress);
    console.warn("WARNING: SINGLE_DEPLOYER_INITIAL_ADMIN_MODE=true. Deployer is initial admin/treasury/guardian; post-deployment transfer runbook is required.");
    return {
      mode,
      addresses: {
        founder: deployer,
        treasury: deployer,
        commercializationAdmin: deployer,
        proofRewardsAdmin: deployer,
        liquidityAdmin: deployer,
        securityAdmin: deployer,
        communityAdmin: deployer,
      },
    };
  }

  const addresses = Object.fromEntries(
    Object.entries(ENV_MAP).map(([key, envName]) => [key, requireValidAddress(envName, process.env[envName])])
  ) as RuntimeAddresses;
  return { mode, addresses };
}

export function applyRuntimeAddressesToEnv(deployerAddress: string): RuntimeAddressMode {
  const { mode, addresses } = loadRuntimeAddresses(deployerAddress);
  for (const [key, envName] of Object.entries(ENV_MAP) as [keyof RuntimeAddresses, string][]) {
    process.env[envName] = addresses[key];
  }
  return mode;
}
