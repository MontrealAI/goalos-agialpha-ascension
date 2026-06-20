#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys

def run(cmd: list[str]) -> int:
    return subprocess.call(cmd)

def main() -> int:
    rc = run([sys.executable, "scripts/mainnet_release_inputs.py"])
    if rc != 0:
        return rc
    # Delegate to the existing fail-closed readiness generator. It must still
    # require real fork evidence and cannot be converted to PASS by this wrapper.
    return run([sys.executable, "scripts/mainnet_operational_readiness.py", "--validate"])
if __name__ == "__main__": raise SystemExit(main())
