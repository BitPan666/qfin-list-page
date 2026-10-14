#!/usr/bin/env python3
"""Restore one qfin-list-page Skill's behavior from a formal release tag."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.compare_skill_trees import FileRecord, build_manifest  # noqa: E402
from scripts.versioning_lib import (  # noqa: E402
    COMPONENTS,
    SKILLS_ROOT,
    SemVer,
    run_command,
    snapshot_component_trees,
)


@dataclass(frozen=True)
class RollbackPlan:
    skill: str
    tag: str
    target_path: str
    current_version: SemVer
    historical_version: SemVer
    differences: tuple[str, ...]
    non_target_manifests: dict[str, dict[str, FileRecord]]


def _require_clean_tree(repo_root: Path) -> None:
    result = run_command(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        repo_root,
    )
    if result.returncode != 0:
        raise ValueError(f"could not inspect working tree: {result.stderr.strip()}")
    if result.stdout.strip():
        raise ValueError("working tree must be clean before a Skill rollback")


def _validate_tag(repo_root: Path, tag: str) -> None:
    try:
        SemVer.parse(tag.removeprefix("v"))
    except ValueError as error:
        raise ValueError("rollback tag must use the v<semver> form") from error
    if not tag.startswith("v") or tag != f"v{SemVer.parse(tag[1:])}":
        raise ValueError("rollback tag must use the v<semver> form")
    ref_check = run_command(["git", "check-ref-format", "--allow-onelevel", tag], repo_root)
    if ref_check.returncode != 0:
        raise ValueError("rollback tag must be a valid one-level Git reference")
    exists = run_command(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}"],
        repo_root,
    )
    if exists.returncode != 0:
        raise ValueError(f"release tag does not exist: {tag}")


def _git_show_bytes(repo_root: Path, object_name: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", object_name],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"cannot read historical object {object_name}: {detail}")
    return completed.stdout


def _historical_manifest(repo_root: Path, tag: str, target_path: str) -> dict[str, FileRecord]:
    tree = run_command(
        ["git", "ls-tree", "-r", tag, "--", target_path],
        repo_root,
    )
    if tree.returncode != 0:
        raise ValueError(f"cannot inspect target Skill at {tag}: {tree.stderr.strip()}")
    manifest: dict[str, FileRecord] = {}
    prefix = target_path.rstrip("/") + "/"
    for line in tree.stdout.splitlines():
        metadata, full_path = line.split("\t", 1)
        mode_text, object_type, _object_id = metadata.split(" ", 2)
        if object_type != "blob" or not full_path.startswith(prefix):
            continue
        relative_path = full_path[len(prefix) :]
        contents = _git_show_bytes(repo_root, f"{tag}:{full_path}")
        if mode_text == "100755":
            mode = 0o755
        elif mode_text == "120000":
            mode = 0o777
        else:
            mode = 0o644
        manifest[relative_path] = FileRecord(
            sha256=hashlib.sha256(contents).hexdigest(),
            mode=mode,
        )
    return manifest


def _manifest_differences(
    current: dict[str, FileRecord], historical: dict[str, FileRecord]
) -> tuple[str, ...]:
    current = {path: record for path, record in current.items() if path != "VERSION"}
    historical = {path: record for path, record in historical.items() if path != "VERSION"}
    differences: list[str] = []
    for path in sorted(historical.keys() - current.keys()):
        differences.append(f"add:{path}")
    for path in sorted(current.keys() - historical.keys()):
        differences.append(f"remove:{path}")
    for path in sorted(current.keys() & historical.keys()):
        if current[path].sha256 != historical[path].sha256:
            differences.append(f"change:{path}")
        if current[path].mode != historical[path].mode:
            differences.append(f"mode:{path}")
    return tuple(differences)


def plan_skill_rollback(repo_root: Path, skill: str, tag: str) -> RollbackPlan:
    root = Path(repo_root)
    if skill not in COMPONENTS:
        raise ValueError(f"unknown component: {skill}")
    _validate_tag(root, tag)
    _require_clean_tree(root)

    directory = COMPONENTS[skill]
    target_path = (SKILLS_ROOT / directory).as_posix()
    current_target = root / target_path
    if not current_target.is_dir() or current_target.is_symlink():
        raise ValueError(f"current target Skill is missing or unsafe: {target_path}")
    try:
        current_version = SemVer.parse(
            (current_target / "VERSION").read_text(encoding="utf-8").strip()
        )
    except (OSError, ValueError) as error:
        raise ValueError(f"current VERSION is missing or invalid for {skill}") from error

    versions_check = run_command(["git", "cat-file", "-e", f"{tag}:versions.json"], root)
    if versions_check.returncode != 0:
        raise ValueError(f"versions.json is missing from release tag {tag}")
    try:
        historical_lock = json.loads(
            _git_show_bytes(root, f"{tag}:versions.json").decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"versions.json is malformed in release tag {tag}") from error

    target_check = run_command(["git", "cat-file", "-e", f"{tag}:{target_path}"], root)
    if target_check.returncode != 0:
        raise ValueError(f"target Skill is missing from release tag {tag}: {directory}")
    version_check = run_command(
        ["git", "cat-file", "-e", f"{tag}:{target_path}/VERSION"],
        root,
    )
    if version_check.returncode != 0:
        raise ValueError(f"historical VERSION is missing for {skill} at {tag}")
    try:
        historical_version = SemVer.parse(
            _git_show_bytes(root, f"{tag}:{target_path}/VERSION")
            .decode("utf-8")
            .strip()
        )
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError(f"historical VERSION is invalid for {skill} at {tag}") from error
    locked_version = historical_lock.get("components", {}).get(directory)
    if locked_version != str(historical_version):
        raise ValueError(
            f"historical versions.json mismatch for {skill}: "
            f"lock={locked_version!r} VERSION={historical_version}"
        )

    current_manifest = build_manifest(current_target)
    historical_manifest = _historical_manifest(root, tag, target_path)
    return RollbackPlan(
        skill=skill,
        tag=tag,
        target_path=target_path,
        current_version=current_version,
        historical_version=historical_version,
        differences=_manifest_differences(current_manifest, historical_manifest),
        non_target_manifests=snapshot_component_trees(root, excluded={skill}),
    )


def _restore_backup(target: Path, backup: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(backup, target, copy_function=shutil.copy2, symlinks=True)


def apply_skill_rollback(
    repo_root: Path,
    plan: RollbackPlan,
    now: datetime | None = None,
) -> Path:
    root = Path(repo_root)
    _require_clean_tree(root)
    target = root / plan.target_path
    if not target.is_dir() or target.is_symlink():
        raise ValueError(f"current target Skill is missing or unsafe: {plan.target_path}")

    timestamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    backup = root / ".qfin-backups" / timestamp / target.name
    if backup.exists():
        raise ValueError(f"backup path already exists: {backup}")
    backup.parent.mkdir(parents=True, exist_ok=False)
    shutil.copytree(target, backup, copy_function=shutil.copy2, symlinks=True)

    try:
        restored = run_command(
            ["git", "restore", "--source", plan.tag, "--worktree", "--", plan.target_path],
            root,
        )
        if restored.returncode != 0:
            raise RuntimeError(f"Git restore failed: {restored.stderr.strip()}")
        (target / "VERSION").write_text(f"{plan.current_version}\n", encoding="utf-8")

        current_non_targets = snapshot_component_trees(root, excluded={plan.skill})
        if current_non_targets != plan.non_target_manifests:
            raise RuntimeError("non-target component changed during Skill rollback")
    except Exception:
        _restore_backup(target, backup)
        raise
    return backup


def _print_plan(plan: RollbackPlan) -> None:
    print(f"Skill: {plan.skill}")
    print(f"Target path: {plan.target_path}")
    print(f"Tag: {plan.tag}")
    print(f"current version: {plan.current_version}")
    print(f"historical version: {plan.historical_version}")
    print(f"preserved VERSION: {plan.current_version}")
    print("Behavior differences:")
    if plan.differences:
        for difference in plan.differences:
            print(f"  - {difference}")
    else:
        print("  - none")
    print("Next release command:")
    print(
        f"  python3 scripts/release.py --component {plan.skill} --bump patch "
        f'--note "Restore {plan.tag} behavior"'
    )


def _validation_commands(plan: RollbackPlan) -> list[list[str]]:
    python = sys.executable
    target = Path(plan.target_path)
    commands = [
        [
            python,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(target / "tests"),
            "-p",
            "test_*.py",
            "-v",
        ]
    ]
    if plan.skill == "router":
        commands.append([python, str(target / "scripts" / "validate_router.py")])
    else:
        commands.append(
            [
                python,
                str(target / "scripts" / "validate_skill_contract.py"),
                str(target),
            ]
        )
    return commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True, choices=tuple(COMPONENTS))
    parser.add_argument("--to", required=True)
    parser.add_argument("--apply", action="store_true")
    return parser


def main(argv: list[str] | None = None, repo_root: Path | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    try:
        plan = plan_skill_rollback(root, args.skill, args.to)
        _print_plan(plan)
        if not args.apply:
            print("DRY-RUN: no backup or working-tree file was created or changed.")
            return 0
        backup = apply_skill_rollback(root, plan)
        for command in _validation_commands(plan):
            result = run_command(command, root)
            if result.returncode != 0:
                print(result.stdout, end="")
                print(result.stderr, end="", file=sys.stderr)
                raise RuntimeError(f"validation command failed: {' '.join(command)}")
        print(f"Backup: {backup}")
        print(
            f"Next: python3 scripts/release.py --component {plan.skill} --bump patch "
            f'--note "Restore {plan.tag} behavior"'
        )
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
