#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from common import write_text, utc_now
p=argparse.ArgumentParser(); p.add_argument('--dir', type=Path, required=True); a=p.parse_args(); write_text(a.dir/'ChronicleEntry.md', f'# Chronicle Entry\n\nGenerated: {utc_now()}\n\nReusable proof-to-action mission memory.\n')
