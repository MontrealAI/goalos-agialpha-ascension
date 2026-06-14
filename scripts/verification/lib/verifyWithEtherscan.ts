import { verifyWithHardhat } from "./verifyWithHardhat";

export function verifyWithEtherscan(network: string, fqcn: string, address: string, constructorArgsFile: string): string {
  return verifyWithHardhat(network, fqcn, address, constructorArgsFile);
}
