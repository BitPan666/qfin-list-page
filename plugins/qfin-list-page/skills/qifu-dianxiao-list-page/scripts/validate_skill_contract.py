#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = (
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/platform-dianxiao.md",
    "references/page-rules.md",
    "references/component-map.md",
    "references/component-invocation-contract.md",
    "references/structural-validation.md",
    "scripts/validate_skill_contract.py",
)
REFERENCE_REQUIREMENTS = {
    "references/platform-dianxiao.md": (
        "platform=dianxiao",
        "全部菜单",
        "收藏菜单",
        "#009E73",
        "#262626",
        "#EBEBEB",
        "200px",
        "16px × 16px",
        "客户销售平台 - 借条",
        "个人信息",
        "消息中心",
    ),
    "references/page-rules.md": (
        "1366px",
        "1366px × 768px",
        "8px",
        "200px",
        "28px",
        "12px",
        "WRAP",
        "Data Display / Table / Shell-V2",
        "5–8",
        "背景色/--qifu-bg-color-canvas",
        "上一页箭头向左",
        "下一页箭头向右",
        "禁止生成独立操作栏",
        "1078px",
        "标题默认不显示",
        "主按钮 → 次按钮",
        "距白色承载面顶部 `20px`",
        "距最后一行数据底部 `12px`",
    ),
    "references/component-map.md": (
        "Navigation / Dianxiao SideMenu / MenuRoot",
        "`5762:1537`",
        "Navigation / Dianxiao SideMenu / SideMenuItem",
        "`5763:1753`",
        "Navigation / HeaderMenu / Dianxiao Header",
        "`5824:4491`",
        "Data Display / Table / Shell-V2",
        "P0 组件 blockers",
        "顶部 Header",
        "12px",
        "只包含三个原生 Slot",
        "不存在 `actionSlot`",
        "1078px",
    ),
    "references/component-invocation-contract.md": (
        "componentProperties",
        "Instance swap",
        "WRAP",
        "columns.length",
        "requiredTableHeight",
        "背景色/--qifu-bg-color-canvas",
        "BLOCKED",
        "只允许通过 `tabsSlot`、`filterSlot`、`tableSlot` 三个原生 Slot",
        "电销/Light",
        "Icon 必须解析为电销主题色",
        "Dianxiao Menu Scroll Viewport",
    ),
    "references/structural-validation.md": (
        "platform=dianxiao",
        "全部菜单",
        "收藏菜单",
        "200px",
        "28px",
        "12px",
        "columns.length",
        "data.length + 1",
        "20px",
        "Navigation / HeaderMenu / Dianxiao Header",
        "5824:4491",
        "readiness=ready",
            "只有结构和视觉均为 PASS",
            "组件调用或验收失败返回 FAIL",
        "不存在独立操作栏",
        "标题默认隐藏",
        "1078px",
        "电销/Light",
        "1366px × 768px",
        "主按钮 → 次按钮",
        "距最后一行数据底部 `12px`",
    ),
}
APPROVED_NODE_IDS = {
    "2381:2318",
    "2859:2820",
    "2967:29996",
    "2967:30327",
    "3178:9659",
    "3350:5949",
    "3368:6025",
    "3376:33871",
    "3393:6352",
    "3406:853",
    "3433:8257",
    "3678:8875",
    "3698:482",
    "5756:11",
    "5756:16",
    "5756:21",
    "5756:36",
    "5756:41",
    "5756:46",
    "5756:51",
    "5756:61",
    "5759:19212",
    "5762:1537",
    "5763:1753",
    "5810:20",
    "5810:30",
    "5810:40",
    "5810:50",
    "5810:60",
    "5810:74",
    "5810:84",
    "5749:18758",
    "5824:4491",
    "5829:15",
    "5829:24",
    "5829:31",
    "5838:9056",
}
APPROVED_COLORS = {"#009E73", "#262626", "#EBEBEB"}
APPROVED_PIXELS = {
    "1px",
    "8px",
    "12px",
    "16px",
    "20px",
    "24px",
    "28px",
    "32px",
    "38px",
    "40px",
    "52px",
    "56px",
    "104px",
    "60px",
    "80px",
    "502px",
    "668px",
    "712px",
    "768px",
    "758px",
    "188px",
    "200px",
    "694px",
    "924px",
    "968px",
    "1024px",
    "1118px",
    "1078px",
    "1248px",
    "130px",
    "1366px",
}
APPROVED_TOKENS = {
    "--qifu-bg-color-canvas",
    "--qifu-bg-color-surface",
    "--qifu-radius-8",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)")
NODE_ID = re.compile(r"\b\d+:\d+\b")
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\b")
PIXEL_VALUE = re.compile(r"\b\d+(?:\.\d+)?px\b")
VARIABLE_TOKEN = re.compile(r"--[A-Za-z][A-Za-z0-9-]*")


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {path}: {exc}")
        return ""


def validate_frontmatter(text: str, errors: list[str]) -> None:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        errors.append("SKILL.md: missing YAML frontmatter")
        return
    lines = [line for line in match.group(1).splitlines() if line.strip()]
    keys = [line.split(":", 1)[0].strip() for line in lines if ":" in line]
    if keys != ["name", "description"]:
        errors.append("SKILL.md: frontmatter must contain only name and description")
    if "name: qifu-dianxiao-list-page" not in lines:
        errors.append("SKILL.md: name must be qifu-dianxiao-list-page")
    description = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("description:")), "")
    if not description.startswith("Use when"):
        errors.append("SKILL.md: description must start with 'Use when'")


def validate_metadata(text: str, errors: list[str]) -> None:
    for required in (
        'display_name: "Qifu Dianxiao List Page"',
        "$qifu-dianxiao-list-page",
        "@figma",
        "allow_implicit_invocation: false",
    ):
        if required not in text:
            errors.append(f"agents/openai.yaml: missing '{required}'")


def validate_reference(relative: str, text: str, errors: list[str]) -> None:
    for node_id in NODE_ID.findall(text):
        if node_id not in APPROVED_NODE_IDS:
            errors.append(f"{relative}: unapproved node ID '{node_id}'")
    for color in HEX_COLOR.findall(text):
        if color.upper() not in APPROVED_COLORS:
            errors.append(f"{relative}: unconfirmed hex color '{color}'")
    for value in PIXEL_VALUE.findall(text):
        if value not in APPROVED_PIXELS:
            errors.append(f"{relative}: unapproved pixel value '{value}'")
    for token in VARIABLE_TOKEN.findall(text):
        if token not in APPROVED_TOKENS:
            errors.append(f"{relative}: unconfirmed variable token '{token}'")


def validate(skill_root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for relative in REQUIRED_FILES:
        path = skill_root / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        else:
            texts[relative] = read_text(path, errors)

    skill = texts.get("SKILL.md", "")
    if skill:
        validate_frontmatter(skill, errors)
        for required in (
            "platform=dianxiao",
            "readiness=ready",
            "目标 Page 由用户指定",
            "禁止手绘",
            "references/platform-dianxiao.md",
            "references/page-rules.md",
            "references/component-map.md",
            "references/component-invocation-contract.md",
            "references/structural-validation.md",
        ):
            if required not in skill:
                errors.append(f"SKILL.md: missing contract '{required}'")
        for forbidden in ("platform=yushu", "platform=jinyumeng"):
            if forbidden in skill:
                errors.append(f"SKILL.md: forbidden cross-platform identity '{forbidden}'")

    version = texts.get("VERSION", "").strip()
    if version != "1.0.0":
        errors.append("VERSION: expected 1.0.0")
    validate_metadata(texts.get("agents/openai.yaml", ""), errors)

    for relative, requirements in REFERENCE_REQUIREMENTS.items():
        text = texts.get(relative, "")
        for required in requirements:
            if required not in text:
                errors.append(f"{relative}: missing contract '{required}'")
        validate_reference(relative, text, errors)

    for markdown_file in skill_root.rglob("*.md"):
        text = read_text(markdown_file, errors)
        for raw_target in MARKDOWN_LINK.findall(text):
            if not (markdown_file.parent / raw_target).resolve().is_file():
                errors.append(f"{markdown_file.relative_to(skill_root)}: broken markdown link {raw_target}")
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
    print("PASS qifu-dianxiao-list-page 1.0.0 (ready)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
