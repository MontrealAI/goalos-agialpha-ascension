import fs from "fs";

export function writeVerificationReport(path: string, title: string, summary: string, claimBoundary: string): void {
  fs.mkdirSync(path.replace(/\/[^/]+$/, ""), { recursive: true });
  fs.writeFileSync(path, `# ${title}\n\n${summary}\n\nClaim boundary: ${claimBoundary}\n`);
}
