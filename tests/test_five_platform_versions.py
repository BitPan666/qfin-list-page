import json
import unittest
from pathlib import Path
import test_release
from scripts.versioning_lib import COMPONENTS, load_version_state, validate_version_state
from scripts.install_version import _historical_state
from scripts.release import plan_release, apply_release
from scripts.versioning_lib import run_command

class FivePlatformVersionTests(unittest.TestCase):
    def setUp(self):
        self.fixture=test_release.ReleaseTests();self.addCleanup(self.fixture.doCleanups)
        self.root=self.fixture.make_repo()

    def extend(self):
        lock=json.loads((self.root/'versions.json').read_text())
        for name in ('qifu-zhikexing-list-page','qifu-zhineng-yunying-list-page'):
            p=self.root/'plugins/qfin-list-page/skills'/name;p.mkdir()
            (p/'VERSION').write_text('0.1.0\n');(p/'SKILL.md').write_text('# child\n')
            lock['components'][name]='0.1.0'
        (self.root/'versions.json').write_text(json.dumps(lock))

    def test_new_aliases_are_available(self):
        self.assertEqual(COMPONENTS.get('zhikexing'),'qifu-zhikexing-list-page')
        self.assertEqual(COMPONENTS.get('zhineng-yunying'),'qifu-zhineng-yunying-list-page')

    def test_six_component_current_repository_is_valid(self):
        self.extend();self.assertEqual(validate_version_state(self.root),[])
        self.assertEqual(len(load_version_state(self.root).components),6)

    def test_missing_new_child_version_fails_with_new_child_present(self):
        self.extend();p=self.root/'versions.json';data=json.loads(p.read_text());del data['components']['qifu-zhikexing-list-page'];p.write_text(json.dumps(data))
        self.assertTrue(validate_version_state(self.root))

    def test_legacy_four_component_repository_remains_supported(self):
        self.assertEqual(validate_version_state(self.root),[])
        self.assertEqual(len(load_version_state(self.root).components),4)

    def test_unknown_extra_component_is_not_treated_as_historical(self):
        p=self.root/'versions.json';data=json.loads(p.read_text());data['components']['surprise']='1.0.0';p.write_text(json.dumps(data))
        self.assertTrue(validate_version_state(self.root))

    def test_new_child_release_bumps_only_selected_component(self):
        self.extend()
        self.fixture.run_git(self.root,'add','.')
        self.fixture.run_git(self.root,'commit','-m','six component baseline')
        child=self.root/'plugins/qfin-list-page/skills/qifu-zhikexing-list-page/SKILL.md'
        child.write_text('# changed child\n')
        plan=plan_release(self.root,('zhikexing',),'patch','Fix candidate preflight')
        self.assertEqual(str(plan.target.components['zhikexing']),'0.1.1')
        self.assertEqual(str(plan.target.components['zhineng-yunying']),'0.1.0')
        apply_release(self.root,plan)
        self.assertEqual(validate_version_state(self.root),[])

    def test_historical_six_component_tag_is_readable(self):
        self.extend()
        p=self.root/'.agents/plugins/marketplace.json';p.parent.mkdir(parents=True);p.write_text('{}')
        self.fixture.run_git(self.root,'add','.')
        self.fixture.run_git(self.root,'commit','-m','six component tag')
        self.fixture.run_git(self.root,'tag','v0.1.0')
        state=_historical_state(self.root,'v0.1.0',run_command)
        self.assertEqual(len(state.components),6)

if __name__=='__main__':unittest.main()
