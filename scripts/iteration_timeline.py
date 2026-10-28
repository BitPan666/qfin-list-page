#!/usr/bin/env python3
"""Show this checkout's commit timeline and suggest a new recovery branch; never mutate Git."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import shlex
import subprocess


def timeline(repo: Path, before: str | None = None) -> dict:
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True, stderr=subprocess.PIPE).strip()

    deadline = None
    if before:
        deadline = datetime.fromisoformat(before.replace('Z', '+00:00'))
        if deadline.tzinfo is None:
            raise ValueError('before must include an explicit timezone, for example +08:00')
    root = Path(git('rev-parse', '--show-toplevel'))
    rows = []
    for line in git('log', '--first-parent', '--format=%H%x09%cI%x09%s', 'HEAD').splitlines():
        sha, date, subject = line.split('\t', 2)
        date = datetime.fromisoformat(date).astimezone(timezone(timedelta(hours=8))).isoformat()
        rows.append({'sha': sha, 'committedAt': date, 'subject': subject})
    eligible = [row for row in rows if deadline is None or datetime.fromisoformat(row['committedAt']) <= deadline]
    selected = max(eligible, key=lambda row: datetime.fromisoformat(row['committedAt'])) if eligible else None
    data = {'status': 'OK' if selected else 'NO_CHECKPOINT', 'repository': str(root),
            'branch': git('branch', '--show-current') or None,
            'dirtyWorktree': bool(git('status', '--porcelain')), 'selected': selected,
            'checkpoints': rows[:50], 'readOnly': True}
    if selected:
        stamp = datetime.fromisoformat(selected['committedAt']).astimezone(timezone(timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
        branch = f"codex/restore-{stamp}-{selected['sha'][:7]}"
        destination = root.parent / (root.name + '-restore-' + stamp + '-' + selected['sha'][:7])
        data['restoreCommand'] = shlex.join(['git', '-C', str(root), 'worktree', 'add', '-b', branch, str(destination), selected['sha']])
        data['note'] = 'Review and run restoreCommand to open a separate checkout at that checkpoint. Existing branches, dirty files, and later commits remain intact. Use a reviewed git revert for a history-preserving rollback of a specific iteration.'
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--before', help='ISO timestamp with timezone; most recent ancestor checkpoint at/before this time')
    args = parser.parse_args()
    try:
        data = timeline(args.repo, args.before)
    except (ValueError, subprocess.CalledProcessError, OSError) as exc:
        print(json.dumps({'status': 'ERROR', 'error': str(exc), 'readOnly': True}))
        return 2
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if data['selected'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
