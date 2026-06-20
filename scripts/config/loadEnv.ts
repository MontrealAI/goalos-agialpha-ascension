import fs from "fs";

function cliNetworkName(): string | undefined {
  const index = process.argv.indexOf("--network");
  if (index >= 0 && process.argv[index + 1]) return process.argv[index + 1];
  const equalsArg = process.argv.find((arg) => arg.startsWith("--network="));
  if (equalsArg) return equalsArg.split("=", 2)[1];
  return undefined;
}

function normalizedNetworkName(networkName?: string): string | undefined {
  return networkName || process.env.HARDHAT_NETWORK || process.env.npm_config_network || cliNetworkName();
}

export function loadDeploymentEnv(networkName?: string) {
  const resolved = normalizedNetworkName(networkName);
  const files = [".env"];
  if (resolved === "ethereumSepolia" || resolved === "sepolia") files.push(".env.sepolia.local", ".private/sepolia-operator.env");
  if (resolved === "ethereumMainnet" || resolved === "mainnet") files.push(".env.mainnet.local", ".private/mainnet-operator.env");
  for (const file of files) {
    if (!fs.existsSync(file)) continue;
    for (const raw of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
      const line = raw.trim();
      if (!line || line.startsWith("#") || !line.includes("=")) continue;
      const [key, ...rest] = line.split("=");
      if (process.env[key] === undefined) process.env[key] = rest.join("=").replace(/^[\'\"]|[\'\"]$/g, "");
    }
  }
}
