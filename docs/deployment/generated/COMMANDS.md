# Generated deployment commands

Package version: 4.4.0

Last verified commit: current Git HEAD (run git rev-parse HEAD)

| Command | Implementation |
|---|---|
| npm run deploy | ts-node scripts/deployment/goalos-deploy-wizard.ts |
| npm run deploy:broadcast | ts-node scripts/deployment/goalos-deploy-wizard.ts broadcast |
| npm run deploy:doctor | ts-node scripts/deployment/goalos-deploy-wizard.ts doctor |
| npm run deploy:ethereum-mainnet:gated | hardhat run scripts/deploy-ethereum-mainnet-gated.ts --network ethereumMainnet |
| npm run deploy:ethereum-mainnet:gated:local | python scripts/private/run-final-local-mainnet-deployment.py --env .private/mainnet-operator.env --input .private/mainnet-operator-input.json |
| npm run deploy:ethereum-sepolia | hardhat run scripts/deploy-ethereum-sepolia.ts --network ethereumSepolia |
| npm run deploy:evidence | ts-node scripts/deployment/goalos-deploy-wizard.ts evidence |
| npm run deploy:handoff | ts-node scripts/deployment/goalos-deploy-wizard.ts handoff |
| npm run deploy:mainnet | ts-node scripts/deployment/goalos-deploy-wizard.ts mainnet |
| npm run deploy:mainnet:activate-ledger | ts-node scripts/deployment/goalos-deploy-command-center.ts mainnet:activate-ledger --network ethereumMainnet |
| npm run deploy:mainnet:doctor | ts-node scripts/deployment/goalos-deploy-command-center.ts mainnet:doctor --network ethereumMainnet |
| npm run deploy:mainnet:dormant:live-and-verify | python scripts/dormant_mainnet.py live-and-verify |
| npm run deploy:mainnet:dormant:live-local-gated | python scripts/dormant_mainnet.py live-local-gated |
| npm run deploy:mainnet:dormant:postcheck | python scripts/dormant_mainnet.py postdeploy |
| npm run deploy:mainnet:dormant:prepare | python scripts/dormant_mainnet.py prepare |
| npm run deploy:mainnet:dormant:recover | python scripts/dormant_mainnet.py recover |
| npm run deploy:mainnet:dormant:status | python scripts/dormant_mainnet.py status |
| npm run deploy:mainnet:evidence | ts-node scripts/deployment/goalos-deploy-command-center.ts mainnet:evidence --network ethereumMainnet |
| npm run deploy:mainnet:fork-rehearsal | npm run mainnet:fork-simulate |
| npm run deploy:mainnet:full-local-gated | npm run deploy:mainnet:doctor && npm run deploy:mainnet:preflight && npm run deploy:mainnet:fork-rehearsal && npm run deploy:mainnet:prepare-local && npm run deploy:mainnet:live-local-gated && npm run verify:mainnet:all && npm run deploy:mainnet:evidence |
| npm run deploy:mainnet:initial:live-local-gated | python scripts/initial_mainnet_profile.py live-local-gated |
| npm run deploy:mainnet:initial:postcheck | python scripts/initial_mainnet_profile.py postcheck |
| npm run deploy:mainnet:initial:prepare-local | python scripts/initial_mainnet_profile.py prepare |
| npm run deploy:mainnet:initial:recover | python scripts/initial_mainnet_profile.py recover |
| npm run deploy:mainnet:initial:status | python scripts/initial_mainnet_profile.py status |
| npm run deploy:mainnet:initial:verify | python scripts/initial_mainnet_profile.py verify |
| npm run deploy:mainnet:live-local-gated | npm run deploy:ethereum-mainnet:gated |
| npm run deploy:mainnet:postcheck | ts-node scripts/deployment/goalos-deploy-command-center.ts mainnet:postcheck --network ethereumMainnet |
| npm run deploy:mainnet:preflight | ts-node scripts/deployment/goalos-deploy-command-center.ts mainnet:preflight --network ethereumMainnet --no-broadcast && npm run preflight:ethereum-mainnet |
| npm run deploy:mainnet:prepare-local | ts-node scripts/deployment/goalos-deploy-command-center.ts mainnet:prepare-local --network ethereumMainnet --no-broadcast |
| npm run deploy:mainnet:recover | ts-node scripts/deployment/goalos-deploy-command-center.ts mainnet:recover --network ethereumMainnet |
| npm run deploy:mainnet:resume | ts-node scripts/deployment/goalos-deploy-wizard.ts resume --network ethereumMainnet |
| npm run deploy:mainnet:status | ts-node scripts/deployment/goalos-deploy-wizard.ts status |
| npm run deploy:mainnet:verify | npm run verify:mainnet |
| npm run deploy:next | ts-node scripts/deployment/goalos-deploy-command-center.ts next |
| npm run deploy:plan | ts-node scripts/deployment/goalos-deploy-wizard.ts plan |
| npm run deploy:rehearse | ts-node scripts/deployment/goalos-deploy-wizard.ts rehearse |
| npm run deploy:report | ts-node scripts/deployment/goalos-deploy-wizard.ts report |
| npm run deploy:resume | ts-node scripts/deployment/goalos-deploy-wizard.ts resume |
| npm run deploy:sepolia | ts-node scripts/deployment/goalos-deploy-wizard.ts sepolia |
| npm run deploy:sepolia:doctor | ts-node scripts/deployment/goalos-deploy-command-center.ts sepolia:doctor --network ethereumSepolia |
| npm run deploy:sepolia:dry-run | ts-node scripts/deployment/goalos-deploy-command-center.ts sepolia:dry-run --network ethereumSepolia --dry-run --no-broadcast |
| npm run deploy:sepolia:evidence | ts-node scripts/deployment/goalos-deploy-command-center.ts sepolia:evidence --network ethereumSepolia |
| npm run deploy:sepolia:full | npm run deploy:sepolia:doctor && npm run deploy:sepolia:dry-run && npm run deploy:sepolia:live && npm run verify:sepolia:all && npm run deploy:sepolia:evidence |
| npm run deploy:sepolia:live | npm run deploy:ethereum-sepolia |
| npm run deploy:sepolia:verify | npm run verify:sepolia |
| npm run deploy:setup | ts-node scripts/deployment/goalos-deploy-wizard.ts setup |
| npm run deploy:status | ts-node scripts/deployment/goalos-deploy-wizard.ts status |
| npm run deploy:test | node scripts/deployment/test-deployment-safety.js |
| npm run deploy:verify | ts-node scripts/deployment/goalos-deploy-wizard.ts verify |
| npm run docs:deployment:build | node scripts/deployment/build-deployment-docs.js |
| npm run docs:deployment:check | node scripts/deployment/check-deployment-docs.js |
| npm run docs:deployment:examples | node scripts/deployment/check-deployment-docs.js --examples |
| npm run docs:deployment:links | node scripts/deployment/check-deployment-docs.js --links |
