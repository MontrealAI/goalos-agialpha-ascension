# Release Checklist — Mainnet Authorization v4.4.0

- [x] Package version aligned to `4.4.0`.
- [x] Mainnet authorization certificate generated.
- [x] Certificate validation passes in git checkout mode.
- [x] Certificate validation supports source archives without `.git` history.
- [x] QA manifests refreshed.
- [x] Public status assertions preserve YES/YES/YES/NO.
- [x] Sovereign RSI v6.3 paper assets are published and verified.
- [x] Branch protection hardening next action documented.
- [ ] Owner may create tag `mainnet-authorization-v4.4.0` after PR merge.
- [ ] Before actual broadcast, owner should complete optional branch-protection hardening and run `npm run deploy:ethereum-mainnet:gated` locally with runtime RPC/key.
