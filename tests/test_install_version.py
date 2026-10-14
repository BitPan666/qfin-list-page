import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.install_version import apply_install, main, plan_install, restore_current
from scripts.versioning_lib import COMPONENTS, CommandResult, run_command


PLUGIN_ID = "qfin-list-page@qfin-list-page"


class FakeRunner:
    def __init__(self, repo_root: Path, fail_once: tuple[str, ...] | None = None):
        self.repo_root = repo_root
        self.calls: list[tuple[str, ...]] = []
        self.fail_once = fail_once
        self.failed = False
        self.marketplace_path = repo_root
        self.plugin_version = "0.1.0"
        self.enabled = True

    def __call__(self, args: list[str], cwd: Path) -> CommandResult:
        call = tuple(str(arg) for arg in args)
        self.calls.append(call)
        if args[0] == "git":
            return run_command(args, cwd)

        should_fail = call == self.fail_once and not self.failed
        if should_fail:
            self.failed = True

        if call[:4] == ("codex", "plugin", "marketplace", "list"):
            payload = {
                "marketplaces": [
                    {
                        "name": "qfin-list-page",
                        "root": str(self.marketplace_path),
                        "marketplaceSource": {
                            "sourceType": "local",
                            "source": str(self.marketplace_path),
                        },
                    }
                ]
            }
            return CommandResult(0, json.dumps(payload), "")
        if call[:3] == ("codex", "plugin", "list"):
            installed = []
            if self.plugin_version is not None:
                installed.append(
                    {
                        "pluginId": PLUGIN_ID,
                        "name": "qfin-list-page",
                        "marketplaceName": "qfin-list-page",
                        "version": self.plugin_version,
                        "installed": True,
                        "enabled": self.enabled,
                    }
                )
            return CommandResult(0, json.dumps({"installed": installed, "available": []}), "")

        if call[:3] == ("codex", "plugin", "remove"):
            self.plugin_version = None
        elif call[:4] == ("codex", "plugin", "marketplace", "remove"):
            self.marketplace_path = None
        elif call[:4] == ("codex", "plugin", "marketplace", "add"):
            self.marketplace_path = Path(args[4])
        elif call[:3] == ("codex", "plugin", "add"):
            manifest_path = self.marketplace_path / "plugins/qfin-list-page/.codex-plugin/plugin.json"
            self.plugin_version = json.loads(manifest_path.read_text(encoding="utf-8"))["version"]
            self.enabled = True

        if should_fail:
            return CommandResult(1, "", "simulated failure")
        return CommandResult(0, "{}", "")


class InstallVersionTests(unittest.TestCase):
    def run_git(self, root: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=True
        )
        return completed.stdout.strip()

    def write_valid_tree(self, root: Path, plugin_version: str = "0.1.0") -> None:
        plugin_root = root / "plugins/qfin-list-page"
        (plugin_root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
        (plugin_root / ".codex-plugin/plugin.json").write_text(
            json.dumps(
                {"name": "qfin-list-page", "version": plugin_version, "skills": "./skills/"},
                indent=2,
            )
            + "\n",
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
            skill.mkdir(parents=True, exist_ok=True)
            (skill / "VERSION").write_text(f"{version}\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(f"# {directory}\n", encoding="utf-8")
        (root / ".agents/plugins").mkdir(parents=True, exist_ok=True)
        (root / ".agents/plugins/marketplace.json").write_text(
            json.dumps(
                {
                    "name": "qfin-list-page",
                    "plugins": [
                        {"name": "qfin-list-page", "source": "./plugins/qfin-list-page"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        (root / "versions.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "pluginVersion": plugin_version,
                    "components": versions,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def make_repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.write_valid_tree(root)
        self.run_git(root, "init", "-b", "main")
        self.run_git(root, "config", "user.name", "Test")
        self.run_git(root, "config", "user.email", "test@example.com")
        self.run_git(root, "add", ".")
        self.run_git(root, "commit", "-m", "baseline")
        self.run_git(root, "tag", "v0.1.0")

        versions_text = (root / "versions.json").read_text(encoding="utf-8")
        manifest_path = root / "plugins/qfin-list-page/.codex-plugin/plugin.json"
        manifest_text = manifest_path.read_text(encoding="utf-8")

        (root / "versions.json").unlink()
        self.run_git(root, "add", "-A")
        self.run_git(root, "commit", "-m", "missing versions")
        self.run_git(root, "tag", "v0.0.1")
        (root / "versions.json").write_text(versions_text, encoding="utf-8")

        manifest = json.loads(manifest_text)
        manifest["version"] = "9.9.9"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.run_git(root, "add", "-A")
        self.run_git(root, "commit", "-m", "mismatched manifest")
        self.run_git(root, "tag", "v0.0.2")
        manifest_path.write_text(manifest_text, encoding="utf-8")

        marketplace_path = root / ".agents/plugins/marketplace.json"
        marketplace_text = marketplace_path.read_text(encoding="utf-8")
        marketplace_path.unlink()
        self.run_git(root, "add", "-A")
        self.run_git(root, "commit", "-m", "missing plugin files")
        self.run_git(root, "tag", "v0.0.3")
        marketplace_path.write_text(marketplace_text, encoding="utf-8")
        self.run_git(root, "add", "-A")
        self.run_git(root, "commit", "-m", "restore current")
        return root

    def mutating_codex_calls(self, runner: FakeRunner) -> list[tuple[str, ...]]:
        return [
            call
            for call in runner.calls
            if call[:3] in {
                ("codex", "plugin", "remove"),
                ("codex", "plugin", "add"),
            }
            or call[:4]
            in {
                ("codex", "plugin", "marketplace", "remove"),
                ("codex", "plugin", "marketplace", "add"),
            }
        ]

    def test_valid_tag_plans_safe_worktree_and_all_component_versions(self):
        root = self.make_repo()
        runner = FakeRunner(root)

        plan = plan_install(root, "v0.1.0", runner)

        self.assertEqual(plan.worktree_path, root.resolve() / ".release-worktrees/v0.1.0")
        self.assertTrue(plan.worktree_path.is_relative_to(root.resolve() / ".release-worktrees"))
        self.assertEqual(str(plan.historical_state.plugin), "0.1.0")
        self.assertEqual(
            {alias: str(version) for alias, version in plan.historical_state.components.items()},
            {"router": "0.1.0", "yushu": "1.3.2", "jinyumeng": "0.7.2", "dianxiao": "0.1.0"},
        )
        self.assertEqual(plan.original_marketplace_path, root.resolve())
        self.assertEqual(str(plan.original_plugin_version), "0.1.0")

    def test_cli_dry_run_creates_no_worktree_or_codex_mutation(self):
        root = self.make_repo()
        runner = FakeRunner(root)
        before = self.run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = main(["--tag", "v0.1.0"], repo_root=root, runner=runner)

        self.assertEqual(result, 0)
        self.assertIn("DRY-RUN", output.getvalue())
        self.assertIn("open a new Codex task", output.getvalue())
        self.assertFalse((root / ".release-worktrees").exists())
        self.assertEqual(self.mutating_codex_calls(runner), [])
        self.assertEqual(
            self.run_git(root, "status", "--porcelain=v1", "--untracked-files=all"),
            before,
        )

    def test_invalid_historical_sources_fail_before_codex_mutation(self):
        root = self.make_repo()
        for tag, message in (
            ("v1", "v<semver>"),
            ("v0.1.0/../../main", "v<semver>"),
            ("v9.9.9", "does not exist"),
            ("v0.0.1", "versions.json"),
            ("v0.0.2", "manifest"),
            ("v0.0.3", "Plugin files"),
        ):
            runner = FakeRunner(root)
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, message):
                plan_install(root, tag, runner)
            self.assertFalse(any(call and call[0] == "codex" for call in runner.calls))

    def test_apply_uses_expected_codex_order_and_leaves_unrelated_worktrees(self):
        root = self.make_repo()
        unrelated = root / "unrelated-worktree-marker"
        unrelated.write_text("keep\n", encoding="utf-8")
        runner = FakeRunner(root)
        plan = plan_install(root, "v0.1.0", runner)
        runner.calls.clear()

        apply_install(root, plan, runner)

        self.assertTrue(unrelated.exists())
        self.assertTrue(plan.worktree_path.is_dir())
        self.assertEqual(
            [call[:4] for call in self.mutating_codex_calls(runner)],
            [
                ("codex", "plugin", "remove", PLUGIN_ID),
                ("codex", "plugin", "marketplace", "remove"),
                ("codex", "plugin", "marketplace", "add"),
                ("codex", "plugin", "add", PLUGIN_ID),
            ],
        )
        self.assertEqual(runner.marketplace_path, plan.worktree_path)
        self.assertEqual(runner.plugin_version, "0.1.0")
        self.assertTrue(any(call[:3] == ("codex", "plugin", "list") for call in runner.calls))
        self.assertFalse(any(call[:3] == ("git", "worktree", "remove") for call in runner.calls))

    def test_every_codex_mutation_failure_restores_original_marketplace_and_plugin(self):
        root = self.make_repo()
        failure_calls = [
            ("codex", "plugin", "remove", PLUGIN_ID, "--json"),
            ("codex", "plugin", "marketplace", "remove", "qfin-list-page", "--json"),
            (
                "codex",
                "plugin",
                "marketplace",
                "add",
                str(root.resolve() / ".release-worktrees/v0.1.0"),
                "--json",
            ),
            ("codex", "plugin", "add", PLUGIN_ID, "--json"),
        ]
        for failure_call in failure_calls:
            with self.subTest(failure_call=failure_call):
                runner = FakeRunner(root, fail_once=failure_call)
                plan = plan_install(root, "v0.1.0", runner)
                if plan.worktree_path.exists():
                    self.run_git(root, "worktree", "remove", str(plan.worktree_path), "--force")
                with self.assertRaisesRegex(RuntimeError, "installation failed"):
                    apply_install(root, plan, runner)
                self.assertEqual(runner.marketplace_path, root.resolve())
                self.assertEqual(runner.plugin_version, "0.1.0")
                self.assertTrue(runner.enabled)

    def test_restore_current_reinstalls_from_main_repository_and_verifies_enabled(self):
        root = self.make_repo()
        historical = root / ".release-worktrees/v0.0.9"
        historical.mkdir(parents=True)
        runner = FakeRunner(root)
        runner.marketplace_path = historical
        runner.plugin_version = "0.0.9"
        runner.calls.clear()

        restore_current(root, runner)

        self.assertEqual(runner.marketplace_path, root.resolve())
        self.assertEqual(runner.plugin_version, "0.1.0")
        self.assertTrue(runner.enabled)
        self.assertEqual(
            [call[:4] for call in self.mutating_codex_calls(runner)],
            [
                ("codex", "plugin", "remove", PLUGIN_ID),
                ("codex", "plugin", "marketplace", "remove"),
                ("codex", "plugin", "marketplace", "add"),
                ("codex", "plugin", "add", PLUGIN_ID),
            ],
        )


if __name__ == "__main__":
    unittest.main()
