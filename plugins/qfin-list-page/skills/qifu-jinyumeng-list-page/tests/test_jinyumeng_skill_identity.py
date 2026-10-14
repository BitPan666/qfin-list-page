import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_REFERENCES = (
    "page-rules.md",
    "component-map.md",
    "component-invocation-contract.md",
    "structural-validation.md",
    "platform-jinyumeng.md",
)
FORBIDDEN_TEXT = (
    "platform-" + "yushu.md",
    "platform-" + "dianxiao.md",
    "3639" + ":1529",
    "3650" + ":998",
    "3478" + ":657",
    "3473" + ":36837",
    "3802" + ":107",
    "3433" + ":8257",
)


class JinyumengSkillIdentityTest(unittest.TestCase):
    def test_required_draft_files_exist(self) -> None:
        required = (
            "SKILL.md",
            "VERSION",
            "agents/openai.yaml",
            "scripts/validate_skill_contract.py",
            *(f"references/{name}" for name in REQUIRED_REFERENCES),
        )
        for relative_path in required:
            self.assertTrue((SKILL_ROOT / relative_path).is_file(), relative_path)

    def test_skill_identity_is_jinyumeng_specific(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)

        self.assertIsNotNone(frontmatter)
        self.assertRegex(frontmatter.group(1), r"(?m)^name:\s*qifu-jinyumeng-list-page\s*$")
        self.assertRegex(frontmatter.group(1), r"(?m)^description:\s*Use when .+list pages.*$")
        self.assertIn("platform=jinyumeng", skill_text)
        self.assertIn("readiness=ready", skill_text)

    def test_ready_preserves_runtime_validation_and_platform_isolation(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("目标 Page 由用户指定", skill_text)
        self.assertIn("DEFERRED 反馈状态", skill_text)
        self.assertNotIn("PENDING 完整平台规则", skill_text)
        self.assertIn("CONFIRMED 完整组件映射", skill_text)
        self.assertNotIn("PENDING 完整组件映射", skill_text)
        self.assertIn("结构和视觉均为 PASS", skill_text)
        self.assertIn("不得回退到 `qifu-yushu-list-page`、`qifu-list-page`", skill_text)
        self.assertIn("禁止手绘占位", skill_text)

    def test_ready_allows_user_selected_page_with_validation(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        validation = (SKILL_ROOT / "references/structural-validation.md").read_text(encoding="utf-8")
        self.assertIn("目标 Page 由用户指定", skill)
        self.assertIn("不限定测试 Page", skill)
        self.assertIn("保护无关已有内容", skill)
        self.assertIn("structuralValidation", validation)
        self.assertIn("visualValidation", validation)
        self.assertNotIn("5037:8717", validation)
        self.assertNotIn("正式业务 Page 继续 BLOCKED", skill)

    def test_ui_metadata_requires_explicit_invocation(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn('display_name: "Qifu Jinyumeng List Page"', metadata)
        self.assertIn("$qifu-jinyumeng-list-page", metadata)
        self.assertIn("@figma", metadata)
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_references_keep_pending_items_and_do_not_guess_platform_details(self) -> None:
        pending_references = (
            "component-invocation-contract.md",
            "structural-validation.md",
            "platform-jinyumeng.md",
        )
        for filename in pending_references:
            reference_text = (SKILL_ROOT / "references" / filename).read_text(encoding="utf-8")
            self.assertIn("PENDING", reference_text, filename)
            self.assertIn("不得猜测", reference_text, filename)

        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("PENDING", component_map)
        self.assertIn("不得猜测", component_map)

        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")
        self.assertIn("DEFERRED", page_rules)
        self.assertNotIn("PENDING empty/loading/error", page_rules)

    def test_confirmed_filter_layout_contract_is_recorded(self) -> None:
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")

        for required in (
            "控件本体固定宽度 `240px`",
            "圆角 `4px`",
            "垂直内边距 `28px`",
            "行间距 `20px`",
            "1366px",
            "每行 `3` 个",
            "每行 `4–5` 个",
        ):
            self.assertIn(required, page_rules)

    def test_confirmed_filter_slot_grid_and_action_wrapping_contract_is_recorded(self) -> None:
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )
        validation = (SKILL_ROOT / "references" / "structural-validation.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "等宽槽位网格",
            "columnCount = max(1, floor(filterSlotWidth / itemSlotWidth))",
            "cellWidth = filterSlotWidth / columnCount",
            "操作组作为一个完整槽位",
            "actionRow = floor(visibleFilterCount / columnCount) + 1",
            "actionColumn = visibleFilterCount % columnCount + 1",
            "2 个筛选项",
            "第 3 列",
            "3 个筛选项",
            "下一行第 1 列",
            "visibleFilterCount = 2 × columnCount - 1",
        ):
            self.assertIn(required, page_rules)

        self.assertIn("查询、重置、展开/收起不得拆分或分别换行", invocation)
        self.assertIn("筛选项与操作组按同一列宽数组定位", validation)
        self.assertNotIn("PENDING exact horizontal Filter Item calculations", validation)

    def test_confirmed_jinyumeng_filter_components_and_tokens_are_mapped(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(
            encoding="utf-8"
        )
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "Entry / Jinyumeng / Input",
            "`5010:19`",
            "Entry / Jinyumeng / Select",
            "`5010:7028`",
            "Entry / Jinyumeng / DatePicker",
            "`5010:7039`",
            "Entry / Jinyumeng / DateRange",
            "`5010:7055`",
            "Data Display / Jinyumeng / Filter Item",
            "`5011:62`",
            "`240 × 32`",
            "`76px`",
            "右对齐",
            "边框/--qifu-border-color-default",
            "--qifu-radius-4",
            "controlSlot 筛选控件插槽",
        ):
            self.assertIn(required, component_map)
        for required in (
            "label 标题",
            "controlSlot 筛选控件插槽",
            "display 显示形式",
            "暴露的嵌套实例",
        ):
            self.assertIn(required, invocation)

    def test_confirmed_jinyumeng_page_shells_and_slots_are_mapped(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(
            encoding="utf-8"
        )
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "Templates / Jinyumeng / Content Shell",
            "`5022:2`",
            "Templates / Jinyumeng / Workspace Shell",
            "`5022:8`",
            "Templates / Jinyumeng / List Page Shell",
            "`5022:16`",
            "tabsSlot 系统内页签插槽",
            "filterSlot 筛选区插槽",
            "actionSlot 独立操作栏插槽",
            "tableSlot 表格区插槽",
            "sidebarSlot 侧边导航插槽",
            "showActionBar 显示独立操作栏",
        ):
            self.assertIn(required, component_map)
        for required in (
            "List Page Shell",
            "Workspace Shell",
            "Content Shell",
            "showActionBar 显示独立操作栏",
        ):
            self.assertIn(required, invocation)

    def test_shared_feedback_components_are_mapped_without_inventing_layout(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(
            encoding="utf-8"
        )
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "Data Display / Loading / Spinner",
            "`3267:8`",
            "Data Display / Loading / Loading",
            "`3268:29`",
            "Data Display 数据展示 / Empty 空状态 / Empty",
            "`3621:45`",
            "text 提示文案",
            "content 内容",
            "status 状态",
            "noData 暂无数据",
            "networkError 网络错误",
            "error 失败",
        ):
            self.assertIn(required, component_map)
        self.assertIn("反馈状态的页面内布局为 DEFERRED", invocation)

    def test_closed_component_mapping_pending_items_are_removed(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(
            encoding="utf-8"
        )
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")

        self.assertNotIn("PENDING 完整组件映射", skill_text)
        self.assertNotIn("PENDING approved Jinyumeng input/select/date", component_map)
        self.assertNotIn("PENDING approved reusable Jinyumeng filter component", invocation)
        self.assertNotIn("PENDING exact semantic border-color token", page_rules)

    def test_confirmed_sidebar_component_contract_is_recorded(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")

        for required in (
            "JYM-SideMenuItem",
            "`4746:46261`",
            "`Level`",
            "`Has Submenu`",
            "`State`",
            "`1`、`2`、`3`",
            "`Default`、`Selected`、`Hover`、`Disabled`",
            "共 `24` 个变体",
            "Instance swap",
        ):
            self.assertIn(required, component_map)

    def test_confirmed_content_surface_tabs_and_action_region_contract_is_recorded(self) -> None:
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")

        for required in (
            "白色内容承载面",
            "侧边栏右侧 `20px`",
            "视口右侧 `20px`",
            "系统内页签栏",
            "独立操作栏高度固定 `52px`",
            "左右内边距 `20px`",
            "左对齐或右对齐",
            "表格上方",
        ):
            self.assertIn(required, page_rules)

    def test_table_action_alignment_uses_full_width_auto_layout(self) -> None:
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")
        validation = (SKILL_ROOT / "references" / "structural-validation.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "primaryAxisAlignItems=MAX",
            "primaryAxisAlignItems=MIN",
            "Hug 宽度容器",
        ):
            self.assertIn(required, page_rules)

        self.assertIn("操作组 Auto Layout 宽度 = 工具栏可用宽度", validation)
        self.assertIn("右对齐回读 `MAX`", validation)
        self.assertIn("左对齐回读 `MIN`", validation)

    def test_overall_effect_trial_uses_five_to_eight_business_columns(self) -> None:
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")
        validation = (SKILL_ROOT / "references" / "structural-validation.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("整体效果验收默认使用 `5–8` 个业务字段", page_rules)
        self.assertIn("选择列不计入", page_rules)
        self.assertIn("可见业务字段数为 `5–8`", validation)

    def test_sidebar_visuals_follow_the_latest_master(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("JYM-SideMenuItem 最新母版是视觉状态的唯一事实源", component_map)
        self.assertIn("不得在 Skill 中硬编码旧的颜色、字重或选中效果", component_map)

    def test_confirmed_internal_tab_and_shared_button_components_are_mapped(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")

        for required in (
            "Data Display / Tag / Tag",
            "`3178:9659`",
            "`4902:2195`",
            "`4902:2065`",
            "Base / Button / Button",
            "`2381:2318`",
            "`2381:788`",
            "`2381:482`",
        ):
            self.assertIn(required, component_map)

    def test_confirmed_jinyumeng_table_family_and_typography_are_recorded(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")

        for required in (
            "Data Display / Jinyumeng Table / Header Cell",
            "`4968:8897`",
            "Data Display / Jinyumeng Table / Content Text",
            "`4972:8909`",
            "Data Display / Jinyumeng Table / Content Cell",
            "`4972:8914`",
            "Data Display / Jinyumeng Table / Selection Cell",
            "`4972:53985`",
            "Data Display / Jinyumeng Table / Row",
            "`4972:54013`",
            "Data Display / Jinyumeng Table / Shell",
            "`4975:9829`",
            "`4975:9830`",
            "`4975:9855`",
            "xlarge 超大 48px",
            "basic 基础",
        ):
            self.assertIn(required, component_map)

        for required in (
            "表格标题可选",
            "`16px`",
            "Semibold",
            "单元格高度固定 `48px`",
            "#595C72",
            "Medium",
            "#121736",
            "Regular",
            "`14px`",
            "基础类型表格",
        ):
            self.assertIn(required, page_rules)

    def test_jinyumeng_header_component_and_fixed_structure_are_recorded(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")

        for required in (
            "Navigation / HeaderMenu / Jinyumeng Header",
            "`4993:1440`",
            "Jinyumeng Header / Base Spec / v1",
            "`4993:1437`",
            "accountName 用户名称",
        ):
            self.assertIn(required, component_map)
        for required in (
            "品牌锁定区",
            "通知入口",
            "用户区",
            "透明背景",
            "高度固定 `56px`",
            "左右内边距 `20px`",
        ):
            self.assertIn(required, page_rules)
        self.assertIn("accountName 用户名称", invocation)
        self.assertIn("`金毓盟/Light`", invocation)

    def test_dynamic_table_column_composition_contract_is_recorded(self) -> None:
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "columns.length",
            "每列 1 个 Jinyumeng Header Cell",
            "每行每列 1 个 Jinyumeng Content Cell",
            "Content Text / Tag / Action Content-V2",
            "Content Cell.contentSlot",
            "Row.cellsSlot",
            "Shell.rowsSlot",
            "Shell.headerSlot",
            "同一列宽数组",
        ):
            self.assertIn(required, invocation)

    def test_dynamic_table_semantic_width_and_overflow_rules_are_recorded(self) -> None:
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")

        for required in (
            "短 ID",
            "名称",
            "长文本",
            "单行省略",
            "数字",
            "右对齐",
            "日期时间",
            "状态",
            "操作",
            "横向滚动",
            "表头与每行使用同一列宽数组",
        ):
            self.assertIn(required, page_rules)

    def test_action_content_and_table_status_tag_are_mapped(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")

        for required in (
            "Data Display / Table / Cell Content / Action Content-V2",
            "`3678:8875`",
            "action1 文案",
            "showAction2 显示动作2",
            "dangerAction 危险项",
            "1–4",
            "金毓盟主题色",
            "表格状态 Tag",
            "medium",
            "square",
        ):
            self.assertIn(required, component_map)

    def test_dynamic_selection_counts_and_shell_height_are_verifiable(self) -> None:
        validation = (SKILL_ROOT / "references" / "structural-validation.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "Header Cell 数量 = columns.length",
            "Content Cell 数量 = data.length × columns.length",
            "Selection Cell 数量 = data.length + 1",
            "requiredTableHeight = headerSlot.height + rowsSlot.height + paginationSlot.height",
            "48px",
        ):
            self.assertIn(required, validation)

    def test_pagination_component_and_properties_are_mapped(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "Navigation / Pagination / Pagination",
            "`3698:482`",
            "`3698:483`",
            "pageCount 页数",
            "current 当前页",
            "total 总数",
            "pageSize 每页条数",
            "showJumper 显示快速跳转",
        ):
            self.assertIn(required, component_map)
        self.assertIn("paginationSlot", invocation)
        self.assertIn("pageCount 页数", invocation)

    def test_pagination_alignment_order_and_header_selection_background_are_locked(self) -> None:
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(
            encoding="utf-8"
        )
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )
        validation = (SKILL_ROOT / "references" / "structural-validation.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "paginationRight = tableRight = tableSurfaceRight - 20px",
            "上一页箭头向左",
            "下一页箭头向右",
            "`← 1 2（当前页）3 4 5 … 8 →`",
            "背景色/--qifu-bg-color-canvas",
            "Header Selection Cell",
            "checkbox 方框本体保持白色",
        ):
            self.assertTrue(
                any(required in text for text in (page_rules, component_map, invocation, validation)),
                msg=f"missing confirmed pagination/header-selection rule: {required}",
            )

        for required in (
            "paginationRight = tableRight = tableSurfaceRight - 20px",
            "上一页箭头向左",
            "下一页箭头向右",
            "背景色/--qifu-bg-color-canvas",
        ):
            self.assertIn(required, validation)

    def test_header_cell_properties_and_deterministic_width_algorithm_are_recorded(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")
        page_rules = (SKILL_ROOT / "references" / "page-rules.md").read_text(encoding="utf-8")
        invocation = (SKILL_ROOT / "references" / "component-invocation-contract.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "headerText 表头文案",
            "showSort 显示排序",
            "showFilter 显示筛选",
            "sortState 排序状态",
        ):
            self.assertIn(required, component_map)
            self.assertIn(required, invocation)
        for required in (
            "columns[].width",
            "表头与样例单元格内容的最大固有宽度",
            "剩余宽度",
            "弹性列",
            "不压缩",
            "内容总宽度",
        ):
            self.assertIn(required, page_rules)

    def test_shared_action_evidence_danger_options_and_status_theme_mapping_are_closed(self) -> None:
        component_map = (SKILL_ROOT / "references" / "component-map.md").read_text(encoding="utf-8")

        for required in (
            "共享基础表格内容组件",
            "None 无",
            "Action1 动作1",
            "Action4 动作4",
            "成功/启用",
            "失败/禁用",
            "等待",
            "运行/处理中",
            "中性",
        ):
            self.assertIn(required, component_map)

    def test_online_menu_icons_must_map_to_real_jinyumeng_icon_components(self) -> None:
        platform = (SKILL_ROOT / "references" / "platform-jinyumeng.md").read_text(encoding="utf-8")

        self.assertIn("线上平台菜单", platform)
        self.assertIn("真实 `Icon/jinyumeng/*` 组件", platform)
        self.assertIn("禁止手绘、猜测或用通用占位图标替代", platform)

    def test_package_contains_no_forbidden_cross_platform_artifacts(self) -> None:
        protected_paths = (
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "agents" / "openai.yaml",
            *(SKILL_ROOT / "references" / name for name in REQUIRED_REFERENCES),
            SKILL_ROOT / "scripts" / "validate_skill_contract.py",
        )
        for path in protected_paths:
            content = path.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_TEXT:
                self.assertNotIn(forbidden, content, f"{path.relative_to(SKILL_ROOT)}: {forbidden}")


if __name__ == "__main__":
    unittest.main()
