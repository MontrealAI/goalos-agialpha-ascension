# Deployment Guide

## 1. What you are about to do
Run boring, explicit Hardhat deployment commands through the GoalOS AGIALPHA Deployment Command Center.

## 2. What you need
A private RPC URL, a funded deployer wallet, local env file, and optional Etherscan API key.

## 3. What not to do
Never commit secrets. Never broadcast Mainnet from CI. Never use MockAGIALPHA on Mainnet.

## 4. Copy-paste commands
See `docs/DEPLOYMENT_START_HERE.md` for the shortest safe Sepolia and Mainnet command paths.

## 5. How to know it worked
PASS statuses, expected chain ID, generated manifest, generated evidence, and verification report.

## 6. What to do if it fails
Run `npm run deploy:doctor` or the network-specific doctor and follow each printed Next action.

## 7. What the generated files mean
Manifests contain addresses and transaction hashes. Evidence dockets explain mechanics and boundaries. Reports are public-safe summaries.

## 8. What you can safely share
Public addresses, transaction hashes, hashes, reports, and verification status.

## 9. What must remain private
Private keys, RPC URLs, mnemonics, seeds, and filled `.private` files.

## 10. Final claim boundary
This evidence reports deployment mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, or production safety.
