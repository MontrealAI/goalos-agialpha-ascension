#!/usr/bin/env python3
from __future__ import annotations
MENU=[
('Check public repo status','npm run mainnet:status'),
('Run local public checks','npm run mainnet:local-checks'),
('Run automated/internal security toolchain','npm run mainnet:security'),
('Run local deterministic rehearsal','npm run mainnet:local-rehearsal'),
('Run public AGIALPHA token verification','npm run verify:agialpha-token:public'),
('Generate Mainnet Authorization Certificate','npm run mainnet:certificate'),
('Compute technical readiness','npm run mainnet:readiness-check'),
('Compute deployment authorization','npm run mainnet:deployment-authorization-check'),
('Compute Ethereum Mainnet authorization','npm run mainnet:authorization-check'),
('Show final manual deployment command','npm run mainnet:next'),
('Run final local gated deployment','npm run deploy:ethereum-mainnet:gated'),
('Generate post-deployment report','python scripts/generate-public-post-deployment-report.py'),
]
print('GoalOS AGIALPHA Ethereum Mainnet Command Center')
print('Public authorization is certificate-based. Runtime RPC/key stay local and are required only for an actual manual broadcast.')
for i,(label,cmd) in enumerate(MENU,1): print(f'{i}. {label}\n   {cmd}')
