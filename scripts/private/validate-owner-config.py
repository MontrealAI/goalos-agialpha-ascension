#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.private.owner_config_common import OwnerConfigError, load_b64, validate_config

def main() -> int:
    p = argparse.ArgumentParser(description="Validate GoalOS private owner config without printing private JSON")
    p.add_argument("--config-b64", default=os.environ.get("GOALOS_PRODUCTION_OWNER_CONFIG_B64"))
    p.add_argument("--kind", default=os.environ.get("GOALOS_PRODUCTION_OWNER_KIND"))
    p.add_argument("--address", default=os.environ.get("GOALOS_PRODUCTION_OWNER_ADDRESS"))
    p.add_argument("--out")
    args = p.parse_args()
    if not args.config_b64:
        print(json.dumps({"status":"OPERATOR_INPUT_REQUIRED","missing":["GOALOS_PRODUCTION_OWNER_CONFIG_B64"]}, indent=2)); return 2
    try:
        data = load_b64(args.config_b64)
        result = validate_config(data, args.kind, args.address)
    except OwnerConfigError as exc:
        print(json.dumps({"status":"FAIL","error":str(exc)}, indent=2)); return 2
    public = result["redacted"] | {"status": "PASS" if result["valid"] else "FAIL", "errors": result["errors"]}
    text = json.dumps(public, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True); Path(args.out).write_text(text + "\n")
    print(text)
    return 0 if result["valid"] else 2
if __name__ == "__main__": raise SystemExit(main())
