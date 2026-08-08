"""需求 provenance 检查（L2 需求接受机制）。

index.md：L2 下人介入需求的**接受**（判断哪几条是 Agent 猜的）。requirement 的
Source Trace 段标 `stated`（人说）/ `inferred(高/中/低)`（Agent 猜 + 置信度）。
低/中置信 inferred 升人审——守护意图最实际的手段是让机器主动标「我这里是在猜」。
"""
from __future__ import annotations

import re
from pathlib import Path


def provenance_lint(requirements_dir) -> dict:
    """检查 requirement provenance（Source Trace + stated），收集低/中置信 inferred。"""
    issues: list[str] = []
    low_confidence: list[str] = []
    for req in sorted(Path(requirements_dir).glob("*.md")):
        text = req.read_text(encoding="utf-8")
        if "## Source Trace" not in text:
            issues.append(f"{req.name}: 缺 Source Trace 段（无来源标注）")
            continue
        if not re.search(r"^-\s+stated:", text, re.M):
            issues.append(f"{req.name}: Source Trace 缺 stated（人说的来源）")
        # 低/中置信 inferred 收集（升人审）
        for m in re.finditer(r"^-\s+inferred\((低|中)\).*", text, re.M):
            low_confidence.append(f"{req.name}: {m.group(0).lstrip('- ').strip()}")
    return {"issues": issues, "low_confidence": low_confidence, "valid": len(issues) == 0}
