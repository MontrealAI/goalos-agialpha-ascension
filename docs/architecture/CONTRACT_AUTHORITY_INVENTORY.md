# Contract Authority Inventory

Generated authority inventory is machine-bound in `qa/mainnet-readiness/system-inventory.json` and legacy compatible `qa/mainnet-operational-inventory.json`. The readiness pipeline is fail-closed: any unclassified managed contract, mutating selector, role, deployment alias, or release-relevant dirty path blocks authorization instead of being inferred as safe.
