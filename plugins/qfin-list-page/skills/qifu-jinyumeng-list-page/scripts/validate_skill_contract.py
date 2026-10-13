#!/usr/bin/env python3
"""Validate the qifu-jinyumeng-list-page 0.7.2 draft acceptance-trial contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = (
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/page-rules.md",
    "references/component-map.md",
    "references/component-invocation-contract.md",
    "references/structural-validation.md",
    "references/platform-jinyumeng.md",
    "scripts/validate_skill_contract.py",
)
REFERENCE_REQUIREMENTS = {
    "references/page-rules.md": (
        "控件本体固定宽度 `240px`",
        "圆角 `4px`",
        "垂直内边距 `28px`",
        "行间距 `20px`",
        "每行 `3` 个",
        "每行 `4–5` 个",
        "等宽槽位网格",
        "columnCount = max(1, floor(filterSlotWidth / itemSlotWidth))",
        "cellWidth = filterSlotWidth / columnCount",
        "操作组作为一个完整槽位",
        "actionRow = floor(visibleFilterCount / columnCount) + 1",
        "actionColumn = visibleFilterCount % columnCount + 1",
        "visibleFilterCount = 2 × columnCount - 1",
        "白色内容承载面",
        "独立操作栏高度固定 `52px`",
        "表格标题可选",
        "单元格高度固定 `48px`",
        "#595C72",
        "#121736",
        "高度固定 `56px`",
        "横向滚动",
        "`76px`",
        "边框/--qifu-border-color-default",
        "--qifu-radius-4",
        "背景色/--qifu-bg-color-canvas",
        "paginationRight = tableRight = tableSurfaceRight - 20px",
        "上一页箭头向左",
        "下一页箭头向右",
        "DEFERRED",
        "不得猜测",
    ),
    "references/component-map.md": (
        "JYM-SideMenuItem",
        "`4746:46261`",
        "`Level`",
        "`Has Submenu`",
        "`State`",
        "共 `24` 个变体",
        "Instance swap",
        "`3178:9659`",
        "`2381:2318`",
        "Data Display / Jinyumeng Table / Shell",
        "`4975:9829`",
        "`4993:1440`",
        "`3678:8875`",
        "`3698:482`",
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
        "Templates / Jinyumeng / Content Shell",
        "`5022:2`",
        "Templates / Jinyumeng / Workspace Shell",
        "`5022:8`",
        "Templates / Jinyumeng / List Page Shell",
        "`5022:16`",
        "Data Display / Loading / Loading",
        "`3268:29`",
        "Data Display 数据展示 / Empty 空状态 / Empty",
        "`3621:45`",
        "headerText 表头文案",
        "pageCount 页数",
        "背景色/--qifu-bg-color-canvas",
        "checkbox 方框本体保持白色",
        "上一页箭头向左",
        "下一页箭头向右",
        "不得猜测",
    ),
    "references/component-invocation-contract.md": (
        "`4746:46261`",
        "Icon/jinyumeng/*",
        "`3178:9659`",
        "`2381:2318`",
        "`4975:9829`",
        "`4993:1440`",
        "`5011:62`",
        "`5022:16`",
        "`3268:29`",
        "`3621:45`",
        "暴露的嵌套实例",
        "查询、重置、展开/收起不得拆分或分别换行",
        "columns.length",
        "requiredTableHeight",
        "headerText 表头文案",
        "pageCount 页数",
        "背景色/--qifu-bg-color-canvas",
        "paginationRight = tableRight = tableSurfaceRight - 20px",
        "上一页箭头向左",
        "下一页箭头向右",
        "BLOCKED",
        "PENDING",
        "不得猜测",
    ),
    "references/structural-validation.md": (
        "`240px`",
        "`4px`",
        "`28px`",
        "`20px`",
        "`52px`",
        "`48px`",
        "#595C72",
        "#121736",
        "`5011:62`",
        "`5022:16`",
        "`3268:29`",
        "`3621:45`",
        "Header Cell 数量 = columns.length",
        "Selection Cell 数量 = data.length + 1",
        "背景色/--qifu-bg-color-canvas",
        "paginationRight = tableRight = tableSurfaceRight - 20px",
        "上一页箭头向左",
        "下一页箭头向右",
        "筛选项与操作组按同一列宽数组定位",
        "acceptanceTrial=true",
        "目标 Page ID = `5037:8717`",
        "PENDING",
        "不得猜测",
    ),
    "references/platform-jinyumeng.md": (
        "platform=jinyumeng",
        "线上平台菜单",
        "真实 `Icon/jinyumeng/*` 组件",
        "Jinyumeng Table",
        "complete first-level 线上平台菜单 preset",
        "禁止手绘、猜测或用通用占位图标替代",
        "反馈状态标记为 DEFERRED",
        "PENDING",
        "不得猜测",
    ),
}
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
APPROVED_NODE_IDS = {
    "3161:10805",
    "4746:46261",
    "4856:1408",
    "4873:1201",
    "3178:9659",
    "4902:2195",
    "4902:2065",
    "2381:2318",
    "2381:788",
    "2381:482",
    "4968:8897",
    "4968:8898",
    "4972:8909",
    "4972:8910",
    "4972:8914",
    "4972:8915",
    "4972:53985",
    "4972:53986",
    "4972:54013",
    "4972:54014",
    "4975:9829",
    "4975:9830",
    "4975:9855",
    "4993:1437",
    "4993:1440",
    "3678:8875",
    "3698:482",
    "3698:483",
    "5010:19",
    "5010:7028",
    "5010:7039",
    "5010:7055",
    "5011:62",
    "5022:2",
    "5022:8",
    "5022:16",
    "3267:8",
    "3268:29",
    "3621:45",
    "5037:8717",
}
APPROVED_PIXEL_VALUES = {"4px", "14px", "16px", "20px", "28px", "32px", "48px", "52px", "56px", "76px", "240px", "1366px"}
APPROVED_HEX_COLORS = {"#121736", "#595C72"}
APPROVED_VARIABLE_TOKENS = {
    "--qifu-border-color-default",
    "--qifu-button-radius",
    "--qifu-radius-2",
    "--qifu-radius-4",
    "--qifu-bg-color-canvas",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
NODE_ID = re.compile(r"\b\d+:\d+\b")
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
PIXEL_VALUE = re.compile(r"\b\d+(?:\.\d+)?px\b")
VARIABLE_TOKEN = re.compile(r"(?:--[A-Za-z][A-Za-z0-9-]*|VariableID:[A-Za-z0-9_:/-]+)")


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {path}: {exc}")
        return ""


def validate_frontmatter(skill_text: str, errors: list[str]) -> None:
    match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not match:
        errors.append("SKILL.md: missing YAML frontmatter")
        return
    frontmatter = match.group(1)
    if not re.search(r"^name:\s*qifu-jinyumeng-list-page\s*$", frontmatter, re.MULTILINE):
        errors.append("SKILL.md: name must be qifu-jinyumeng-list-page")
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not description or not description.group(1).startswith("Use when"):
        errors.append("SKILL.md: description must start with 'Use when'")


def validate_links(skill_root: Path, markdown_file: Path, text: str, errors: list[str]) -> None:
    for raw_target in MARKDOWN_LINK.findall(text):
        resolved = (markdown_file.parent / raw_target).resolve()
        if not resolved.exists():
            errors.append(f"{markdown_file.relative_to(skill_root)}: broken markdown link {raw_target}")


def validate_implicit_invocation_policy(metadata: str, errors: list[str]) -> None:
    values: list[str] = []
    in_policy = False
    for raw_line in metadata.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not in_policy:
            if raw_line.strip() == "policy:":
                in_policy = True
            continue
        if not raw_line[0].isspace():
            break
        active_line = raw_line.split("#", 1)[0].strip()
        match = re.fullmatch(r"allow_implicit_invocation:\s*(true|false)", active_line)
        if match:
            values.append(match.group(1))
    if values != ["false"]:
        errors.append("agents/openai.yaml: policy.allow_implicit_invocation must be false")


def validate_reference(relative_path: str, text: str, errors: list[str]) -> None:
    for node_id in NODE_ID.findall(text):
        if node_id not in APPROVED_NODE_IDS:
            errors.append(f"{relative_path}: unapproved node ID '{node_id}'")
    for color in HEX_COLOR.findall(text):
        if color.upper() not in APPROVED_HEX_COLORS:
            errors.append(f"{relative_path}: unconfirmed hex color '{color}'")
    for value in PIXEL_VALUE.findall(text):
        if value not in APPROVED_PIXEL_VALUES:
            errors.append(f"{relative_path}: unapproved pixel value '{value}'")
    for token in VARIABLE_TOKEN.findall(text):
        if token not in APPROVED_VARIABLE_TOKENS:
            errors.append(f"{relative_path}: unconfirmed variable token '{token}'")
    for line in text.splitlines():
        if line.startswith("- 菜单条目"):
            errors.append(f"{relative_path}: non-allowlisted scaffold bullet '{line}'")


def validate(skill_root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for relative_path in REQUIRED_FILES:
        path = skill_root / relative_path
        if not path.is_file():
            errors.append(f"missing required file: {relative_path}")
            continue
        texts[relative_path] = read_text(path, errors)

    skill_text = texts.get("SKILL.md", "")
    if skill_text:
        validate_frontmatter(skill_text, errors)
        for required in (
            "platform=jinyumeng",
            "readiness=draft",
            "除受限验收试生成外，生成或修改 Figma 页面请求必须停止",
            "DEFERRED 反馈状态",
            "CONFIRMED 完整组件映射",
            "PENDING 完整验收",
            "acceptance_trial",
            "测试qifu-jinyumeng-list-page skill",
            "`5037:8717`",
            "不得回退到 `qifu-yushu-list-page`、`qifu-list-page`",
            "禁止手绘占位",
        ):
            if required not in skill_text:
                errors.append(f"SKILL.md: missing fail-closed contract '{required}'")

    version = texts.get("VERSION", "").strip()
    if version and not SEMVER.fullmatch(version):
        errors.append("VERSION: expected semantic version")
    if version != "0.7.2":
        errors.append("VERSION: expected 0.7.2")

    metadata = texts.get("agents/openai.yaml", "")
    for required in ('display_name: "Qifu Jinyumeng List Page"', "$qifu-jinyumeng-list-page", "@figma"):
        if required not in metadata:
            errors.append(f"agents/openai.yaml: missing required identity '{required}'")
    validate_implicit_invocation_policy(metadata, errors)

    for relative_path, requirements in REFERENCE_REQUIREMENTS.items():
        text = texts.get(relative_path, "")
        for required in requirements:
            if required not in text:
                errors.append(f"{relative_path}: missing draft contract '{required}'")
        validate_reference(relative_path, text, errors)

    protected_paths = ("SKILL.md", "agents/openai.yaml", *REFERENCE_REQUIREMENTS, "scripts/validate_skill_contract.py")
    for relative_path in protected_paths:
        text = texts.get(relative_path, "")
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(f"{relative_path}: forbidden cross-platform reference '{forbidden}'")

    for markdown_file in skill_root.rglob("*.md"):
        validate_links(skill_root, markdown_file, read_text(markdown_file, errors), errors)
    return errors


def main(argv: list[str]) -> int:
    skill_root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parents[1]
    if not skill_root.is_dir():
        print(f"FAIL\n- skill root does not exist: {skill_root}")
        return 2
    errors = validate(skill_root)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS qifu-jinyumeng-list-page 0.7.2 (draft+acceptance_trial)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
