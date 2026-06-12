# Hardhat Ethereum Mainnet Deployment Guide

Hardhat exposes `ethereumMainnet` without requiring secrets during compile/test. The final command is `npm run deploy:ethereum-mainnet:gated`. It refuses CI, requires chainId 1, exact AGIALPHA token address, public YES decisions, runtime RPC/key, runtime addresses, and typed confirmation.
