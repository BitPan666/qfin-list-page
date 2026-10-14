#!/usr/bin/env python3
"""Shared version and repository validation helpers for qfin-list-page."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.compare_skill_trees import FileRecord, build_manifest


PLUGIN_ROOT = Path("plugins/qfin-list-page")
PLUGIN_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
COMPONENTS = {
    "router": "qfin-list-page",
    "yushu": "qifu-yushu-list-page",
    "jinyumeng": "qifu-jinyumeng-list-page",
    "dianxiao": "qifu-dianxiao-list-page",
}
_SEMVER_PATTERN = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")


@dataclass(frozen=True, order=True)
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "SemVer":
        if not isinstance(value, str):
            raise ValueError(f"invalid semantic version: {value!r}")
        match = _SEMVER_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError(f"invalid semantic version: {value!r}")
        return cls(*(int(part) for part in match.groups()))

    def bump(self, level: str) -> "SemVer":
        if level == "patch":
            return SemVer(self.major, self.minor, self.patch + 1)
        if level == "minor":
            return SemVer(self.major, self.minor + 1, 0)
        if level == "major":
            return SemVer(self.major + 1, 0, 0)
        raise ValueError(f"invalid version bump: {level!r}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class VersionState:
    plugin: SemVer
    components: dict[str, SemVer]


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def read_versions_json(repo_root: Path) -> dict[str, object]:
    path = Path(repo_root) / "versions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("versions.json root must be an object")
    return data


def load_version_state(repo_root: Path) -> VersionState:
    data = read_versions_json(repo_root)
    if data.get("schemaVersion") != 1:
        raise ValueError("versions.json schemaVersion must be 1")
    component_data = data.get("components")
    if not isinstance(component_data, dict):
        raise ValueError("versions.json components must be an object")
    expected = set(COMPONENTS.values())
    if set(component_data) != expected:
        raise ValueError("versions.json components do not match the required component set")

    plugin = SemVer.parse(data.get("pluginVersion"))  # type: ignore[arg-type]
    components = {
        alias: SemVer.parse(component_data[directory])  # type: ignore[arg-type]
        for alias, directory in COMPONENTS.items()
    }
    return VersionState(plugin=plugin, components=components)


def _read_json_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{label} is missing")
        return None
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{label} is unreadable: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} root must be an object")
        return None
    return value


def validate_version_state(repo_root: Path) -> list[str]:
    root = Path(repo_root)
    errors: list[str] = []
    lock = _read_json_object(root / "versions.json", "versions.json", errors)
    if lock is None:
        return errors

    if lock.get("schemaVersion") != 1:
        errors.append("versions.json schemaVersion must be 1")

    lock_plugin: SemVer | None = None
    raw_plugin = lock.get("pluginVersion")
    try:
        lock_plugin = SemVer.parse(raw_plugin)  # type: ignore[arg-type]
    except ValueError:
        errors.append(f"versions.json pluginVersion is invalid: {raw_plugin!r}")

    expected_directories = set(COMPONENTS.values())
    raw_components = lock.get("components")
    parsed_components: dict[str, SemVer] = {}
    if not isinstance(raw_components, dict):
        errors.append("versions.json components must be an object")
        raw_components = {}
    else:
        missing = sorted(expected_directories - set(raw_components))
        extra = sorted(set(raw_components) - expected_directories)
        if missing:
            errors.append(f"versions.json components missing: {', '.join(missing)}")
        if extra:
            errors.append(f"versions.json components extra: {', '.join(extra)}")

    for alias, directory in COMPONENTS.items():
        if directory not in raw_components:
            continue
        raw_version = raw_components[directory]
        try:
            parsed_components[alias] = SemVer.parse(raw_version)  # type: ignore[arg-type]
        except ValueError:
            errors.append(f"versions.json component {directory} is invalid: {raw_version!r}")

    manifest = _read_json_object(root / PLUGIN_MANIFEST, "plugin manifest", errors)
    if manifest is not None:
        raw_manifest_version = manifest.get("version")
        try:
            manifest_version = SemVer.parse(raw_manifest_version)  # type: ignore[arg-type]
        except ValueError:
            errors.append(f"plugin manifest version is invalid: {raw_manifest_version!r}")
        else:
            if lock_plugin is not None and lock_plugin != manifest_version:
                errors.append(
                    "plugin version mismatch: "
                    f"versions.json={lock_plugin} plugin.json={manifest_version}"
                )

    for alias, directory in COMPONENTS.items():
        version_path = root / SKILLS_ROOT / directory / "VERSION"
        try:
            raw_version = version_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            errors.append(f"component VERSION is missing: {alias}")
            continue
        except OSError as error:
            errors.append(f"component VERSION is unreadable: {alias}: {error}")
            continue
        try:
            disk_version = SemVer.parse(raw_version)
        except ValueError:
            errors.append(f"component VERSION is invalid: {alias}: {raw_version!r}")
            continue
        lock_version = parsed_components.get(alias)
        if lock_version is not None and lock_version != disk_version:
            errors.append(
                "component version mismatch: "
                f"{alias} versions.json={lock_version} VERSION={disk_version}"
            )

    return errors


def snapshot_component_trees(
    repo_root: Path, excluded: set[str]
) -> dict[str, dict[str, FileRecord]]:
    unknown = excluded - set(COMPONENTS)
    if unknown:
        raise ValueError(f"unknown component aliases: {', '.join(sorted(unknown))}")
    root = Path(repo_root)
    return {
        alias: build_manifest(root / SKILLS_ROOT / directory)
        for alias, directory in COMPONENTS.items()
        if alias not in excluded
    }


def run_command(args: list[str], cwd: Path) -> CommandResult:
    completed = subprocess.run(
        args,
        cwd=Path(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    return CommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
