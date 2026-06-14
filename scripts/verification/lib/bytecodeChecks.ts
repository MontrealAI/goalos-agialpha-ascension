export async function hasContractBytecode(provider: { getCode(address: string): Promise<string> }, address: string): Promise<boolean> {
  const code = await provider.getCode(address);
  return Boolean(code && code !== "0x");
}

export function isAddressLike(address: unknown): address is string {
  return typeof address === "string" && /^0x[0-9a-fA-F]{40}$/.test(address);
}
