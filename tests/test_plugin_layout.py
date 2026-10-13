import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "qfin-list-page"
MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
README_PATH = REPO_ROOT / "README.md"


class PluginLayoutTests(unittest.TestCase):
    def test_plugin_manifest_contract(self):
        self.assertTrue(MANIFEST_PATH.is_file(), f"missing {MANIFEST_PATH}")
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "qfin-list-page")
        self.assertEqual(manifest["version"], "0.1.0")
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
            "codex plugin marketplace add owner/qfin-list-page --ref main",
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


if __name__ == "__main__":
    unittest.main()
