# Deployment Claim Boundary

## 1. What this does
Defines what deployment evidence may and may not claim.

## 2. What this does not do
It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, or Ethereum Mainnet deployment.

## 3. What you need
Use the deployment command center and evidence files to support only mechanics claims.

## 4. What must stay private
Private keys, RPC URLs, mnemonics, signatures, and filled `.private/` files.

## 5. What is safe to share
Public contract addresses, transaction hashes, manifest hashes, verification reports, and claim-bounded reports after review.

## 6. Copy-paste commands
```bash
npm run deployment:claim-boundary:check
```

## 7. How to know it worked
The command prints `Deployment claim-boundary check passed.`

## 8. What generated files mean
Evidence files describe deployment mechanics. They are not marketing claims.

## 9. What to do if it fails
Remove or correct the unsafe claim, then rerun the check.

## 10. Claim boundary
This evidence reports Ethereum Mainnet deployment, verification, and configuration mechanics only. It does not claim achieved AGI, ASI, superintelligence, guaranteed ROI, legal approval, tax approval, security approval, external audit completion, production safety, user-fund authorization, or production activation.
