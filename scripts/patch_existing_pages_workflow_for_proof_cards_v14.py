#!/usr/bin/env python3
"""Patch existing Pages workflow for Proof Cards 001-008. Safe to run repeatedly."""
from pathlib import Path
wf = Path('.github/workflows/autonomous-github-pages.yml')
if not wf.exists():
    raise SystemExit('autonomous-github-pages.yml not found')
print('Use the packaged autonomous-github-pages.yml for the canonical patched workflow.')
