import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "qfin-list-page"
MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
README_PATH = REPO_ROOT / "README.md"
INTEGRITY_PATH = REPO_ROOT / "docs" / "import-integrity-2026-10-13.md"
VERSIONS_PATH = REPO_ROOT / "versions.json"


class PluginLayoutTests(unittest.TestCase):
    def test_plugin_manifest_contract(self):
        self.assertTrue(MANIFEST_PATH.is_file(), f"missing {MANIFEST_PATH}")
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        versions = json.loads(VERSIONS_PATH.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "qfin-list-page")
        self.assertEqual(manifest["version"], versions["pluginVersion"])
        self.assertEqual(manifest["skills"], "./skills/")
        for forbidden_key in ("apps", "mcpServers", "hooks"):
            self.assertNotIn(forbidden_key, manifest)

    def test_marketplace_contract(self):
        self.assertTrue(MARKETPLACE_PATH.is_file(), f"missing {MARKETPLACE_PATH}")
        marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))

        self.assertEqual(marketplace["name"], "qfin-list-page")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "qfin-list-page")
        self.assertEqual(
            entry["source"],
            {"source": "local", "path": "./plugins/qfin-list-page"},
        )
        self.assertEqual(entry["category"], "Productivity")
        self.assertEqual(
            entry["policy"],
            {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        )

    def test_complete_plugin_contains_exactly_four_skills(self):
        skills_root = PLUGIN_ROOT / "skills"
        actual = {path.name for path in skills_root.iterdir() if path.is_dir()}
        self.assertEqual(
            actual,
            {
                "qfin-list-page",
                "qifu-yushu-list-page",
                "qifu-jinyumeng-list-page",
                "qifu-dianxiao-list-page",
            },
        )

    def test_readme_documents_install_use_and_update_contract(self):
        self.assertTrue(README_PATH.is_file())
        text = README_PATH.read_text(encoding="utf-8")
        for required in (
            "codex plugin marketplace add https://github.com/BitPan666/qfin-list-page.git --ref main",
            "codex plugin add qfin-list-page@qfin-list-page",
            "新任务",
            "$qfin-list-page",
            "毓数",
            "金毓盟",
            "电销",
            "唯一可编辑源",
            "version",
            "cachebuster",
        ):
            self.assertIn(required, text)

    def test_version_management_distribution_layout(self):
        for relative_path in (
            "versions.json",
            "CHANGELOG.md",
            "scripts/release.py",
            "scripts/rollback_skill.py",
            "scripts/install_version.py",
        ):
            self.assertTrue((REPO_ROOT / relative_path).is_file(), f"missing {relative_path}")

    def test_readme_documents_complete_release_and_recovery_workflows(self):
        text = README_PATH.read_text(encoding="utf-8")
        for required in (
            "版本管理流程总览",
            "正常发布流程",
            "单 Skill 恢复流程",
            "整个 Plugin 临时降级流程",
            "python3 scripts/release.py",
            "python3 scripts/rollback_skill.py",
            "python3 scripts/install_version.py --tag",
            "python3 scripts/install_version.py --restore-current",
            "默认都是 dry-run",
            "人工创建 Git 标签",
            "不要直接编辑 Plugin 缓存",
            "新建 Codex 任务",
        ):
            self.assertIn(required, text)

    def test_integrity_record_proves_versioning_did_not_change_skill_trees(self):
        text = INTEGRITY_PATH.read_text(encoding="utf-8")
        self.assertIn("26051cf", text)
        self.assertIn("四个 Skill 树没有变化", text)


if __name__ == "__main__":
    unittest.main()
