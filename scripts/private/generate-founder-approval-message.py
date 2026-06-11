#!/usr/bin/env python3
from common import pathlib, parser, read_json, AGIALPHA, git_commit

args = parser().parse_args()
_ = read_json(pathlib.Path(args.input))
print(f'''I approve Ethereum Mainnet deployment authorization for GoalOS AGIALPHA Ascension.

Repository: MontrealAI/goalos-agialpha-ascension
Commit: {git_commit()}
Chain: Ethereum Mainnet
ChainId: 1
AGIALPHA token: {AGIALPHA}
Technical readiness decision hash: <hash>
Automated/internal security clearance hash: <hash>
Sepolia Evidence Docket hash: <hash>
Mainnet preflight hash: <hash>
Address ceremony commitment hash: <hash>
Policy decision commitment hash: <hash>
I understand this repository is not externally audited.
I approve deployment authorization, but not automatic CI deployment.
Date: <date>''')
