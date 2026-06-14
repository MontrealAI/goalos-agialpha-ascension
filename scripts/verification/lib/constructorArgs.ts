import fs from "fs";

export function constructorArgsFor(contract: any, manifest: any): unknown[] | undefined {
  if (Array.isArray(contract.constructorArgs)) return contract.constructorArgs;
  if (Array.isArray(manifest?.constructorArgs?.[contract.name])) return manifest.constructorArgs[contract.name];
  return undefined;
}

export function writeConstructorArgsFile(path: string, args: unknown[]): string {
  fs.mkdirSync(path.replace(/\/[^/]+$/, ""), { recursive: true });
  fs.writeFileSync(path, `export default ${JSON.stringify(args, null, 2)};\n`);
  return path;
}
