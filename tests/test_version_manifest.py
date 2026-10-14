import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.versioning_lib import (
    COMPONENTS,
    SemVer,
    load_version_state,
    read_versions_json,
    snapshot_component_trees,
    validate_version_state,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class SemVerTests(unittest.TestCase):
    def test_semantic_versions_sort_by_major_minor_and_patch(self):
        values = [SemVer.parse(value) for value in ("0.1.0", "0.1.1", "0.2.0", "1.0.0")]
        self.assertEqual(values, sorted(values))
        self.assertEqual(str(values[0].bump("patch")), "0.1.1")
        self.assertEqual(str(values[0].bump("minor")), "0.2.0")
        self.assertEqual(str(values[0].bump("major")), "1.0.0")

    def test_malformed_semantic_versions_fail_closed(self):
        for value in ("1", "v1.0.0", "01.0.0", "1.0"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                SemVer.parse(value)

        with self.assertRaises(ValueError):
            SemVer.parse("1.2.3").bump("micro")


class VersionManifestTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        plugin_root = root / "plugins" / "qfin-list-page"
        (plugin_root / ".codex-plugin").mkdir(parents=True)
        (plugin_root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "qfin-list-page", "version": "0.1.0"}),
            encoding="utf-8",
        )

        versions = {
            "qfin-list-page": "0.1.0",
            "qifu-yushu-list-page": "1.3.2",
            "qifu-jinyumeng-list-page": "0.7.2",
            "qifu-dianxiao-list-page": "0.1.0",
        }
        for directory, version in versions.items():
            skill = plugin_root / "skills" / directory
            skill.mkdir(parents=True)
            (skill / "VERSION").write_text(f"{version}\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(f"# {directory}\n", encoding="utf-8")

        (root / "versions.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "pluginVersion": "0.1.0",
                    "components": versions,
                }
            ),
            encoding="utf-8",
        )
        return root

    def read_lock(self, root: Path) -> dict[str, object]:
        return json.loads((root / "versions.json").read_text(encoding="utf-8"))

    def write_lock(self, root: Path, data: dict[str, object]) -> None:
        (root / "versions.json").write_text(json.dumps(data), encoding="utf-8")

    def test_published_repository_versions_match_every_source(self):
        state = load_version_state(REPO_ROOT)
        lock = read_versions_json(REPO_ROOT)
        raw_components = lock["components"]
        self.assertIsInstance(raw_components, dict)
        self.assertEqual(str(state.plugin), lock["pluginVersion"])
        self.assertEqual(
            {alias: str(version) for alias, version in state.components.items()},
            {
                alias: raw_components[directory]
                for alias, directory in COMPONENTS.items()
            },
        )
        self.assertEqual(validate_version_state(REPO_ROOT), [])

    def test_missing_and_extra_components_are_reported_deterministically(self):
        root = self.make_repo()
        lock = self.read_lock(root)
        components = lock["components"]
        self.assertIsInstance(components, dict)
        del components["qifu-dianxiao-list-page"]
        components["unexpected-skill"] = "0.1.0"
        self.write_lock(root, lock)

        self.assertEqual(
            validate_version_state(root),
            [
                "versions.json components missing: qifu-dianxiao-list-page",
                "versions.json components extra: unexpected-skill",
            ],
        )

    def test_mismatched_versions_are_reported_in_stable_order(self):
        root = self.make_repo()
        lock = self.read_lock(root)
        lock["pluginVersion"] = "0.1.1"
        components = lock["components"]
        self.assertIsInstance(components, dict)
        components["qifu-yushu-list-page"] = "1.3.3"
        self.write_lock(root, lock)

        self.assertEqual(
            validate_version_state(root),
            [
                "plugin version mismatch: versions.json=0.1.1 plugin.json=0.1.0",
                "component version mismatch: yushu versions.json=1.3.3 VERSION=1.3.2",
            ],
        )

    def test_malformed_versions_and_schema_are_reported_without_tracebacks(self):
        root = self.make_repo()
        lock = self.read_lock(root)
        lock["schemaVersion"] = 2
        lock["pluginVersion"] = "v0.1.0"
        components = lock["components"]
        self.assertIsInstance(components, dict)
        components["qifu-jinyumeng-list-page"] = "01.0.0"
        self.write_lock(root, lock)

        self.assertEqual(
            validate_version_state(root),
            [
                "versions.json schemaVersion must be 1",
                "versions.json pluginVersion is invalid: 'v0.1.0'",
                "versions.json component qifu-jinyumeng-list-page is invalid: '01.0.0'",
            ],
        )

    def test_component_snapshots_exclude_only_the_requested_alias_and_do_not_follow_links(self):
        root = self.make_repo()
        cache = root / "plugin-cache"
        cache.mkdir()
        (cache / "secret.txt").write_text("cache material\n", encoding="utf-8")
        router = root / "plugins" / "qfin-list-page" / "skills" / COMPONENTS["router"]
        os.symlink(cache, router / "cache-link")

        manifests = snapshot_component_trees(root, excluded={"yushu"})

        self.assertEqual(set(manifests), {"router", "jinyumeng", "dianxiao"})
        self.assertIn("cache-link", manifests["router"])
        self.assertNotIn("cache-link/secret.txt", manifests["router"])


if __name__ == "__main__":
    unittest.main()
