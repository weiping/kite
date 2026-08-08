"""charter-lint：L3 需求候选的宪章一致性论证检查。

index.md L3：Agent 发起的需求候选必须逐条论证与使命宪章的一致性。
本工具做弱检查（确定性）：扫 requirements 的 Source Trace 是否引用 charter。
语义级一致性论证由 Agent 在生成需求时做，本工具检查"引用存在"。
"""
from __future__ import annotations

from pathlib import Path


def charter_lint(requirements_dir, charter_keyword: str = "charter") -> dict:
    """检查 requirements 的 Source Trace 引用 charter（L3 一致性论证来源）。"""
    issues: list[str] = []
    checked = 0
    with_charter = 0
    for req in sorted(Path(requirements_dir).glob("*.md")):
        text = req.read_text(encoding="utf-8")
        checked += 1
        if "## Source Trace" not in text:
            issues.append(f"{req.name}: 缺 Source Trace（无来源标注）")
            continue
        if charter_keyword in text.lower():
            with_charter += 1
        else:
            issues.append(f"{req.name}: Source Trace 未引用 charter（L3 一致性论证缺）")
    return {
        "checked": checked,
        "with_charter": with_charter,
        "coverage": with_charter / checked if checked else 0,
        "issues": issues,
    }
