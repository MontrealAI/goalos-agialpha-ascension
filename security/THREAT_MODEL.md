# Threat Model

Primary threats are unauthorized role escalation, replayed or missing proof evidence, unsafe AGIALPHA integration, vault fund release without milestone authority, privacy leakage through on-chain payloads, and premature mainnet deployment. Controls include AccessControl roles, nonzero hash/address validation, SafeERC20 transfers, separate launch gates, evidence dockets, read-only mainnet preflight, and hard blocking of mainnet deployment without complete real gates.
