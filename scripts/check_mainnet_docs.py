#!/usr/bin/env python3
import subprocess, pathlib, sys
root=pathlib.Path(__file__).resolve().parents[1]
before={p: (root/p).read_text() for p in ['config/ethereum-mainnet.contracts.json','docs/ETHEREUM_MAINNET_CONTRACTS.md','app/config/ethereum-mainnet.contracts.generated.ts','website/data/ethereum-mainnet.contracts.json'] if (root/p).exists()}
subprocess.run([sys.executable,str(root/'scripts/generate_mainnet_docs.py')],check=True)
for p,s in before.items():
 if (root/p).read_text()!=s:
  print('generated drift:',p); sys.exit(1)
print('mainnet docs deterministic')
