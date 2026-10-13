import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_skill_contract.py"


class SkillContractValidatorTest(unittest.TestCase):
    def run_validator(self, skill_root: Path) -> subprocess.CompletedProcess[str]:
        self.assertTrue(VALIDATOR.exists(), "contract validator must be implemented")
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(skill_root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def copy_skill(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        copied_root = Path(temp_dir.name) / "qifu-jinyumeng-list-page"
        shutil.copytree(SKILL_ROOT, copied_root)
        return temp_dir, copied_root

    def append_component_map(self, copied_root: Path, addition: str) -> None:
        reference_file = copied_root / "references" / "component-map.md"
        reference_file.write_text(
            reference_file.read_text(encoding="utf-8") + addition,
            encoding="utf-8",
        )

    def test_published_skill_satisfies_draft_contract(self) -> None:
        result = self.run_validator(SKILL_ROOT)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS qifu-jinyumeng-list-page 0.7.2 (draft+acceptance_trial)", result.stdout)

    def test_missing_platform_reference_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        (copied_root / "references" / "platform-jinyumeng.md").unlink()

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("platform-jinyumeng.md", result.stdout)

    def test_openai_metadata_must_disable_implicit_invocation(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        metadata_file = copied_root / "agents" / "openai.yaml"
        metadata_file.write_text(
            metadata_file.read_text(encoding="utf-8").replace(
                "allow_implicit_invocation: false", "allow_implicit_invocation: true"
            ),
            encoding="utf-8",
        )

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("allow_implicit_invocation", result.stdout)

    def test_missing_failure_closed_gate_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        skill_file = copied_root / "SKILL.md"
        skill_file.write_text(
            skill_file.read_text(encoding="utf-8").replace("生成或修改 Figma 页面请求必须停止", ""),
            encoding="utf-8",
        )

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("生成或修改 Figma 页面请求必须停止", result.stdout)

    def test_forbidden_yushu_node_id_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        reference_file = copied_root / "references" / "component-map.md"
        reference_file.write_text(
            reference_file.read_text(encoding="utf-8")
            + "\nforbidden fixture: "
            + "3639"
            + ":1529\n",
            encoding="utf-8",
        )

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("3639" + ":1529", result.stdout)

    def test_missing_draft_readiness_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        skill_file = copied_root / "SKILL.md"
        skill_file.write_text(
            skill_file.read_text(encoding="utf-8").replace("readiness=draft", ""),
            encoding="utf-8",
        )

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("readiness=draft", result.stdout)

    def test_forbidden_platform_filename_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        self.append_component_map(copied_root, "\n" + "platform-" + "yushu.md\n")

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("platform-" + "yushu.md", result.stdout)

    def test_unapproved_generic_node_id_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        self.append_component_map(copied_root, "\nPENDING candidate node `4931:6330`\n")

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unapproved node ID", result.stdout)

    def test_unconfirmed_hex_color_remains_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        self.append_component_map(copied_root, "\nPENDING color #3366FF\n")

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unconfirmed hex color", result.stdout)

    def test_unconfirmed_pixel_value_outside_allowlist_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        self.append_component_map(copied_root, "\nPENDING width 999px\n")

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unapproved pixel value", result.stdout)

    def test_unconfirmed_variable_token_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        self.append_component_map(copied_root, "\nPENDING token --qifu-color-primary\n")

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unconfirmed variable token", result.stdout)

    def test_unconfirmed_menu_bullet_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        self.append_component_map(copied_root, "\n- 菜单条目：账户管理\n")

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-allowlisted scaffold bullet", result.stdout)

    def test_unlimited_length_node_id_is_rejected(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        self.append_component_map(copied_root, "\nPENDING candidate node 4931123:6330123\n")

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unapproved node ID", result.stdout)

    def test_metadata_true_value_cannot_be_hidden_by_false_comment(self) -> None:
        temp_dir, copied_root = self.copy_skill()
        self.addCleanup(temp_dir.cleanup)
        metadata_file = copied_root / "agents" / "openai.yaml"
        metadata_file.write_text(
            metadata_file.read_text(encoding="utf-8").replace(
                "allow_implicit_invocation: false",
                "allow_implicit_invocation: true\n# allow_implicit_invocation: false",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(copied_root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("policy.allow_implicit_invocation must be false", result.stdout)


if __name__ == "__main__":
    unittest.main()
