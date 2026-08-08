"""monthly-audit：L3 月度累积效应审计骨架。

L3 反馈周期月级（index.md），必须配月级检测。汇总 shadow 趋势 + 变更计数。
逃逸缺陷追踪待 L2 达标后补（当前 None）。
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from spec_runner.shadow import shadow_report


def monthly_audit(shadow_jsonl, since: str = "1 month ago") -> dict:
    """月度累积效应审计：shadow 趋势 + 变更计数。"""
    return {
        "period": since,
        "commits": len(_git_log_since(since)),
        "shadow": shadow_report(shadow_jsonl),
        "escape_defects": None,  # 待 L2 达标后追踪
    }


def _git_log_since(since: str) -> list[str]:
    try:
        r = subprocess.run(["git", "log", "--oneline", f"--since={since}"],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return []
    return [line for line in r.stdout.splitlines() if line.strip()]
