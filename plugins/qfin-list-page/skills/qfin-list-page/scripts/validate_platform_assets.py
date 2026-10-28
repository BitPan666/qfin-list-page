#!/usr/bin/env python3
"""Validate the 2026-10-28 offline asset snapshot; does not enable routes or call Figma."""
import argparse
import json
from pathlib import Path

DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / 'references/platform-assets.json'
COLLECTION = 'VariableCollectionId:9:8'

# These assertions pin independently reviewed evidence. Changing the registry alone
# cannot promote a candidate or swap a platform source. Re-audit before changing them.
COMMON = {
    'yushu': ('3478:657', 'COMPONENT', 1248, 397, 'list-content', '3639:1529', 'COMPONENT_SET', 48, '3650:998', '9:6'),
    'jinyumeng': ('5022:16', 'COMPONENT', 1366, 1024, 'full-app', '4993:1440', 'COMPONENT', 56, '4746:46261', '4717:0'),
    'dianxiao': ('5829:31', 'COMPONENT', 1366, 768, 'full-app', '5824:4491', 'COMPONENT', 56, '5763:1753', '5722:0'),
    'zhikexing': ('5468:3233', 'FRAME', 1366, 768, 'full-app-candidate', '5517:2109', 'COMPONENT_SET', 48, '3650:998', None),
    'zhineng-yunying': ('6155:1851', 'FRAME', 1366, 768, 'full-app', '6148:32454', 'FRAME', 48, '6158:1989', '2158:0'),
}
RUNTIME_PLATFORMS = ('yushu', 'jinyumeng', 'dianxiao')


def _expect(record, path, expected, errors, prefix):
    value = record
    for key in path.split('.'):
        if not isinstance(value, dict) or key not in value:
            errors.append(f'{prefix}.{path}: missing audited field')
            return
        value = value[key]
    if type(value) is not type(expected) or value != expected:
        errors.append(f'{prefix}.{path}: expected {expected!r}, got {value!r}')


def validate(registry):
    """Return deterministic errors for missing, foreign, or overclaimed asset facts."""
    errors = []
    if not isinstance(registry, dict):
        return ['registry: expected an object']
    for path, expected in {
        'schemaVersion': 1, 'audit.date': '2026-10-28',
        'audit.fileKey': 'gTV3VdC6a5e9vpkRHIZSXA',
        'audit.scope': 'asset-facts-only', 'defaultPlatform': None,
    }.items():
        _expect(registry, path, expected, errors, 'registry')
    platforms = registry.get('platforms')
    if not isinstance(platforms, dict):
        return errors + ['platforms: expected an object with exactly five platforms']
    if set(platforms) != set(COMMON):
        errors.append('platforms: expected exactly ' + ', '.join(COMMON))
    for platform, facts in COMMON.items():
        record = platforms.get(platform)
        if not isinstance(record, dict):
            errors.append(f'{platform}: missing platform object')
            continue
        shell, node_type, width, height, scope, header, header_type, header_height, menu, mode = facts
        expected = {
            'shell.id': shell, 'shell.type': node_type, 'shell.width': width,
            'shell.height': height, 'shell.scope': scope,
            'header.id': header, 'header.type': header_type,
            'header.width': 1366, 'header.height': header_height,
            'menu.ownerId': menu, 'menu.type': 'COMPONENT_SET',
            'theme.collectionId': COLLECTION, 'theme.modeId': mode,
            'theme.strategy': 'inherit-verified-template-bindings' if mode is None else 'explicit-platform-mode',
            'runtime.status': 'existing-child' if platform in RUNTIME_PLATFORMS else 'pending-adapter',
            'runtime.childSkill': f'qifu-{platform}-list-page' if platform in RUNTIME_PLATFORMS else None,
            'readiness': 'existing-child-not-revalidated' if platform in RUNTIME_PLATFORMS else ('candidate' if platform == 'zhikexing' else 'shell-audited'),
            'generationValidatedInAudit': False,
        }
        if platform in ('yushu', 'zhikexing'):
            expected.update({'menu.itemWidth': 200, 'menu.observedItemHeights': [44, 40]})
        else:
            expected.update({'menu.itemWidth': 208 if platform == 'jinyumeng' else 200,
                             'menu.itemHeight': 48 if platform == 'jinyumeng' else 40,
                             'menu.variantCount': 36 if platform == 'dianxiao' else 24})
        if platform == 'yushu':
            expected.update({'content.strategy': 'compose-platform-navigation-and-content-slots',
                             'content.slotIds': ['3479:2', '3479:3', '3479:4']})
        elif platform in ('jinyumeng', 'dianxiao'):
            ids = ['5022:3', '5022:4', '5022:5', '5022:6'] if platform == 'jinyumeng' else ['5829:16', '5829:17', '5829:19']
            expected.update({'content.strategy': 'native-slots', 'content.slotIds': ids,
                             'content.id': '5022:2' if platform == 'jinyumeng' else '5829:15',
                             'content.type': 'COMPONENT'})
            if platform == 'dianxiao':
                expected.update({'menu.rootOwnerId': '5762:1537'})
        elif platform == 'zhineng-yunying':
            expected.update({'content.id': '6148:34365', 'content.type': 'RECTANGLE',
                             'content.x': 216, 'content.y': 102, 'content.width': 1134,
                             'content.height': 633, 'content.strategy': 'clone-frame-create-content-container-on-copy',
                             'content.requiresShellRebuild': False, 'content.nativeSlot': False,
                             'tabs.id': '6156:1989', 'tabs.type': 'FRAME', 'tabs.width': 1134, 'tabs.height': 38,
                             'menu.levels': [1, 2], 'menu.currentInstanceCount': 17,
                             'menu.observedPropertyKeys': ['Label#5763:0', 'showIcon 显示图标#5763:37', 'icon 图标#5763:74'],
                             'visibleUnstyledTextCount': 7})
        else:
            expected.update({'header.actualItems': '0', 'header.instanceNameItems': '5',
                             'visibleUnstyledTextCount': 50,
                             'content.strategy': 'candidate-only-no-generation-adapter',
                             'manualCandidate.id': '5408:13969', 'manualCandidate.type': 'FRAME',
                             'manualCandidate.width': 1366, 'manualCandidate.height': 768,
                             'legacyRejected.id': '4892:34812', 'legacyRejected.type': 'FRAME',
                             'legacyRejected.width': 1366, 'legacyRejected.height': 768,
                             'legacyRejected.headerOwnerId': '3639:1529',
                             'legacyRejected.eligibleDefault': False,
                             'theme.observedInheritedModeId': '9:6'})
        for path, value in expected.items():
            _expect(record, path, value, errors, platform)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    try:
        registry = json.loads(args.registry.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        print(f'FAIL: registry: {error}')
        return 1
    errors = validate(registry)
    if errors:
        for error in errors:
            print(f'FAIL: {error}')
        return 1
    print('PASS: 5 platforms; 3 runtime routes; asset facts only, no page acceptance claim')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
