#!/usr/bin/env python3
"""Validate a Zhikexing list request and emit a read-only generation plan."""
import argparse
import json
from pathlib import Path

PLATFORM = 'zhikexing'
SOURCE = '5468:3233'
MENU = '3650:998'
MODE = None

class PlanError(ValueError):
    pass

def plan_page(spec):
    if not isinstance(spec, dict): raise PlanError('INVALID_SPEC')
    if spec.get('platform') != PLATFORM: raise PlanError('PLATFORM_CONFLICT')
    if spec.get('sourceNodeId', SOURCE) != SOURCE: raise PlanError('BLOCKED_SOURCE')
    if spec.get('menuOwnerId', MENU) != MENU: raise PlanError('MENU_PLATFORM_CONFLICT')
    if spec.get('modeId', MODE) != MODE: raise PlanError('THEME_PLATFORM_CONFLICT')
    if not isinstance(spec.get('targetPageId'), str) or not spec['targetPageId'].strip(): raise PlanError('TARGET_REQUIRED')
    if not isinstance(spec.get('pageName'), str) or not spec['pageName'].strip(): raise PlanError('PAGE_NAME_REQUIRED')
    path = spec.get('sidePath')
    if not isinstance(path,list) or not 1 <= len(path) <= 3 or not all(isinstance(x,str) and x.strip() for x in path): raise PlanError('NAVIGATION_REQUIRED')
    columns = spec.get('columns')
    if not isinstance(columns,list) or not 1 <= len(columns) <= 8: raise PlanError('INVALID_COLUMNS')
    keys = []
    for col in columns:
        if not isinstance(col,dict) or not isinstance(col.get('key'),str) or not col['key'].strip() or not isinstance(col.get('label'),str) or not col['label'].strip(): raise PlanError('INVALID_COLUMNS')
        keys.append(col['key'])
    if len(set(keys)) != len(keys): raise PlanError('INVALID_COLUMNS')
    if not isinstance(spec.get('tableSelection',False),bool): raise PlanError('INVALID_SELECTION')
    if not isinstance(spec.get('filters',[]),list) or not isinstance(spec.get('data',[]),list): raise PlanError('INVALID_SPEC')
    if any(not isinstance(row,dict) for row in spec.get('data',[])): raise PlanError('INVALID_DATA')
    page = dict(spec);page['tableSelection']=spec.get('tableSelection',False);page['sideActive']=path[-1];page['activeTab']=path[-1]
    return {'status':'PREFLIGHT_REQUIRED','generationValidated':False,'platform':PLATFORM,'sourceNodeId':SOURCE,'shellType':'FRAME','menuOwnerId':MENU,'headerOwnerId':'5517:2109','modeId':MODE,'collectionId':'VariableCollectionId:9:8','sourceReadiness':'candidate','contentStrategy':'clone-verified-candidate-adapt-real-components','contentSourceNodeId':'5468:3255','contentBounds':{'x':216,'y':152,'width':1134,'height':600},'pageSpec':page,'requiredChecks':['source-owner','component-properties','text-styles','semantic-bindings','geometry','screenshot']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--spec',required=True,type=Path);args=parser.parse_args()
    try:
        plan=plan_page(json.loads(args.spec.read_text(encoding='utf-8')))
    except (OSError,ValueError,TypeError) as exc:
        print(json.dumps({'status':'BLOCKED','error':str(exc) if isinstance(exc,PlanError) else 'INVALID_SPEC'},ensure_ascii=False));return 2
    print(json.dumps(plan,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
