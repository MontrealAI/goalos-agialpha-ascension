import { execFileSync } from "child_process";

export function verifyWithHardhat(network: string, fqcn: string, address: string, constructorArgsFile: string): string {
  return execFileSync("npx", ["hardhat", "verify", "--network", network, "--contract", fqcn, "--constructor-args", constructorArgsFile, address], { encoding: "utf8", stdio: "pipe" });
}
