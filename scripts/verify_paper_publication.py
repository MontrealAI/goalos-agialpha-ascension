#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PAPER_ROOT = ROOT / 'docs/papers/sovereign-rsi'
V63 = PAPER_ROOT / 'v6.3'
CANONICAL = [
    'GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.md',
    'GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.pdf',
    'GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.docx',
    'GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.tex',
]
SECRET_PATTERNS = [
    re.compile(r'(PRIVATE_KEY|SEED_PHRASE|MNEMONIC|ETHERSCAN_API_KEY)\s*[:=]\s*(?!$|<|process\.env|PRIVATE_LOCAL_ONLY)[^\s"\']+', re.I),
    re.compile(r'https?://[^\s"\']*(alchemy|infura|quicknode|ankr|blast|drpc|chainstack)[^\s"\']+', re.I),
]
errors: list[str] = []
def require(path: Path, label: str) -> None:
    if not path.exists(): errors.append(f'missing {label}: {path.relative_to(ROOT)}')
require(V63 / 'README.md', 'v6.3 README')
for name in CANONICAL: require(V63 / name, name)
require(V63 / 'PAPER_ASSET_MANIFEST.json', 'paper asset manifest')
require(V63 / 'CHECKSUMS.sha256', 'checksums')
# Check checksum file.
if (V63 / 'CHECKSUMS.sha256').exists():
    for i, line in enumerate((V63 / 'CHECKSUMS.sha256').read_text().splitlines(), 1):
        if not line.strip(): continue
        parts = line.split()
        if len(parts) < 2:
            errors.append(f'CHECKSUMS.sha256:{i}: malformed line')
            continue
        expected, rel = parts[0], parts[-1]
        path = ROOT / rel
        if not path.exists():
            errors.append(f'checksum target missing: {rel}')
        else:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected: errors.append(f'checksum mismatch: {rel}')
# Check manifest hashes.
if (V63 / 'PAPER_ASSET_MANIFEST.json').exists():
    manifest = json.loads((V63 / 'PAPER_ASSET_MANIFEST.json').read_text())
    if manifest.get('version') != 'v6.3' or manifest.get('canonical') is not True: errors.append('manifest is not canonical v6.3')
    boundary = manifest.get('claimBoundary', {})
    for key in ['achievedAGI','achievedASI','achievedSuperintelligence','empiricalSOTA','guaranteedEconomicReturn','legalApproval','taxApproval','securityApproval','energyAbundance','kardashevTypeIIAchieved']:
        if boundary.get(key) is not False: errors.append(f'manifest claimBoundary.{key} must be false')
    for entry in manifest.get('files', []):
        p = V63 / entry.get('path', '')
        if not p.exists(): errors.append(f'manifest file missing: {entry.get("path")}')
        elif hashlib.sha256(p.read_bytes()).hexdigest() != entry.get('sha256'): errors.append(f'manifest sha mismatch: {entry.get("path")}')
# README links.
readme = (V63 / 'README.md').read_text(encoding='utf-8', errors='ignore') if (V63 / 'README.md').exists() else ''
for name in CANONICAL:
    link = f'./{name}'
    if link not in readme: errors.append(f'v6.3 README missing exact link: {link}')
    if not (V63 / name).exists(): errors.append(f'v6.3 README link target missing: {link}')
root_readme = (ROOT / 'README.md').read_text(encoding='utf-8', errors='ignore') if (ROOT / 'README.md').exists() else ''
if '## Research paper' not in root_readme or 'docs/papers/sovereign-rsi/v6.3/GoalOS_native_alpha_AGI_Ascension_using_AGIALPHA_v6.3_Sovereign_RSI.md' not in root_readme:
    errors.append('root README missing research-paper section/link to v6.3')
for child in V63.iterdir() if V63.exists() else []:
    n = child.name
    if 'Paper_v5' in n: errors.append(f'v5 file incorrectly in v6.3 root: {n}')
    if 'v6.1' in n: errors.append(f'v6.1 file incorrectly in v6.3 root: {n}')
for ver, pattern in [('v5','*Paper_v5.*'), ('v6.1','*v6.1_Sovereign_RSI.*')]:
    if not list((PAPER_ROOT / 'archive' / ver).glob(pattern)): errors.append(f'older version not archived under archive/{ver}')
if 'This paper does not claim achieved AGI, ASI, superintelligence' not in readme:
    errors.append('claim boundary missing from v6.3 README')
for path in list(V63.glob('*')) + list((PAPER_ROOT / 'archive').rglob('*')):
    if path.is_file() and path.suffix.lower() in {'.md','.tex','.json','.sha256'}:
        text = path.read_text(encoding='utf-8', errors='ignore')
        for pat in SECRET_PATTERNS:
            if pat.search(text): errors.append(f'potential private secret in paper file: {path.relative_to(ROOT)}')
out = {'status': 'PASSED' if not errors else 'FAILED', 'errors': errors, 'paperFolder': str(V63.relative_to(ROOT)), 'canonicalAssets': CANONICAL}
print(json.dumps(out, indent=2))
if errors: sys.exit(1)
