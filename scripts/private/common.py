from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[2]
PRIVATE = ROOT/'.private'
QA = ROOT/'qa'
AGIALPHA = '0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha256_bytes(data: bytes) -> str: return '0x' + hashlib.sha256(data).hexdigest()
def sha256_file(path: pathlib.Path) -> str: return sha256_bytes(path.read_bytes())
def git_commit():
    try: return subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    except Exception: return 'UNKNOWN'
def read_json(path: pathlib.Path) -> dict:
    try: return json.loads(path.read_text())
    except Exception: return {}
def write_json(path: pathlib.Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, indent=2)+'\n')
def load_env(path: pathlib.Path) -> dict:
    env={}
    if path.exists():
        for line in path.read_text().splitlines():
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k,v=line.split('=',1); env[k.strip()]=v.strip()
    return env
def public_base():
    return {'redacted': True, 'containsSecrets': False, 'containsPrivateAddresses': False, 'chain':'ethereum', 'chainId':1, 'agialphaToken':AGIALPHA, 'commit':git_commit(), 'generatedAt':now()}
def parser():
    p=argparse.ArgumentParser(); p.add_argument('--env', default='.private/mainnet-operator.env'); p.add_argument('--input', default='.private/mainnet-operator-input.json'); return p
