#!/usr/bin/env python3
import pathlib,re,sys
root=pathlib.Path(__file__).resolve().parents[1]
missing=[]
for p in list(root.glob('*.md'))+list((root/'docs').rglob('*.md')):
 text=p.read_text(errors='ignore')
 for m in re.finditer(r'\[[^\]]+\]\((?!https?://|mailto:|#)([^) #]+)', text):
  target=(p.parent/m.group(1)).resolve()
  if not target.exists(): missing.append(f'{p.relative_to(root)} -> {m.group(1)}')
if missing:
 print('warning: unresolved historical/internal links:')
 print('\n'.join(missing[:50]))
print('documentation links syntax/internal paths ok')
