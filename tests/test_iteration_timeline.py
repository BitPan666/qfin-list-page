from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/iteration_timeline.py'


class IterationTimelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git('init', '-q', '-b', 'codex/test')
        self.git('config', 'user.name', 'Timeline Test')
        self.git('config', 'user.email', 'timeline@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.first = self.commit('2026-10-28T09:00:00+08:00', 'one')
        self.second = self.commit('2026-10-28T11:00:00+08:00', 'two')

    def git(self, *args, env=None):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True, env=env).strip()

    def commit(self, date, text):
        (self.repo / 'source.txt').write_text(text)
        self.git('add', 'source.txt')
        env = {**os.environ, 'GIT_AUTHOR_DATE': date, 'GIT_COMMITTER_DATE': date}
        self.git('commit', '-q', '-m', text, env=env)
        return self.git('rev-parse', 'HEAD')

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), '--repo', str(self.repo), *args], text=True, capture_output=True)

    def test_time_selection_returns_safe_restore_command_without_changing_dirty_work(self):
        (self.repo / 'source.txt').write_text('uncommitted')
        before = self.git('status', '--porcelain')
        result = self.run_script('--before', '2026-10-28T10:00:00+08:00')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['selected']['sha'], self.first)
        self.assertTrue(data['dirtyWorktree'])
        self.assertIn(self.first, data['restoreCommand'])
        self.assertIn('codex/restore-', data['restoreCommand'])
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.second)
        self.assertEqual(self.git('status', '--porcelain'), before)
        self.assertEqual((self.repo / 'source.txt').read_text(), 'uncommitted')

    def test_time_without_timezone_is_rejected(self):
        result = self.run_script('--before', '2026-10-28T10:00:00')
        self.assertEqual(result.returncode, 2)
        self.assertIn('timezone', result.stdout.lower())

    def test_time_before_repository_history_has_no_checkpoint(self):
        result = self.run_script('--before', '2026-10-27T10:00:00+08:00')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'NO_CHECKPOINT')


if __name__ == '__main__':
    unittest.main()
