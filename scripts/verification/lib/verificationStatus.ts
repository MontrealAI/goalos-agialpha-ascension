export type VerificationStatus = "pending" | "verified" | "already_verified" | "failed" | "skipped";

const ALREADY_VERIFIED = /already verified|already been verified|already verified contract/i;

export function classifyVerificationOutput(output: string): VerificationStatus {
  if (ALREADY_VERIFIED.test(output)) return "already_verified";
  if (/successfully verified|verified successfully/i.test(output)) return "verified";
  if (/skipped/i.test(output)) return "skipped";
  return "failed";
}

export function verificationSucceeded(status: VerificationStatus): boolean {
  return status === "verified" || status === "already_verified";
}
