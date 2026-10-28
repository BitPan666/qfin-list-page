"""Offline mutation tests for the audited asset boundary, independent of routing."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'references/platform-assets.json'
VALIDATOR = ROOT / 'scripts/validate_platform_assets.py'


class PlatformAssetTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(VALIDATOR.is_file(), 'five-platform asset validator is missing')
        self.assertTrue(REGISTRY.is_file(), 'five-platform asset registry is missing')
        spec = importlib.util.spec_from_file_location('platform_assets', VALIDATOR)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.data = json.loads(REGISTRY.read_text(encoding='utf-8'))

    def reject(self, mutate, expected):
        data = copy.deepcopy(self.data)
        mutate(data)
        errors = self.module.validate(data)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_audited_registry_passes_without_network(self):
        self.assertEqual(self.module.validate(self.data), [])

    def test_cli_accepts_registry_argument(self):
        result = subprocess.run([sys.executable, str(VALIDATOR), '--registry', str(REGISTRY)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('5 platforms; 3 runtime routes', result.stdout)

    def test_cli_missing_registry_fails_without_traceback(self):
        result = subprocess.run([sys.executable, str(VALIDATOR), '--registry', '/nonexistent/platform-assets.json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stderr)

    def test_cli_rejects_mutated_registry(self):
        self.data['platforms']['zhineng-yunying']['menu']['ownerId'] = '5763:1753'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'assets.json'
            path.write_text(json.dumps(self.data))
            result = subprocess.run([sys.executable, str(VALIDATOR), '--registry', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('menu.ownerId', result.stdout)

    def test_missing_platform_is_rejected(self):
        self.reject(lambda d: d['platforms'].pop('zhikexing'), 'platforms')

    def test_cross_platform_shell_is_rejected(self):
        self.reject(lambda d: d['platforms']['jinyumeng'].__setitem__('shell', d['platforms']['dianxiao']['shell']), 'shell')

    def test_electric_menu_cannot_own_smartops(self):
        self.reject(lambda d: d['platforms']['zhineng-yunying']['menu'].__setitem__('ownerId', '5763:1753'), 'menu.ownerId')

    def test_smartops_menu_cannot_own_electric(self):
        self.reject(lambda d: d['platforms']['dianxiao']['menu'].__setitem__('ownerId', '6158:1989'), 'menu.ownerId')

    def test_shared_property_suffix_does_not_override_owner(self):
        menu = self.data['platforms']['zhineng-yunying']['menu']
        self.assertIn('Label#5763:0', menu['observedPropertyKeys'])
        self.assertEqual(menu['ownerId'], '6158:1989')
        self.assertEqual(self.module.validate(self.data), [])

    def test_candidate_cannot_be_promoted_to_validated_template(self):
        self.reject(lambda d: d['platforms']['zhikexing'].__setitem__('readiness', 'validated-template'), 'readiness')

    def test_candidate_cannot_enable_runtime_route(self):
        self.reject(lambda d: d['platforms']['zhikexing']['runtime'].__setitem__('status', 'existing-child'), 'runtime')

    def test_no_fallback_child_for_pending_adapter(self):
        self.reject(lambda d: d['platforms']['zhineng-yunying']['runtime'].__setitem__('childSkill', 'qifu-dianxiao-list-page'), 'runtime')

    def test_legacy_zhikexing_cannot_be_default_shell(self):
        self.reject(lambda d: d['platforms']['zhikexing']['shell'].__setitem__('id', '4892:34812'), 'shell')

    def test_legacy_yushu_header_conflict_is_preserved(self):
        self.reject(lambda d: d['platforms']['zhikexing']['legacyRejected'].__setitem__('eligibleDefault', True), 'legacyRejected')

    def test_live_items_value_beats_instance_name(self):
        self.reject(lambda d: d['platforms']['zhikexing']['header'].__setitem__('actualItems', '5'), 'header.actualItems')

    def test_candidate_style_gaps_cannot_disappear(self):
        self.reject(lambda d: d['platforms']['zhikexing'].__setitem__('visibleUnstyledTextCount', 0), 'visibleUnstyledTextCount')

    def test_smartops_frame_cannot_be_native_component(self):
        self.reject(lambda d: d['platforms']['zhineng-yunying']['shell'].__setitem__('type', 'COMPONENT'), 'shell.type')

    def test_smartops_blank_rectangle_cannot_be_slot(self):
        self.reject(lambda d: d['platforms']['zhineng-yunying']['content'].__setitem__('type', 'SLOT'), 'content.type')

    def test_smartops_uses_copy_content_container(self):
        self.reject(lambda d: d['platforms']['zhineng-yunying']['content'].__setitem__('strategy', 'native-slots'), 'content.strategy')

    def test_smartops_must_not_rebuild_shell(self):
        self.reject(lambda d: d['platforms']['zhineng-yunying']['content'].__setitem__('requiresShellRebuild', True), 'requiresShellRebuild')

    def test_smartops_content_bounds_are_audited(self):
        self.reject(lambda d: d['platforms']['zhineng-yunying']['content'].__setitem__('width', 1118), 'content.width')

    def test_full_shell_dimensions_do_not_use_names(self):
        self.reject(lambda d: d['platforms']['jinyumeng']['shell'].__setitem__('height', 768), 'shell.height')

    def test_yushu_content_shell_is_not_full_app(self):
        self.reject(lambda d: d['platforms']['yushu']['shell'].__setitem__('scope', 'full-app'), 'shell.scope')

    def test_menu_variant_dimensions_are_platform_specific(self):
        self.reject(lambda d: d['platforms']['jinyumeng']['menu'].__setitem__('itemWidth', 200), 'menu.itemWidth')

    def test_live_modes_cannot_cross_platforms(self):
        self.reject(lambda d: d['platforms']['dianxiao']['theme'].__setitem__('modeId', '2158:0'), 'theme.modeId')

    def test_zhikexing_cannot_invent_dedicated_mode(self):
        self.reject(lambda d: d['platforms']['zhikexing']['theme'].__setitem__('modeId', '9:6'), 'theme.modeId')

    def test_zhikexing_preserves_verified_template_bindings(self):
        self.reject(lambda d: d['platforms']['zhikexing']['theme'].__setitem__('strategy', 'explicit-mode'), 'theme.strategy')

    def test_malformed_structure_fails_closed(self):
        for value in (None, [], {}, {'schemaVersion': 1, 'platforms': []}):
            with self.subTest(value=value):
                self.assertTrue(self.module.validate(value))


if __name__ == '__main__':
    unittest.main()
