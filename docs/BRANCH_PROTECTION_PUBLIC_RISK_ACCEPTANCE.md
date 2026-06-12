# Branch Protection Public Risk Acceptance

GitHub branch-protection/ruleset state may not be readable from unauthenticated public CI. Until live ruleset evidence is attached, public governance accepts this explicit public risk record as the deployment-authorization governance fallback.

Required protections remain: pull request before merge, required status checks, no force pushes, no branch deletion, conversation resolution, and CODEOWNER/sensitive-path review where possible.

This risk acceptance may support `MAINNET_DEPLOYMENT_AUTHORIZED: YES` only when all technical gates pass and no critical/high blockers remain. It does not authorize CI deployment and does not store runtime secrets.
