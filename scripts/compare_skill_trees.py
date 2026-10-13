#!/usr/bin/env python3
"""Compare two Skill trees by relative path, SHA256 content, and mode bits."""

from __future__ import annotations

import hashlib
import stat
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileRecord:
    sha256: str
    mode: int


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(path.readlink().as_posix().encode("utf-8"))
        return digest.hexdigest()

    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path) -> dict[str, FileRecord]:
    """Return records for every file or symlink below *root*."""
    root = Path(root)
    manifest: dict[str, FileRecord] = {}
    for path in sorted(root.rglob("*")):
        if not (path.is_file() or path.is_symlink()):
            continue
        relative_path = path.relative_to(root).as_posix()
        manifest[relative_path] = FileRecord(
            sha256=_digest(path),
            mode=stat.S_IMODE(path.lstat().st_mode),
        )
    return manifest


def compare_trees(source: Path, target: Path) -> list[str]:
    """Return deterministic differences between source and target trees."""
    source_manifest = build_manifest(Path(source))
    target_manifest = build_manifest(Path(target))
    differences: list[str] = []

    for relative_path in sorted(source_manifest.keys() - target_manifest.keys()):
        differences.append(f"missing:{relative_path}")
    for relative_path in sorted(target_manifest.keys() - source_manifest.keys()):
        differences.append(f"extra:{relative_path}")
    for relative_path in sorted(source_manifest.keys() & target_manifest.keys()):
        source_record = source_manifest[relative_path]
        target_record = target_manifest[relative_path]
        if source_record.sha256 != target_record.sha256:
            differences.append(f"changed:{relative_path}")
        if source_record.mode != target_record.mode:
            differences.append(f"mode:{relative_path}")

    return differences


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: compare_skill_trees.py SOURCE TARGET", file=sys.stderr)
        return 2

    source = Path(argv[1])
    target = Path(argv[2])
    if not source.is_dir() or not target.is_dir():
        print("SOURCE and TARGET must both be existing directories", file=sys.stderr)
        return 2

    differences = compare_trees(source, target)
    if differences:
        print("\n".join(differences))
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
