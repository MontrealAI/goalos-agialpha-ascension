
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const output = JSON.parse(fs.readFileSync(path.join(root, 'direct-solc-output', 'output.json'), 'utf8'));
const artifactsRoot = path.join(root, 'artifacts');

function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }

for (const [sourceName, contracts] of Object.entries(output.contracts || {})) {
  for (const [contractName, c] of Object.entries(contracts)) {
    const bytecode = c.evm?.bytecode?.object || "";
    const deployedBytecode = c.evm?.deployedBytecode?.object || "";
    const artifact = {
      _format: "hh-sol-artifact-1",
      contractName,
      sourceName,
      abi: c.abi || [],
      bytecode: bytecode ? "0x" + bytecode : "0x",
      deployedBytecode: deployedBytecode ? "0x" + deployedBytecode : "0x",
      linkReferences: c.evm?.bytecode?.linkReferences || {},
      deployedLinkReferences: c.evm?.deployedBytecode?.linkReferences || {}
    };
    const outDir = path.join(artifactsRoot, path.dirname(sourceName), path.basename(sourceName));
    ensureDir(outDir);
    fs.writeFileSync(path.join(outDir, `${contractName}.json`), JSON.stringify(artifact, null, 2));
  }
}

console.log("Generated Hardhat-compatible artifacts from direct solc output.");
