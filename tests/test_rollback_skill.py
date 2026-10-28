import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from scripts.compare_skill_trees import build_manifest
from scripts.rollback_skill import apply_skill_rollback, main, plan_skill_rollback
from scripts.versioning_lib import COMPONENTS, snapshot_component_trees


class RollbackSkillTests(unittest.TestCase):
    def run_git(self, root: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=True
        )
        return completed.stdout.strip()

    def make_repo(
        self,
        *,
        missing_historical_skill: str | None = None,
        missing_historical_version: str | None = None,
    ) -> Path:
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
            "qifu-zhikexing-list-page": "0.1.0",
            "qifu-zhineng-yunying-list-page": "0.1.0",
        }
        for alias, directory in COMPONENTS.items():
            if alias == missing_historical_skill:
                continue
            skill = plugin_root / "skills" / directory
            skill.mkdir(parents=True)
            if alias != missing_historical_version:
                (skill / "VERSION").write_text(f"{versions[directory]}\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(f"historical {alias}\n", encoding="utf-8")
            (skill / "old-only.txt").write_text(f"old {alias}\n", encoding="utf-8")
            (skill / "mode.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            os.chmod(skill / "mode.sh", 0o644)
        (root / "versions.json").write_text(
            json.dumps(
                {"schemaVersion": 1, "pluginVersion": "0.1.0", "components": versions},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        self.run_git(root, "init", "-b", "main")
        self.run_git(root, "config", "user.name", "Test")
        self.run_git(root, "config", "user.email", "test@example.com")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "historical")
        self.run_git(root, "tag", "v0.1.0")

        for alias, directory in COMPONENTS.items():
            skill = plugin_root / "skills" / directory
            skill.mkdir(parents=True, exist_ok=True)
            if not (skill / "VERSION").exists():
                (skill / "VERSION").write_text(f"{versions[directory]}\n", encoding="utf-8")
            if not (skill / "SKILL.md").exists():
                (skill / "SKILL.md").write_text(f"current {alias}\n", encoding="utf-8")
            if not (skill / "old-only.txt").exists():
                (skill / "old-only.txt").write_text(f"old {alias}\n", encoding="utf-8")
            if not (skill / "mode.sh").exists():
                (skill / "mode.sh").write_text("#!/bin/sh\n", encoding="utf-8")
                os.chmod(skill / "mode.sh", 0o644)

        yushu = plugin_root / "skills" / COMPONENTS["yushu"]
        (yushu / "SKILL.md").write_text("current yushu\n", encoding="utf-8")
        (yushu / "new-only.txt").write_text("new yushu\n", encoding="utf-8")
        (yushu / "old-only.txt").unlink(missing_ok=True)
        os.chmod(yushu / "mode.sh", 0o755)
        (yushu / "VERSION").write_text("1.3.3\n", encoding="utf-8")
        versions[COMPONENTS["yushu"]] = "1.3.3"
        manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = "0.1.1"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (root / "versions.json").write_text(
            json.dumps(
                {"schemaVersion": 1, "pluginVersion": "0.1.1", "components": versions},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "current")
        return root

    def test_all_aliases_map_to_the_exact_skill_directory(self):
        root = self.make_repo()
        for alias, directory in COMPONENTS.items():
            with self.subTest(alias=alias):
                plan = plan_skill_rollback(root, alias, "v0.1.0")
                self.assertEqual(
                    plan.target_path,
                    f"plugins/qfin-list-page/skills/{directory}",
                )

    def test_dry_run_reports_every_difference_and_changes_nothing(self):
        root = self.make_repo()
        before = build_manifest(root)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = main(["--skill", "yushu", "--to", "v0.1.0"], repo_root=root)

        self.assertEqual(result, 0)
        text = output.getvalue()
        for required in (
            "add:old-only.txt",
            "remove:new-only.txt",
            "change:SKILL.md",
            "mode:mode.sh",
            "current version: 1.3.3",
            "historical version: 1.3.2",
            "preserved VERSION: 1.3.3",
            "release.py --component yushu --bump patch",
        ):
            self.assertIn(required, text)
        self.assertEqual(build_manifest(root), before)
        self.assertFalse((root / ".qfin-backups").exists())

    def test_apply_backs_up_target_restores_behavior_and_preserves_current_version(self):
        root = self.make_repo()
        plan = plan_skill_rollback(root, "yushu", "v0.1.0")
        target = root / plan.target_path
        current_manifest = build_manifest(target)
        non_targets = snapshot_component_trees(root, excluded={"yushu"})

        backup = apply_skill_rollback(
            root,
            plan,
            now=datetime(2026, 10, 14, 12, 0, 0),
        )

        self.assertEqual(
            backup,
            root / ".qfin-backups/20261014-120000/qifu-yushu-list-page",
        )
        self.assertEqual(build_manifest(backup), current_manifest)
        self.assertEqual((target / "SKILL.md").read_text(), "historical yushu\n")
        self.assertTrue((target / "old-only.txt").exists())
        self.assertFalse((target / "new-only.txt").exists())
        self.assertEqual((target / "mode.sh").stat().st_mode & 0o777, 0o644)
        self.assertEqual((target / "VERSION").read_text(), "1.3.3\n")
        self.assertEqual(snapshot_component_trees(root, excluded={"yushu"}), non_targets)

    def test_invalid_tags_components_and_repository_states_fail_before_mutation(self):
        root = self.make_repo()
        for skill, tag, message in (
            ("unknown", "v0.1.0", "unknown component"),
            ("yushu", "v1", "v<semver>"),
            ("yushu", "v0.1.0/../../main", "v<semver>"),
            ("yushu", "v9.9.9", "does not exist"),
        ):
            with self.subTest(skill=skill, tag=tag), self.assertRaisesRegex(ValueError, message):
                plan_skill_rollback(root, skill, tag)

        dirty = self.make_repo()
        (dirty / "unrelated.txt").write_text("dirty\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "working tree must be clean"):
            plan_skill_rollback(dirty, "yushu", "v0.1.0")

        missing_skill = self.make_repo(missing_historical_skill="yushu")
        with self.assertRaisesRegex(ValueError, "target Skill is missing"):
            plan_skill_rollback(missing_skill, "yushu", "v0.1.0")

        missing_version = self.make_repo(missing_historical_version="yushu")
        with self.assertRaisesRegex(ValueError, "historical VERSION is missing"):
            plan_skill_rollback(missing_version, "yushu", "v0.1.0")

    def test_invariant_failure_restores_target_from_backup(self):
        root = self.make_repo()
        plan = plan_skill_rollback(root, "yushu", "v0.1.0")
        target = root / plan.target_path
        before = build_manifest(target)
        broken = replace(
            plan,
            non_target_manifests={**plan.non_target_manifests, "router": {}},
        )

        with self.assertRaisesRegex(RuntimeError, "non-target component changed"):
            apply_skill_rollback(
                root,
                broken,
                now=datetime(2026, 10, 14, 12, 0, 1),
            )

        self.assertEqual(build_manifest(target), before)


if __name__ == "__main__":
    unittest.main()
