# Final Local Pre-Deployment Checklist

- [ ] `npm ci` passed.
- [ ] `npm run mainnet:local-checks` passed.
- [ ] `npm run mainnet:security` completed and unresolved critical/high findings are zero.
- [ ] Local deterministic rehearsal passed.
- [ ] Private Sepolia rehearsal evidence exists locally and only redacted commitments are public.
- [ ] Private Ethereum Mainnet preflight evidence exists locally and only redacted commitments are public.
- [ ] Founder approval commitment exists.
- [ ] Address ceremony commitment exists.
- [ ] Branch protection or founder risk-acceptance commitment exists.
- [ ] `npm run mainnet:final-check` reports YES for technical readiness, deployment authorization, and Ethereum Mainnet authorization.
- [ ] Final execution is local-only, not GitHub Actions.
