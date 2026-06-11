const fs = require("fs");
const path = require("path");

const artifactsDir = path.join(__dirname, "..", "artifacts", "contracts");
const outDir = path.join(__dirname, "..", "deployments", "abis");
fs.mkdirSync(outDir, { recursive: true });

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).flatMap((name) => {
    const p = path.join(dir, name);
    return fs.statSync(p).isDirectory() ? walk(p) : [p];
  });
}

for (const file of walk(artifactsDir)) {
  if (!file.endsWith(".json") || file.endsWith(".dbg.json")) continue;
  const artifact = JSON.parse(fs.readFileSync(file, "utf8"));
  if (!artifact.abi) continue;
  fs.writeFileSync(path.join(outDir, path.basename(file)), JSON.stringify(artifact.abi, null, 2));
  console.log("exported", path.basename(file));
}
