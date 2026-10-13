#!/usr/bin/env python3
"""Validate the qifu-yushu-list-page package's executable safety contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = (
    "SKILL.md",
    "VERSION",
    "references/page-rules.md",
    "references/component-map.md",
    "references/component-invocation-contract.md",
    "references/structural-validation.md",
    "references/platform-yushu.md",
)

REQUIRED_SEMANTICS = {
    "SKILL.md": (
        "## 失败关闭",
        "PROPERTY_READBACK_MISMATCH",
        "structural-validation.md",
        "component-invocation-contract.md",
        "Navigation Text Overlay",
        "tableSelection=true|false",
        "业务提示词首句必须显式调用 `@figma` 插件",
        "P0 菜单状态",
        "P0 表格 Tag",
        "P0 表头选择列",
        "本 Skill 固定用于毓数平台",
        "platform=yushu",
    ),
    "references/component-invocation-contract.md": (
        "componentProperties",
        "expectedType=TEXT|BOOLEAN|VARIANT|INSTANCE_SWAP|SLOT",
        "候选必须恰好为一个",
        "PROPERTY_NOT_FOUND",
        "SLOT_WRITE_FAILED",
        "只有 `COMPONENT_MISSING` 可以进入 Fallback 判断",
    ),
    "references/page-rules.md": (
        "primaryAction.placement=listActions.left|listActions.right",
        "最多 8 个业务列",
        "列表操作栏不会自动开启选择列",
        "列表操作栏只描述 Table Shell 上方 12px 的按钮",
        "sidePath 只控制左侧菜单",
    ),
    "references/component-map.md": (
        "表头 Selection Cell-V2 的根节点 `fills` 必须绑定 `背景色/--qifu-bg-color-canvas`",
        "所有列表状态标签：",
        "size=medium",
        "shape=square",
    ),
    "references/platform-yushu.md": (
        "navigationMode=yushuPreset|custom",
        "Icon/<system>/<purpose>",
        "只有当前路径祖先可以进入 `sideExpanded`",
        "所有祖先都使用 `State=Selected`",
        "各级菜单状态视觉矩阵（P0）",
        "图标仍为黑色或其他中性色时本项判 `FAIL`",
    ),
    "references/structural-validation.md": (
        "ComponentResolutionManifest",
        "visible Table Shell-V2 = 1",
        "Filter Item-V2 实例数等于 `filters[]` 数量",
        "Navigation Text Overlay",
        "structuralValidation PASS|BLOCKED|FAIL",
        "## 2. P0 重点检查项",
        "全量 Tag 样式",
        "Header Selection Cell 根节点",
    ),
}

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


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
    if not re.search(r"^name:\s*qifu-yushu-list-page\s*$", frontmatter, re.MULTILINE):
        errors.append("SKILL.md: name must be qifu-yushu-list-page")
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not description or not description.group(1).startswith("Use when"):
        errors.append("SKILL.md: description must start with 'Use when'")


def validate_links(skill_root: Path, markdown_file: Path, text: str, errors: list[str]) -> None:
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.split("#", 1)[0]
        if "://" in target:
            continue
        resolved = (markdown_file.parent / target).resolve()
        if not resolved.exists():
            errors.append(
                f"{markdown_file.relative_to(skill_root)}: broken markdown link {raw_target}"
            )


def validate(skill_root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for relative_path in REQUIRED_FILES:
        path = skill_root / relative_path
        if not path.is_file():
            errors.append(f"missing required reference: {relative_path}")
            continue
        texts[relative_path] = read_text(path, errors)

    skill_text = texts.get("SKILL.md", "")
    if skill_text:
        validate_frontmatter(skill_text, errors)
        for forbidden_platform_reference in (
            "platform-jinyumeng.md",
            "platform-dianxiao.md",
        ):
            if forbidden_platform_reference in skill_text:
                errors.append(
                    f"SKILL.md: forbidden cross-platform route {forbidden_platform_reference}"
                )

    version = texts.get("VERSION", "").strip()
    if version and not SEMVER.fullmatch(version):
        errors.append("VERSION: expected semantic version such as 1.1.0")

    for relative_path, required_phrases in REQUIRED_SEMANTICS.items():
        text = texts.get(relative_path, "")
        if not text:
            continue
        for phrase in required_phrases:
            if phrase not in text:
                errors.append(f"{relative_path}: missing required contract '{phrase}'")

    for markdown_file in skill_root.rglob("*.md"):
        text = read_text(markdown_file, errors)
        validate_links(skill_root, markdown_file, text, errors)

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

    version = (skill_root / "VERSION").read_text(encoding="utf-8").strip()
    print(f"PASS qifu-yushu-list-page {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
