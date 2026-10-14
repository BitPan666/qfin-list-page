import hashlib
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class YushuSkillIdentityTest(unittest.TestCase):
    def test_skill_identity_is_yushu_specific(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)

        self.assertIsNotNone(frontmatter)
        self.assertRegex(frontmatter.group(1), r"(?m)^name:\s*qifu-yushu-list-page\s*$")
        self.assertRegex(
            frontmatter.group(1),
            r"(?m)^description:\s*Use when .*Yushu.*list pages.*$",
        )

    def test_skill_is_locked_to_yushu_platform(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("本 Skill 固定用于毓数平台", skill_text)
        self.assertIn("platform=yushu", skill_text)
        self.assertNotIn("platform-jinyumeng.md", skill_text)
        self.assertNotIn("platform-dianxiao.md", skill_text)

    def test_ui_metadata_targets_yushu_skill(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn('display_name: "Qifu Yushu List Page"', metadata)
        self.assertIn("$qifu-yushu-list-page", metadata)
        self.assertIn("毓数", metadata)
        self.assertIn("@figma", metadata)
        self.assertIn("显式多选框", metadata)

    def test_frozen_yushu_references_match_1_3_3_baseline(self) -> None:
        expected = {
            "VERSION": "a74a0cf84ef0b15e01e64746c3465813312b763796f4f6362b092f092dccb8b5",
            "references/component-invocation-contract.md": "7f3f431a1b490281405025c3cb8fc74f12c893c5f9944f0579bd7c0ffaf7b083",
            "references/component-map.md": "4c7f0cf39ee0a10f37b57dadc22befc03959cb97bb8de343be17ee2de6e5853e",
            "references/page-rules.md": "01f763f3c5631dba4fd503c7bd0d0eba1a811f7138e0bc265f8626eae8192875",
            "references/platform-yushu.md": "3de50b89e2f0df8375435923e81a77f0e40f70aa4d84672f5d57be15dc02a595",
            "references/structural-validation.md": "c59fb5a3f0e57cd8ade62225784e8b8e56215ab642722a1f1b31533bb2a123a9",
        }

        for relative_path, expected_hash in expected.items():
            digest = hashlib.sha256((SKILL_ROOT / relative_path).read_bytes()).hexdigest()
            self.assertEqual(digest, expected_hash, relative_path)


if __name__ == "__main__":
    unittest.main()
