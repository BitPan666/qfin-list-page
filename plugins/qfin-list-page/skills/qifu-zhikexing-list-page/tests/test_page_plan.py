import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT.name.removeprefix('qifu-').removesuffix('-list-page')

class PagePlanTests(unittest.TestCase):
    def run_plan(self, **changes):
        spec = {'platform': PLATFORM, 'pageName': '客户列表', 'targetPageId': '3497:651', 'sidePath': ['客户管理', '客户列表'], 'columns': [{'key': 'name', 'label': '姓名'}], 'filters': [], 'data': [{'name': '测试客户'}]}
        spec.update(changes)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'spec.json'; p.write_text(json.dumps(spec))
            r = subprocess.run([sys.executable, str(ROOT / 'scripts/plan_page.py'), '--spec', str(p)], text=True, capture_output=True)
        self.assertTrue(r.stdout.strip(), r.stderr)
        return r.returncode, json.loads(r.stdout)

    def test_valid_request_produces_platform_owned_plan(self):
        code, result = self.run_plan()
        self.assertEqual(code, 0)
        self.assertEqual(result['platform'], PLATFORM)
        self.assertEqual(result['status'], 'PREFLIGHT_REQUIRED')
        self.assertFalse(result['generationValidated'])
        self.assertEqual(result['menuOwnerId'], '6158:1989' if PLATFORM == 'zhineng-yunying' else '3650:998')
        self.assertEqual(result['sourceNodeId'], '6155:1851' if PLATFORM == 'zhineng-yunying' else '5468:3233')
        self.assertEqual(result['modeId'], '2158:0' if PLATFORM == 'zhineng-yunying' else None)

    def test_rejects_foreign_platform_without_fallback(self):
        code, result = self.run_plan(platform='dianxiao')
        self.assertNotEqual(code, 0); self.assertEqual(result['error'], 'PLATFORM_CONFLICT')

    def test_rejects_old_zhikexing_or_foreign_source(self):
        code, result = self.run_plan(sourceNodeId='4892:34812')
        self.assertNotEqual(code, 0); self.assertEqual(result['error'], 'BLOCKED_SOURCE')

    def test_batch_action_does_not_enable_selection(self):
        code, result = self.run_plan(tableActions=['批量导出'])
        self.assertEqual(code, 0); self.assertFalse(result['pageSpec']['tableSelection'])

    def test_dynamic_columns_and_explicit_selection_are_preserved(self):
        columns = [{'key': 'k'+str(i), 'label': '字段'+str(i)} for i in range(6)]
        code, result = self.run_plan(columns=columns, data=[], tableSelection=True)
        self.assertEqual(code, 0); self.assertEqual(result['pageSpec']['columns'], columns)
        self.assertTrue(result['pageSpec']['tableSelection'])

    def test_missing_target_is_blocked_before_any_write(self):
        code, result = self.run_plan(targetPageId=None)
        self.assertNotEqual(code, 0); self.assertEqual(result['error'], 'TARGET_REQUIRED')

    def test_duplicate_column_keys_are_rejected(self):
        code, result = self.run_plan(columns=[{'key':'x','label':'A'},{'key':'x','label':'B'}])
        self.assertNotEqual(code, 0); self.assertEqual(result['error'], 'INVALID_COLUMNS')

    def test_unsupported_mode_and_menu_override_are_rejected(self):
        for field,value,error in [('modeId','5722:0','THEME_PLATFORM_CONFLICT'),('menuOwnerId','5763:1753','MENU_PLATFORM_CONFLICT')]:
            with self.subTest(field=field):
                code, result=self.run_plan(**{field:value})
                self.assertNotEqual(code,0);self.assertEqual(result['error'],error)

if __name__ == '__main__': unittest.main()
