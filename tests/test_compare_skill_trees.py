import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.compare_skill_trees import build_manifest, compare_trees


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "compare_skill_trees.py"


class CompareSkillTreesTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        (self.source / "nested").mkdir(parents=True)
        (self.source / "SKILL.md").write_text("skill\n", encoding="utf-8")
        (self.source / "nested" / "config.json").write_text("{}\n", encoding="utf-8")
        os.chmod(self.source / "SKILL.md", 0o640)
        shutil.copytree(self.source, self.target, copy_function=shutil.copy2)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_identical_trees_match_and_cli_prints_pass(self):
        self.assertEqual(compare_trees(self.source, self.target), [])

        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(self.source), str(self.target)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "PASS")

    def test_changed_content_is_reported(self):
        (self.target / "SKILL.md").write_text("changed\n", encoding="utf-8")
        self.assertIn("changed:SKILL.md", compare_trees(self.source, self.target))

    def test_extra_target_file_is_reported(self):
        (self.target / "extra.txt").write_text("extra\n", encoding="utf-8")
        self.assertIn("extra:extra.txt", compare_trees(self.source, self.target))

    def test_missing_target_file_is_reported(self):
        (self.target / "nested" / "config.json").unlink()
        self.assertIn("missing:nested/config.json", compare_trees(self.source, self.target))

    def test_manifest_uses_posix_paths_sha256_and_permission_bits(self):
        manifest = build_manifest(self.source)
        self.assertEqual(set(manifest), {"SKILL.md", "nested/config.json"})
        record = manifest["SKILL.md"]
        self.assertRegex(record.sha256, r"^[0-9a-f]{64}$")
        self.assertEqual(record.mode, 0o640)

    def test_changed_permission_bits_are_reported(self):
        os.chmod(self.target / "SKILL.md", 0o600)
        self.assertIn("mode:SKILL.md", compare_trees(self.source, self.target))


if __name__ == "__main__":
    unittest.main()
