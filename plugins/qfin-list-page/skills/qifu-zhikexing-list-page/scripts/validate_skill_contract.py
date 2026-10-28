#!/usr/bin/env python3
"""Validate an independent platform list Skill package."""
import re
import sys
from pathlib import Path

def validate(root):
    errors=[]
    for name in ['SKILL.md','VERSION','scripts/plan_page.py','references/platform-and-components.md','references/validation.md','agents/openai.yaml']:
        if not (root/name).is_file(): errors.append('missing '+name)
    if errors:return errors
    text=(root/'SKILL.md').read_text()
    if not text.startswith('---\nname: '+root.name+'\n'):errors.append('wrong skill name')
    if not re.search(r'^description: Use when',text,re.M):errors.append('missing discovery description')
    if not re.fullmatch(r'\d+\.\d+\.\d+',(root/'VERSION').read_text().strip()):errors.append('invalid version')
    for link in re.findall(r'\[[^]]+\]\(([^)]+)\)',text):
        if not link.startswith(('https://','#')) and not (root/link).exists():errors.append('broken reference '+link)
    return errors

if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    errors=validate(root)
    print('\n'.join('FAIL: '+e for e in errors) if errors else 'PASS: '+root.name+' '+(root/'VERSION').read_text().strip())
    raise SystemExit(bool(errors))
