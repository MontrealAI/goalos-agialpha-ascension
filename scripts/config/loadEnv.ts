import fs from "fs";

export function loadDeploymentEnv(networkName?: string) {
  const files = [".env"];
  if (networkName === "ethereumSepolia" || networkName === "sepolia") files.push(".env.sepolia.local");
  if (networkName === "ethereumMainnet" || networkName === "mainnet") files.push(".env.mainnet.local", ".private/mainnet-operator.env");
  for (const file of files) {
    if (!fs.existsSync(file)) continue;
    for (const raw of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
      const line = raw.trim();
      if (!line || line.startsWith("#") || !line.includes("=")) continue;
      const [key, ...rest] = line.split("=");
      if (process.env[key] === undefined) process.env[key] = rest.join("=").replace(/^['\"]|['\"]$/g, "");
    }
  }
}
