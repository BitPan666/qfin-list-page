#!/usr/bin/env python3
"""Plan and apply qfin-list-page release metadata updates."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.versioning_lib import (  # noqa: E402
    COMPONENTS,
    PLUGIN_MANIFEST,
    SKILLS_ROOT,
    SemVer,
    VersionState,
    load_version_state,
    run_command,
    validate_version_state,
)


_BUMP_RANK = {"patch": 0, "minor": 1, "major": 2}


@dataclass(frozen=True)
class ReleasePlan:
    current: VersionState
    target: VersionState
    components: tuple[str, ...]
    bump: str
    plugin_bump: str
    note: str
    tag: str
    changed_paths: tuple[str, ...]


def _git(repo_root: Path, *args: str):
    result = run_command(["git", *args], Path(repo_root))
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return result


def _status_paths(repo_root: Path) -> list[str]:
    result = _git(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return sorted(paths)


def _component_for_path(path: str) -> str | None:
    for alias, directory in COMPONENTS.items():
        prefix = f"{SKILLS_ROOT.as_posix()}/{directory}/"
        if path.startswith(prefix):
            return alias
    return None


def detect_changed_components(repo_root: Path) -> tuple[set[str], list[str]]:
    changed: set[str] = set()
    unrelated: list[str] = []
    for path in _status_paths(Path(repo_root)):
        component = _component_for_path(path)
        if component is None:
            unrelated.append(path)
        else:
            changed.add(component)
    return changed, unrelated


def _released_plugin_versions(repo_root: Path) -> list[SemVer]:
    result = _git(repo_root, "tag", "--list", "v*")
    versions: list[SemVer] = []
    for tag in result.stdout.splitlines():
        try:
            versions.append(SemVer.parse(tag.removeprefix("v")))
        except ValueError:
            continue
    return versions


def plan_release(
    repo_root: Path,
    components: tuple[str, ...],
    bump: str,
    note: str,
    plugin_bump: str | None = None,
) -> ReleasePlan:
    root = Path(repo_root)
    if bump not in _BUMP_RANK:
        raise ValueError(f"invalid version bump: {bump!r}")
    selected_plugin_bump = plugin_bump or bump
    if selected_plugin_bump not in _BUMP_RANK:
        raise ValueError(f"invalid plugin version bump: {selected_plugin_bump!r}")
    if _BUMP_RANK[selected_plugin_bump] < _BUMP_RANK[bump]:
        raise ValueError("plugin bump cannot be lower than component bump")
    if not components:
        raise ValueError("at least one component is required")
    if len(set(components)) != len(components):
        raise ValueError("component aliases must not be repeated")
    unknown = set(components) - set(COMPONENTS)
    if unknown:
        raise ValueError(f"unknown component aliases: {', '.join(sorted(unknown))}")
    if not note.strip():
        raise ValueError("release note must not be empty")

    validation_errors = validate_version_state(root)
    if validation_errors:
        raise ValueError("invalid current version state: " + "; ".join(validation_errors))
    current = load_version_state(root)

    changed, unrelated = detect_changed_components(root)
    if unrelated:
        raise ValueError(f"unrelated changes block release: {', '.join(unrelated)}")
    if not changed:
        raise ValueError("no component changes detected")
    if changed != set(components):
        raise ValueError(
            "changed components do not match declared components: "
            f"changed={','.join(sorted(changed))} declared={','.join(sorted(components))}"
        )

    target_components = dict(current.components)
    for alias in components:
        target_components[alias] = current.components[alias].bump(bump)
    target_plugin = current.plugin.bump(selected_plugin_bump)
    tag = f"v{target_plugin}"
    tag_result = run_command(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}"],
        root,
    )
    if tag_result.returncode == 0:
        raise ValueError(f"target tag already exists: {tag}")
    if tag_result.returncode not in (0, 1):
        raise ValueError(f"could not check target tag {tag}: {tag_result.stderr.strip()}")
    released = _released_plugin_versions(root)
    if released and target_plugin <= max(released):
        raise ValueError(
            f"target Plugin version {target_plugin} is not newer than released {max(released)}"
        )

    return ReleasePlan(
        current=current,
        target=VersionState(plugin=target_plugin, components=target_components),
        components=components,
        bump=bump,
        plugin_bump=selected_plugin_bump,
        note=note.strip(),
        tag=tag,
        changed_paths=tuple(_status_paths(root)),
    )


def _render_changelog_section(plan: ReleasePlan) -> str:
    changed = [
        f"`{COMPONENTS[alias]}` `{plan.current.components[alias]}` → "
        f"`{plan.target.components[alias]}`"
        for alias in plan.components
    ]
    unchanged = [
        f"`{COMPONENTS[alias]}` `{plan.current.components[alias]}`"
        for alias in COMPONENTS
        if alias not in plan.components
    ]
    lines = [
        f"## {plan.target.plugin} - {date.today().isoformat()}",
        "",
        f"- Reason: {plan.note}",
        f"- Updated components: {', '.join(changed)}.",
    ]
    if unchanged:
        lines.append(f"- Unchanged components: {', '.join(unchanged)}.")
    lines.append(f"- Tag: `{plan.tag}`.")
    return "\n".join(lines) + "\n"


def apply_release(repo_root: Path, plan: ReleasePlan) -> None:
    root = Path(repo_root)
    paths = [
        root / SKILLS_ROOT / COMPONENTS[alias] / "VERSION"
        for alias in plan.components
    ]
    paths.extend(
        [
            root / PLUGIN_MANIFEST,
            root / "versions.json",
            root / "CHANGELOG.md",
        ]
    )
    originals = {path: path.read_bytes() for path in paths}
    try:
        for alias in plan.components:
            version_path = root / SKILLS_ROOT / COMPONENTS[alias] / "VERSION"
            version_path.write_text(f"{plan.target.components[alias]}\n", encoding="utf-8")

        manifest_path = root / PLUGIN_MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = str(plan.target.plugin)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        lock = {
            "schemaVersion": 1,
            "pluginVersion": str(plan.target.plugin),
            "components": {
                directory: str(plan.target.components[alias])
                for alias, directory in COMPONENTS.items()
            },
        }
        (root / "versions.json").write_text(
            json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        changelog_path = root / "CHANGELOG.md"
        existing = changelog_path.read_text(encoding="utf-8")
        header = "# Changelog\n"
        if not existing.startswith(header):
            raise ValueError("CHANGELOG.md must start with '# Changelog'")
        prior_entries = existing[len(header) :].lstrip("\n")
        changelog_path.write_text(
            header + "\n" + _render_changelog_section(plan) + "\n" + prior_entries,
            encoding="utf-8",
        )

        errors = validate_version_state(root)
        if errors:
            raise ValueError("release produced invalid version state: " + "; ".join(errors))
    except Exception:
        for path, contents in originals.items():
            path.write_bytes(contents)
        raise


def _validation_commands(repo_root: Path, components: tuple[str, ...]) -> list[list[str]]:
    root = Path(repo_root)
    python = sys.executable
    commands = [
        [python, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        [
            python,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(SKILLS_ROOT / COMPONENTS["router"] / "tests"),
            "-p",
            "test_*.py",
            "-v",
        ],
        [python, str(SKILLS_ROOT / COMPONENTS["router"] / "scripts" / "validate_router.py")],
    ]
    for alias in components:
        directory = COMPONENTS[alias]
        if alias == "router":
            continue
        skill_path = SKILLS_ROOT / directory
        commands.extend(
            [
                [
                    python,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    str(skill_path / "tests"),
                    "-p",
                    "test_*.py",
                    "-v",
                ],
                [
                    python,
                    str(skill_path / "scripts" / "validate_skill_contract.py"),
                    str(skill_path),
                ],
            ]
        )
    plugin_validator = (
        Path.home()
        / ".codex/skills/.system/plugin-creator/scripts/validate_plugin.py"
    )
    commands.append(
        [
            "uv",
            "run",
            "--with",
            "pyyaml",
            "python",
            str(plugin_validator),
            str(root / "plugins/qfin-list-page"),
        ]
    )
    return commands


def _print_plan(plan: ReleasePlan, repo_root: Path) -> None:
    print(f"Plugin: {plan.current.plugin} -> {plan.target.plugin}")
    for alias in COMPONENTS:
        print(
            f"{alias}: {plan.current.components[alias]} -> {plan.target.components[alias]}"
        )
    print("Changed paths:")
    for path in plan.changed_paths:
        print(f"  - {path}")
    print("Changelog preview:")
    print(_render_changelog_section(plan).rstrip())
    print("Validation commands:")
    for command in _validation_commands(Path(repo_root), plan.components):
        print("  " + " ".join(command))
    print(f"Proposed tag: {plan.tag}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", action="append", required=True, choices=tuple(COMPONENTS))
    parser.add_argument("--bump", required=True, choices=tuple(_BUMP_RANK))
    parser.add_argument("--note", required=True)
    parser.add_argument("--plugin-bump", choices=tuple(_BUMP_RANK))
    parser.add_argument("--apply", action="store_true")
    return parser


def main(argv: list[str] | None = None, repo_root: Path | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    try:
        plan = plan_release(
            root,
            tuple(args.component),
            args.bump,
            args.note,
            plugin_bump=args.plugin_bump,
        )
        _print_plan(plan, root)
        if not args.apply:
            print("DRY-RUN: no files, commits, tags, or Plugin state were changed.")
            return 0
        apply_release(root, plan)
        for command in _validation_commands(root, plan.components):
            result = run_command(command, root)
            if result.returncode != 0:
                print(result.stdout, end="")
                print(result.stderr, end="", file=sys.stderr)
                raise RuntimeError(f"validation command failed: {' '.join(command)}")
        print("Applied release metadata. Review, commit, and create the annotated tag manually.")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
