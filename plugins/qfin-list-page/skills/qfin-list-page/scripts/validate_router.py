#!/usr/bin/env python3
"""Validate the qfin-list-page router contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROUTES = {
    "yushu": "../qifu-yushu-list-page/SKILL.md",
    "jinyumeng": "../qifu-jinyumeng-list-page/SKILL.md",
    "dianxiao": "../qifu-dianxiao-list-page/SKILL.md",
    "zhikexing": "../qifu-zhikexing-list-page/SKILL.md",
    "zhineng-yunying": "../qifu-zhineng-yunying-list-page/SKILL.md",
}

ERROR_CODES = (
    "PLATFORM_REQUIRED",
    "PLATFORM_CONFLICT",
    "UNSUPPORTED_PLATFORM",
    "CHILD_SKILL_MISSING",
)

REQUIRED_CONTRACT_LINES = (
    "Load exactly one child Skill.",
    "Pass the unmodified raw request",
    "Stop applying parent generation rules after handoff.",
    "The child owns PageSpec, execution, and validation after handoff.",
    "Preserve child readiness and native status verbatim.",
    "selectedPlatform",
    "selectedSkill",
    "routingEvidence",
    "There is no default platform.",
)


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        return {}
    result: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def validate(skill_root: Path) -> list[str]:
    skill_root = Path(skill_root)
    errors: list[str] = []
    skill_path = skill_root / "SKILL.md"
    version_path = skill_root / "VERSION"
    prompt_path = skill_root / "references" / "prompt-template.md"
    metadata_path = skill_root / "agents" / "openai.yaml"

    if not skill_path.is_file():
        return ["missing SKILL.md"]
    text = skill_path.read_text(encoding="utf-8")

    metadata = _frontmatter(text)
    if metadata.get("name") != "qfin-list-page":
        errors.append("frontmatter name must be qfin-list-page")
    if not metadata.get("description"):
        errors.append("frontmatter description is required")

    if not version_path.is_file():
        errors.append("missing VERSION")
    else:
        version = version_path.read_text(encoding="utf-8").strip()
        if not re.fullmatch(
            r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version
        ):
            errors.append("VERSION must be strict semver")

    for platform, relative_path in ROUTES.items():
        route_path = (skill_root / relative_path).resolve()
        if not route_path.is_file():
            errors.append(f"CHILD_SKILL_MISSING: {platform} -> {relative_path}")
        if f"]({relative_path})" not in text:
            errors.append(f"route target mismatch for {platform}: {relative_path}")

    for code in ERROR_CODES:
        if code not in text:
            errors.append(f"missing routing error code: {code}")

    for required_line in REQUIRED_CONTRACT_LINES:
        if required_line not in text:
            if "readiness" in required_line:
                errors.append("missing readiness passthrough contract")
            elif "exactly one" in required_line:
                errors.append("missing exactly one child loading contract")
            else:
                errors.append(f"missing router contract: {required_line}")

    if re.search(r"DEFAULT_PLATFORM\s*[:=]", text, flags=re.IGNORECASE):
        errors.append("default platform configuration is forbidden")
    for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if link.startswith(("http://", "https://", "#")):
            continue
        if not (skill_root / link).resolve().exists():
            errors.append(f"unresolvable Markdown link: {link}")

    if not prompt_path.is_file():
        errors.append("missing prompt template")
    else:
        prompt = prompt_path.read_text(encoding="utf-8")
        non_empty_lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        if not non_empty_lines or non_empty_lines[0] != "@figma":
            errors.append("prompt template must start with @figma")
        if "$qfin-list-page" not in prompt:
            errors.append("prompt template must invoke $qfin-list-page")
        if "目标平台（必填，五选一）：毓数 / 金毓盟 / 电销 / 智客星 / 智能运营" not in prompt:
            errors.append("prompt template must require one supported platform")
        if "app://" in prompt:
            errors.append("prompt template must not hard-code a connector ID")

    if not metadata_path.is_file():
        errors.append("missing agents/openai.yaml")
    else:
        metadata = metadata_path.read_text(encoding="utf-8")
        if not re.search(
            r'(?m)^\s*display_name:\s*["\']?QFIN List Page["\']?\s*$', metadata
        ):
            errors.append("metadata display_name must be QFIN List Page")
        short_match = re.search(
            r'(?m)^\s*short_description:\s*["\'](.+)["\']\s*$', metadata
        )
        if not short_match or not 25 <= len(short_match.group(1)) <= 64:
            errors.append("metadata short_description must contain 25-64 characters")
        if "$qfin-list-page" not in metadata:
            errors.append("metadata default_prompt must invoke $qfin-list-page")
        implicit_match = re.search(
            r"(?m)^\s*allow_implicit_invocation:\s*(\w+)\s*$", metadata
        )
        if implicit_match and implicit_match.group(1).lower() != "true":
            errors.append("allow_implicit_invocation must be true when declared")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print("usage: validate_router.py [SKILL_ROOT]", file=sys.stderr)
        return 2
    skill_root = Path(argv[1]) if len(argv) == 2 else Path(__file__).resolve().parents[1]
    errors = validate(skill_root)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    version = (skill_root / "VERSION").read_text(encoding="utf-8").strip()
    print(f"PASS qfin-list-page {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
