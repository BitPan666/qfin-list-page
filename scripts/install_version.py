#!/usr/bin/env python3
"""Temporarily install a tagged qfin-list-page Plugin with recovery."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.versioning_lib import (  # noqa: E402
    COMPONENTS,
    component_map,
    CommandResult,
    SemVer,
    VersionState,
    load_version_state,
    run_command,
    validate_version_state,
)


PLUGIN_ID = "qfin-list-page@qfin-list-page"
MARKETPLACE_NAME = "qfin-list-page"
Runner = Callable[[list[str], Path], CommandResult]


@dataclass(frozen=True)
class InstallPlan:
    tag: str
    worktree_path: Path
    historical_state: VersionState
    original_marketplace_path: Path
    original_plugin_version: SemVer


def _required(
    runner: Runner,
    args: list[str],
    cwd: Path,
    label: str,
) -> CommandResult:
    result = runner(args, cwd)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"{label} failed: {detail}")
    return result


def _validate_tag(repo_root: Path, tag: str, runner: Runner) -> None:
    if not tag.startswith("v"):
        raise ValueError("install tag must use the v<semver> form")
    try:
        version = SemVer.parse(tag[1:])
    except ValueError as error:
        raise ValueError("install tag must use the v<semver> form") from error
    if tag != f"v{version}":
        raise ValueError("install tag must use the v<semver> form")
    check = runner(["git", "check-ref-format", "--allow-onelevel", tag], repo_root)
    if check.returncode != 0:
        raise ValueError("install tag must be a valid one-level Git reference")
    exists = runner(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}"],
        repo_root,
    )
    if exists.returncode != 0:
        raise ValueError(f"release tag does not exist: {tag}")


def _tag_file(repo_root: Path, tag: str, path: str, runner: Runner) -> str:
    exists = runner(["git", "cat-file", "-e", f"{tag}:{path}"], repo_root)
    if exists.returncode != 0:
        raise ValueError(f"required historical file is missing: {path}")
    result = _required(runner, ["git", "show", f"{tag}:{path}"], repo_root, path)
    return result.stdout


def _historical_state(repo_root: Path, tag: str, runner: Runner) -> VersionState:
    try:
        lock = json.loads(_tag_file(repo_root, tag, "versions.json", runner))
    except json.JSONDecodeError as error:
        raise ValueError(f"historical versions.json is malformed at {tag}") from error
    if not isinstance(lock, dict) or lock.get("schemaVersion") != 1:
        raise ValueError(f"historical versions.json is malformed at {tag}")
    raw_components = lock.get("components")
    try:
        mapping = component_map(raw_components)
    except ValueError as error:
        raise ValueError(f"historical versions.json component set is invalid at {tag}") from error
    try:
        state = VersionState(
            plugin=SemVer.parse(lock["pluginVersion"]),
            components={
                alias: SemVer.parse(raw_components[directory])
                for alias, directory in mapping.items()
            },
        )
    except (KeyError, ValueError, TypeError) as error:
        raise ValueError(f"historical versions.json contains invalid versions at {tag}") from error

    marketplace = runner(
        ["git", "cat-file", "-e", f"{tag}:.agents/plugins/marketplace.json"],
        repo_root,
    )
    manifest_check = runner(
        [
            "git",
            "cat-file",
            "-e",
            f"{tag}:plugins/qfin-list-page/.codex-plugin/plugin.json",
        ],
        repo_root,
    )
    if marketplace.returncode != 0 or manifest_check.returncode != 0:
        raise ValueError(f"required historical Plugin files are missing at {tag}")

    try:
        manifest = json.loads(
            _tag_file(
                repo_root,
                tag,
                "plugins/qfin-list-page/.codex-plugin/plugin.json",
                runner,
            )
        )
    except json.JSONDecodeError as error:
        raise ValueError(f"historical Plugin manifest is malformed at {tag}") from error
    if manifest.get("name") != "qfin-list-page" or manifest.get("version") != str(state.plugin):
        raise ValueError(f"historical Plugin manifest does not match versions.json at {tag}")

    for alias, directory in mapping.items():
        version_path = f"plugins/qfin-list-page/skills/{directory}/VERSION"
        try:
            disk_version = SemVer.parse(_tag_file(repo_root, tag, version_path, runner).strip())
        except ValueError as error:
            raise ValueError(f"historical Skill VERSION is invalid for {alias} at {tag}") from error
        if disk_version != state.components[alias]:
            raise ValueError(f"historical Skill VERSION mismatch for {alias} at {tag}")
    return state


def _read_current_install(repo_root: Path, runner: Runner) -> tuple[Path, SemVer]:
    marketplace_result = _required(
        runner,
        ["codex", "plugin", "marketplace", "list", "--json"],
        repo_root,
        "marketplace listing",
    )
    plugin_result = _required(
        runner,
        ["codex", "plugin", "list", "--json"],
        repo_root,
        "Plugin listing",
    )
    try:
        marketplaces = json.loads(marketplace_result.stdout)["marketplaces"]
        entry = next(item for item in marketplaces if item.get("name") == MARKETPLACE_NAME)
        marketplace_path = Path(
            entry.get("marketplaceSource", {}).get("source") or entry["root"]
        ).resolve()
        installed = json.loads(plugin_result.stdout)["installed"]
        plugin = next(item for item in installed if item.get("pluginId") == PLUGIN_ID)
        if not plugin.get("installed") or not plugin.get("enabled"):
            raise ValueError("current qfin-list-page Plugin is not installed and enabled")
        plugin_version = SemVer.parse(plugin["version"])
    except (KeyError, StopIteration, TypeError, json.JSONDecodeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith("current qfin"):
            raise
        raise ValueError("could not determine current qfin-list-page installation") from error
    return marketplace_path, plugin_version


def plan_install(repo_root: Path, tag: str, runner: Runner) -> InstallPlan:
    root = Path(repo_root).resolve()
    _validate_tag(root, tag, runner)
    historical_state = _historical_state(root, tag, runner)
    release_root = (root / ".release-worktrees").resolve()
    worktree_path = (release_root / tag).resolve()
    if not worktree_path.is_relative_to(release_root):
        raise ValueError("derived worktree path escapes .release-worktrees")
    original_marketplace_path, original_plugin_version = _read_current_install(root, runner)
    return InstallPlan(
        tag=tag,
        worktree_path=worktree_path,
        historical_state=historical_state,
        original_marketplace_path=original_marketplace_path,
        original_plugin_version=original_plugin_version,
    )


def _codex_required(runner: Runner, args: list[str], cwd: Path) -> None:
    result = runner(args, cwd)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({' '.join(args)}): {detail}")


def _verify_installed(repo_root: Path, expected: SemVer, runner: Runner) -> None:
    result = runner(["codex", "plugin", "list", "--json"], repo_root)
    if result.returncode != 0:
        raise RuntimeError(f"installed-state verification failed: {result.stderr.strip()}")
    try:
        installed = json.loads(result.stdout)["installed"]
        plugin = next(item for item in installed if item.get("pluginId") == PLUGIN_ID)
        actual = SemVer.parse(plugin["version"])
        enabled = plugin.get("installed") is True and plugin.get("enabled") is True
    except (KeyError, StopIteration, TypeError, json.JSONDecodeError, ValueError) as error:
        raise RuntimeError("installed-state verification returned malformed data") from error
    if actual != expected or not enabled:
        raise RuntimeError(
            f"installed-state verification failed: version={actual}, enabled={enabled}"
        )


def restore_current(repo_root: Path, runner: Runner) -> None:
    root = Path(repo_root).resolve()
    current = load_version_state(root)
    # Removals are idempotent recovery steps: absence is acceptable.
    runner(["codex", "plugin", "remove", PLUGIN_ID, "--json"], root)
    runner(
        ["codex", "plugin", "marketplace", "remove", MARKETPLACE_NAME, "--json"],
        root,
    )
    _codex_required(
        runner,
        ["codex", "plugin", "marketplace", "add", str(root), "--json"],
        root,
    )
    _codex_required(
        runner,
        ["codex", "plugin", "add", PLUGIN_ID, "--json"],
        root,
    )
    _verify_installed(root, current.plugin, runner)


def _validate_worktree(plan: InstallPlan) -> None:
    errors = validate_version_state(plan.worktree_path)
    if errors:
        raise RuntimeError("historical worktree validation failed: " + "; ".join(errors))
    state = load_version_state(plan.worktree_path)
    if state != plan.historical_state:
        raise RuntimeError("historical worktree version state changed after planning")
    required = [
        plan.worktree_path / ".agents/plugins/marketplace.json",
        plan.worktree_path / "plugins/qfin-list-page/.codex-plugin/plugin.json",
    ]
    if not all(path.is_file() for path in required):
        raise RuntimeError("historical worktree is missing required Plugin files")


def apply_install(repo_root: Path, plan: InstallPlan, runner: Runner) -> None:
    root = Path(repo_root).resolve()
    if plan.worktree_path.exists():
        raise RuntimeError(f"historical worktree already exists: {plan.worktree_path}")
    plan.worktree_path.parent.mkdir(parents=True, exist_ok=True)
    worktree = runner(
        [
            "git",
            "worktree",
            "add",
            "--detach",
            str(plan.worktree_path),
            plan.tag,
        ],
        root,
    )
    if worktree.returncode != 0:
        raise RuntimeError(f"could not create historical worktree: {worktree.stderr.strip()}")
    _validate_worktree(plan)

    try:
        _codex_required(
            runner,
            ["codex", "plugin", "remove", PLUGIN_ID, "--json"],
            root,
        )
        _codex_required(
            runner,
            ["codex", "plugin", "marketplace", "remove", MARKETPLACE_NAME, "--json"],
            root,
        )
        _codex_required(
            runner,
            [
                "codex",
                "plugin",
                "marketplace",
                "add",
                str(plan.worktree_path),
                "--json",
            ],
            root,
        )
        _codex_required(
            runner,
            ["codex", "plugin", "add", PLUGIN_ID, "--json"],
            root,
        )
        _verify_installed(root, plan.historical_state.plugin, runner)
    except Exception as install_error:
        try:
            restore_current(plan.original_marketplace_path, runner)
            _verify_installed(
                plan.original_marketplace_path,
                plan.original_plugin_version,
                runner,
            )
        except Exception as recovery_error:
            raise RuntimeError(
                f"installation failed ({install_error}); automatic recovery also failed ({recovery_error})"
            ) from install_error
        raise RuntimeError(
            f"installation failed ({install_error}); original Plugin was restored"
        ) from install_error


def _print_plan(plan: InstallPlan) -> None:
    print(f"Tag: {plan.tag}")
    print(f"Historical worktree: {plan.worktree_path}")
    print(f"Plugin: {plan.historical_state.plugin}")
    for alias in plan.historical_state.components:
        print(f"{alias}: {plan.historical_state.components[alias]}")
    print(
        f"Current install: {plan.original_plugin_version} from {plan.original_marketplace_path}"
    )
    print("Command plan:")
    print(f"  git worktree add --detach {plan.worktree_path} {plan.tag}")
    print(f"  codex plugin remove {PLUGIN_ID}")
    print(f"  codex plugin marketplace remove {MARKETPLACE_NAME}")
    print(f"  codex plugin marketplace add {plan.worktree_path}")
    print(f"  codex plugin add {PLUGIN_ID}")
    print("Recovery plan:")
    print("  python3 scripts/install_version.py --restore-current --apply")
    print("After installation, open a new Codex task to load the selected Plugin version.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--tag")
    selection.add_argument("--restore-current", action="store_true")
    parser.add_argument("--apply", action="store_true")
    return parser


def main(
    argv: list[str] | None = None,
    repo_root: Path | None = None,
    runner: Runner = run_command,
) -> int:
    args = build_parser().parse_args(argv)
    root = Path(repo_root).resolve() if repo_root is not None else Path.cwd().resolve()
    try:
        if args.restore_current:
            print(f"Restore marketplace and Plugin from: {root}")
            print(f"  codex plugin remove {PLUGIN_ID}")
            print(f"  codex plugin marketplace remove {MARKETPLACE_NAME}")
            print(f"  codex plugin marketplace add {root}")
            print(f"  codex plugin add {PLUGIN_ID}")
            if not args.apply:
                print("DRY-RUN: installed Plugin state was not changed.")
                return 0
            restore_current(root, runner)
            print("Current Plugin restored. Open a new Codex task.")
            print("Historical worktrees were retained. Remove a specific one with:")
            print("  git worktree remove .release-worktrees/<tag>")
            return 0

        plan = plan_install(root, args.tag, runner)
        _print_plan(plan)
        if not args.apply:
            print("DRY-RUN: no worktree, marketplace, Plugin, or file state was changed.")
            return 0
        apply_install(root, plan, runner)
        print(f"Installed {plan.tag}. Open a new Codex task.")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
