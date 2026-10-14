import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class DianxiaoSkillIdentityTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        path = SKILL_ROOT / relative_path
        self.assertTrue(path.is_file(), f"missing required file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def test_isolated_identity_and_fail_closed_gate(self) -> None:
        skill = self.read("SKILL.md")
        self.assertIn("name: qifu-dianxiao-list-page", skill)
        self.assertIn("platform=dianxiao", skill)
        self.assertIn("readiness=ready", skill)
        self.assertIn("BLOCKED", skill)
        self.assertNotIn("platform=yushu", skill)
        self.assertNotIn("platform=jinyumeng", skill)

    def test_platform_rules_and_component_gaps_are_explicit(self) -> None:
        platform = self.read("references/platform-dianxiao.md")
        rules = self.read("references/page-rules.md")
        mapping = self.read("references/component-map.md")

        for expected in ("全部菜单", "收藏菜单", "#009E73", "#262626", "#EBEBEB", "200px", "16px"):
            self.assertIn(expected, platform)
        for expected in ("8px", "200px", "28px", "12px", "WRAP", "Data Display / Table / Shell-V2"):
            self.assertIn(expected, rules)
        for expected in (
            "1366px × 768px",
            "主按钮 → 次按钮",
            "距白色承载面顶部 `20px`",
            "距最后一行数据底部 `12px`",
            "上一页箭头向左",
            "下一页箭头向右",
        ):
            self.assertIn(expected, rules)
        for expected in (
            "Navigation / Dianxiao SideMenu / MenuRoot",
            "Navigation / Dianxiao SideMenu / SideMenuItem",
            "顶部 Header",
            "只包含三个原生 Slot",
            "不存在 `actionSlot`",
            "1078px",
        ):
            self.assertIn(expected, mapping)
        self.assertIn("Navigation / HeaderMenu / Dianxiao Header", mapping)
        self.assertIn("5824:4491", mapping)
        self.assertIn("1118 × 502px", mapping)
        self.assertIn("1366 × 768px", mapping)
        self.assertNotIn("| 顶部 Header | PENDING 正式组件 | PENDING |", mapping)

    def test_selected_icon_and_short_viewport_rules_are_explicit(self) -> None:
        platform = self.read("references/platform-dianxiao.md")
        contract = self.read("references/component-invocation-contract.md")
        validation = self.read("references/structural-validation.md")

        self.assertIn("选中且有 Icon", platform)
        self.assertIn("Icon 必须解析为电销主题色", contract)
        self.assertIn("Dianxiao Menu Scroll Viewport", contract)
        self.assertIn("1366px × 768px", validation)
        self.assertIn("主按钮 → 次按钮", validation)
        self.assertIn("距最后一行数据底部 `12px`", validation)

    def test_dynamic_table_uses_content_aware_visual_spacing(self) -> None:
        skill = self.read("SKILL.md")
        rules = self.read("references/page-rules.md")
        validation = self.read("references/structural-validation.md")

        self.assertIn("内容感知列宽", skill)
        self.assertIn("禁止把所有业务列机械等宽", rules)
        self.assertIn("统一视觉尾部留白", rules)
        self.assertIn("选择列固定 `40px`", rules)
        self.assertIn("操作列内容宽度 + 右侧 `20px`", rules)
        self.assertIn("visualTrailingGap", rules)
        self.assertIn("视觉尾部留白差值不超过 `1px`", validation)
        self.assertIn("列宽总和等于表格可视宽度", validation)


if __name__ == "__main__":
    unittest.main()
