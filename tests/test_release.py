import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.release import apply_release, detect_changed_components, main, plan_release
from scripts.versioning_lib import COMPONENTS


class ReleaseTests(unittest.TestCase):
    def run_git(self, root: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=True
        )
        return completed.stdout.strip()

    def make_repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        plugin_root = root / "plugins" / "qfin-list-page"
        (plugin_root / ".codex-plugin").mkdir(parents=True)
        (plugin_root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "qfin-list-page", "version": "0.1.0"}, indent=2) + "\n",
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
                {"schemaVersion": 1, "pluginVersion": "0.1.0", "components": versions},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 0.1.0 - 2026-10-14\n\n- Initial.\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("fixture\n", encoding="utf-8")
        self.run_git(root, "init", "-b", "main")
        self.run_git(root, "config", "user.name", "Test")
        self.run_git(root, "config", "user.email", "test@example.com")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "baseline")
        return root

    def edit_component(self, root: Path, alias: str, text: str = "changed\n") -> None:
        path = (
            root
            / "plugins"
            / "qfin-list-page"
            / "skills"
            / COMPONENTS[alias]
            / "SKILL.md"
        )
        path.write_text(text, encoding="utf-8")

    def all_file_bytes(self, root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }

    def test_yushu_only_plan_bumps_yushu_and_plugin_patch(self):
        root = self.make_repo()
        self.edit_component(root, "yushu")

        changed, unrelated = detect_changed_components(root)
        plan = plan_release(root, ("yushu",), "patch", "Fix filters")

        self.assertEqual(changed, {"yushu"})
        self.assertEqual(unrelated, [])
        self.assertEqual(str(plan.current.components["yushu"]), "1.3.2")
        self.assertEqual(str(plan.target.components["yushu"]), "1.3.3")
        self.assertEqual(str(plan.current.plugin), "0.1.0")
        self.assertEqual(str(plan.target.plugin), "0.1.1")
        self.assertEqual(str(plan.target.components["jinyumeng"]), "0.7.2")
        self.assertEqual(plan.tag, "v0.1.1")

    def test_router_alias_and_multiple_components_update_only_named_components(self):
        root = self.make_repo()
        self.edit_component(root, "router")
        self.edit_component(root, "dianxiao")

        plan = plan_release(
            root,
            ("router", "dianxiao"),
            "minor",
            "Add shared behavior",
        )

        self.assertEqual(str(plan.target.components["router"]), "0.2.0")
        self.assertEqual(str(plan.target.components["dianxiao"]), "0.2.0")
        self.assertEqual(str(plan.target.components["yushu"]), "1.3.2")
        self.assertEqual(str(plan.target.components["jinyumeng"]), "0.7.2")

    def test_invalid_or_unsafe_release_inputs_fail_closed(self):
        cases = []

        clean = self.make_repo()
        cases.append((clean, ("yushu",), "patch", None, "no component changes"))

        unrelated = self.make_repo()
        (unrelated / "README.md").write_text("dirty\n", encoding="utf-8")
        cases.append((unrelated, ("yushu",), "patch", None, "unrelated changes"))

        undeclared = self.make_repo()
        self.edit_component(undeclared, "yushu")
        cases.append((undeclared, ("dianxiao",), "patch", None, "changed components"))

        invalid_bump = self.make_repo()
        self.edit_component(invalid_bump, "yushu")
        cases.append((invalid_bump, ("yushu",), "micro", None, "invalid version bump"))

        lower_plugin = self.make_repo()
        self.edit_component(lower_plugin, "yushu")
        cases.append((lower_plugin, ("yushu",), "minor", "patch", "plugin bump"))

        existing_tag = self.make_repo()
        self.edit_component(existing_tag, "yushu")
        self.run_git(existing_tag, "tag", "v0.1.1")
        cases.append((existing_tag, ("yushu",), "patch", None, "already exists"))

        newer_tag = self.make_repo()
        self.edit_component(newer_tag, "yushu")
        self.run_git(newer_tag, "tag", "v0.2.0")
        cases.append((newer_tag, ("yushu",), "patch", None, "not newer"))

        for root, components, bump, plugin_bump, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                plan_release(
                    root,
                    components,
                    bump,
                    "Release note",
                    plugin_bump=plugin_bump,
                )

    def test_cli_defaults_to_dry_run_without_writes_commits_or_tags(self):
        root = self.make_repo()
        self.edit_component(root, "yushu")
        before = self.all_file_bytes(root)
        head = self.run_git(root, "rev-parse", "HEAD")
        tags = self.run_git(root, "tag", "--list")

        result = main(
            ["--component", "yushu", "--bump", "patch", "--note", "Fix filters"],
            repo_root=root,
        )

        self.assertEqual(result, 0)
        self.assertEqual(self.all_file_bytes(root), before)
        self.assertEqual(self.run_git(root, "rev-parse", "HEAD"), head)
        self.assertEqual(self.run_git(root, "tag", "--list"), tags)

    def test_apply_updates_only_release_metadata_and_never_commits_or_tags(self):
        root = self.make_repo()
        self.edit_component(root, "yushu")
        plan = plan_release(root, ("yushu",), "patch", "Fix filters")
        head = self.run_git(root, "rev-parse", "HEAD")

        apply_release(root, plan)

        status_paths = {
            line.split(maxsplit=1)[1]
            for line in self.run_git(root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
        }
        self.assertEqual(
            status_paths,
            {
                "CHANGELOG.md",
                "plugins/qfin-list-page/.codex-plugin/plugin.json",
                "plugins/qfin-list-page/skills/qifu-yushu-list-page/SKILL.md",
                "plugins/qfin-list-page/skills/qifu-yushu-list-page/VERSION",
                "versions.json",
            },
        )
        self.assertEqual(
            (
                root
                / "plugins/qfin-list-page/skills/qifu-yushu-list-page/VERSION"
            ).read_text(encoding="utf-8"),
            "1.3.3\n",
        )
        self.assertEqual(
            json.loads((root / "plugins/qfin-list-page/.codex-plugin/plugin.json").read_text())[
                "version"
            ],
            "0.1.1",
        )
        self.assertEqual(self.run_git(root, "rev-parse", "HEAD"), head)
        self.assertEqual(self.run_git(root, "tag", "--list"), "")


if __name__ == "__main__":
    unittest.main()
