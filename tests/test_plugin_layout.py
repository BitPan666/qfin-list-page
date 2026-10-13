import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "qfin-list-page"
MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"


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


if __name__ == "__main__":
    unittest.main()
