#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.private.owner_config_common import OwnerConfigError, load_b64, validate_config

REQUIRED = ["MAINNET_FORK_RPC_URL", "GOALOS_PRODUCTION_OWNER_KIND", "GOALOS_PRODUCTION_OWNER_ADDRESS", "GOALOS_PRODUCTION_OWNER_CONFIG_B64"]
ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

def main() -> int:
    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        print("OPERATOR_INPUT_REQUIRED")
        print("missing=" + ",".join(missing))
        print("safe_setup=Create/use the protected GitHub Environment `mainnet-readiness` or a local untracked .private/mainnet-readiness.env; store MAINNET_FORK_RPC_URL and GOALOS_PRODUCTION_OWNER_CONFIG_B64 only as secrets; never commit populated private files.")
        print("resume_command=npm run mainnet:fork-rehearsal:release && npm run mainnet:production-readiness && npm run mainnet:certificate:validate && npm run mainnet:final-check")
        return 2
    errors: list[str] = []
    if os.environ["GOALOS_PRODUCTION_OWNER_KIND"] not in {"SAFE", "EOA"}:
        errors.append("GOALOS_PRODUCTION_OWNER_KIND must be SAFE or EOA")
    if not ADDRESS_RE.match(os.environ["GOALOS_PRODUCTION_OWNER_ADDRESS"]):
        errors.append("GOALOS_PRODUCTION_OWNER_ADDRESS must be an Ethereum address")
    funder = os.environ.get("FORK_AGIALPHA_FUNDER")
    if funder and not ADDRESS_RE.match(funder):
        errors.append("FORK_AGIALPHA_FUNDER must be a public Ethereum address when supplied")
    try:
        owner = validate_config(load_b64(os.environ["GOALOS_PRODUCTION_OWNER_CONFIG_B64"]), os.environ["GOALOS_PRODUCTION_OWNER_KIND"], os.environ["GOALOS_PRODUCTION_OWNER_ADDRESS"])
        errors.extend(owner["errors"])
    except OwnerConfigError as exc:
        errors.append(str(exc))
        owner = {"redacted": {}}
    out = {"status": "PASS" if not errors else "FAIL", "errors": errors, "owner": owner.get("redacted", {}), "requiredInputsPresent": True, "broadcastKeyPresent": any("PRIVATE_KEY" in k or "MNEMONIC" in k for k in os.environ)}
    Path("qa/mainnet-readiness").mkdir(parents=True, exist_ok=True)
    Path("qa/mainnet-readiness/release-inputs.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))
    if out["broadcastKeyPresent"]:
        print("Refusing RELEASE_MODE with broadcaster key-like environment variable present")
        return 2
    return 0 if not errors else 2
if __name__ == "__main__": raise SystemExit(main())
