import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_skill_contract.py"


class SkillContractValidatorTest(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(VALIDATOR), str(root)], capture_output=True, text=True, check=False)

    def copy_skill(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        copied_root = Path(temp_dir.name) / "qifu-dianxiao-list-page"
        shutil.copytree(SKILL_ROOT, copied_root)
        return temp_dir, copied_root

    def test_published_skill_satisfies_draft_contract(self) -> None:
        result = self.run_validator(SKILL_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS qifu-dianxiao-list-page 0.1.0 (draft)", result.stdout)

    def test_missing_platform_reference_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        (copied_root / "references" / "platform-dianxiao.md").unlink()
        result = self.run_validator(copied_root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("platform-dianxiao.md", result.stdout)

    def test_cross_platform_identity_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        skill = copied_root / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nplatform=yushu\n", encoding="utf-8")
        result = self.run_validator(copied_root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cross-platform identity", result.stdout)

    def test_unapproved_node_id_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        mapping = copied_root / "references" / "component-map.md"
        mapping.write_text(mapping.read_text(encoding="utf-8") + "\nPENDING node `9999:9999`\n", encoding="utf-8")
        result = self.run_validator(copied_root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unapproved node ID", result.stdout)

    def test_implicit_invocation_must_stay_disabled_while_draft(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        metadata = copied_root / "agents" / "openai.yaml"
        metadata.write_text(metadata.read_text(encoding="utf-8").replace("allow_implicit_invocation: false", "allow_implicit_invocation: true"), encoding="utf-8")
        result = self.run_validator(copied_root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("allow_implicit_invocation: false", result.stdout)


if __name__ == "__main__":
    unittest.main()
