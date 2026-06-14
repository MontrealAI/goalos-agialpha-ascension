const SENSITIVE_KEY = /(KEY|SECRET|TOKEN|PRIVATE|RPC|MNEMONIC|SEED|SIGNATURE|BEARER|AUTHORIZATION)/i;
const PRIVATE_KEY = /0x[0-9a-fA-F]{64}/g;
const URL = /https?:\/\/[^\s"']+/g;
const BEARER = /Bearer\s+[A-Za-z0-9._~+/=-]+/gi;

export const REDACTED = "[REDACTED]";

export function isSensitiveEnvName(name: string): boolean {
  return SENSITIVE_KEY.test(name);
}

export function redactString(value: string | undefined): string {
  if (!value) return "";
  return value.replace(BEARER, "Bearer [REDACTED]").replace(PRIVATE_KEY, REDACTED).replace(URL, REDACTED);
}

export function redactValue(key: string, value: unknown): unknown {
  if (value === undefined || value === null) return value;
  if (typeof value === "string") return isSensitiveEnvName(key) ? REDACTED : redactString(value);
  if (Array.isArray(value)) return value.map((entry) => redactValue(key, entry));
  if (typeof value === "object") return redactObject(value as Record<string, unknown>);
  return value;
}

export function redactObject<T extends Record<string, unknown>>(input: T): T {
  return Object.fromEntries(Object.entries(input).map(([key, value]) => [key, redactValue(key, value)])) as T;
}

export function redactedEnv(names: string[]): Record<string, string> {
  return Object.fromEntries(names.map((name) => [name, process.env[name] ? REDACTED : "<unset>"]));
}
