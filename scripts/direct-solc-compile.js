
const fs = require('fs');
const path = require('path');
const solc = require('solc');

const root = path.resolve(__dirname, '..');
const contractDir = path.join(root, 'contracts');

function walk(dir) {
  const out = [];
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) out.push(...walk(p));
    else if (name.endsWith('.sol')) out.push(p);
  }
  return out;
}

const sources = {};
for (const file of walk(contractDir)) {
  const rel = path.relative(root, file).replace(/\\/g, '/');
  sources[rel] = { content: fs.readFileSync(file, 'utf8') };
}

function findImports(importPath) {
  const candidates = [
    path.join(root, importPath),
    path.join(root, 'contracts', importPath),
    path.join(root, 'node_modules', importPath),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) {
      return { contents: fs.readFileSync(c, 'utf8') };
    }
  }
  return { error: `Import not found: ${importPath}` };
}

const input = {
  language: 'Solidity',
  sources,
  settings: {
    optimizer: { enabled: true, runs: 200 },
    outputSelection: {
      '*': {
        '*': ['abi', 'evm.bytecode.object', 'evm.deployedBytecode.object'],
        '': ['ast']
      }
    }
  }
};

const output = JSON.parse(solc.compile(JSON.stringify(input), { import: findImports }));

fs.mkdirSync(path.join(root, 'direct-solc-output'), { recursive: true });
fs.writeFileSync(path.join(root, 'direct-solc-output', 'output.json'), JSON.stringify(output, null, 2));

let errors = output.errors || [];
for (const e of errors) {
  console.log(`${e.severity.toUpperCase()}: ${e.formattedMessage}`);
}
const fatal = errors.filter(e => e.severity === 'error');
if (fatal.length > 0) {
  process.exit(1);
}
console.log(`Direct solc-js compile passed with ${errors.length} warnings/errors total and ${fatal.length} fatal errors.`);
