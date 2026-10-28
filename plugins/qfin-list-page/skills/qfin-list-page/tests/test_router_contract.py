import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = SKILL_ROOT.parent
VALIDATOR_PATH = SKILL_ROOT / "scripts" / "validate_router.py"
SPEC = importlib.util.spec_from_file_location("qfin_router_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
ROUTES = VALIDATOR.ROUTES
validate = VALIDATOR.validate


class RouterContractTests(unittest.TestCase):
    def test_published_router_passes_validator(self):
        self.assertEqual(validate(SKILL_ROOT), [])

    def test_each_platform_maps_to_expected_sibling_skill(self):
        self.assertEqual(
            ROUTES,
            {
                "yushu": "../qifu-yushu-list-page/SKILL.md",
                "jinyumeng": "../qifu-jinyumeng-list-page/SKILL.md",
                "dianxiao": "../qifu-dianxiao-list-page/SKILL.md",
                "zhikexing": "../qifu-zhikexing-list-page/SKILL.md",
                "zhineng-yunying": "../qifu-zhineng-yunying-list-page/SKILL.md",
            },
        )
        for relative_path in ROUTES.values():
            self.assertTrue((SKILL_ROOT / relative_path).resolve().is_file())

    def test_pinned_routing_errors_are_documented(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for code in (
            "PLATFORM_REQUIRED",
            "PLATFORM_CONFLICT",
            "UNSUPPORTED_PLATFORM",
            "CHILD_SKILL_MISSING",
        ):
            self.assertIn(code, text)
        self.assertIn("no fallback", text.lower())

    def test_removing_readiness_passthrough_fails(self):
        errors = self._validate_after_replacing(
            "Preserve child readiness and native status verbatim.", ""
        )
        self.assertTrue(any("readiness" in error.lower() for error in errors))

    def test_adding_yushu_default_fails(self):
        errors = self._validate_after_replacing(
            "## Routing procedure", "DEFAULT_PLATFORM: yushu\n\n## Routing procedure"
        )
        self.assertTrue(any("default" in error.lower() for error in errors))

    def test_removing_exact_one_child_rule_fails(self):
        errors = self._validate_after_replacing(
            "Load exactly one child Skill.", "Load the selected child Skill."
        )
        self.assertTrue(any("exactly one" in error.lower() for error in errors))

    def test_child_owns_work_after_handoff(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("The child owns PageSpec, execution, and validation after handoff.", text)
        self.assertIn("Stop applying parent generation rules after handoff.", text)
        self.assertIn("Pass the unmodified raw request", text)

    def test_prompt_template_contract(self):
        prompt_path = SKILL_ROOT / "references" / "prompt-template.md"
        self.assertTrue(prompt_path.is_file())
        text = prompt_path.read_text(encoding="utf-8")
        first_non_empty = next(line for line in text.splitlines() if line.strip())
        self.assertEqual(first_non_empty, "@figma")
        self.assertIn("qfin-list-page", text)
        self.assertIn("目标平台", text)
        self.assertIn("目标平台（必填，五选一）：毓数 / 金毓盟 / 电销 / 智客星 / 智能运营", text)
        self.assertNotIn("app://", text)

    def test_openai_metadata_contract(self):
        metadata_path = SKILL_ROOT / "agents" / "openai.yaml"
        self.assertTrue(metadata_path.is_file())
        text = metadata_path.read_text(encoding="utf-8")
        self.assertRegex(text, r'(?m)^\s*display_name:\s*["\']?QFIN List Page["\']?\s*$')

        short_match = re.search(
            r'(?m)^\s*short_description:\s*["\'](.+)["\']\s*$', text
        )
        self.assertIsNotNone(short_match)
        self.assertGreaterEqual(len(short_match.group(1)), 25)
        self.assertLessEqual(len(short_match.group(1)), 64)
        self.assertIn("$qfin-list-page", text)

        implicit_match = re.search(
            r"(?m)^\s*allow_implicit_invocation:\s*(\w+)\s*$", text
        )
        if implicit_match:
            self.assertEqual(implicit_match.group(1).lower(), "true")

    def _validate_after_replacing(self, old: str, new: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tempdir:
            copied_skills = Path(tempdir) / "skills"
            shutil.copytree(SKILLS_ROOT, copied_skills)
            copied_router = copied_skills / "qfin-list-page"
            skill_path = copied_router / "SKILL.md"
            original = skill_path.read_text(encoding="utf-8")
            self.assertIn(old, original)
            skill_path.write_text(original.replace(old, new, 1), encoding="utf-8")
            return validate(copied_router)


if __name__ == "__main__":
    unittest.main()
