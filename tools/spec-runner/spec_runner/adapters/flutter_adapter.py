"""flutter test 适配器。

关键坑（方案）：Flutter 机器可读输出里有隐藏用例——框架为每个测试文件生成一条加载用例并
标记为隐藏。这里从默认输出的 "+N:" 进度行解析可见测试数（已排除框架隐藏用例的计数），
为 0 时判 fail。
"""
from __future__ import annotations

import re

from spec_runner.adapters.base import ExecResult, combined
from spec_runner.verdict import Verdict


def _parse_visible(stdout: str) -> int:
    nums = [int(m) for m in re.findall(r"\+(\d+):", stdout)]
    return max(nums) if nums else 0


def classify(result: ExecResult) -> tuple[Verdict, str]:
    out = combined(result)
    if result.exit_code == 127 or "command not found" in out.lower() or "not recognized" in out.lower():
        return Verdict.UNCERTAIN, "flutter 命令不存在，工具链缺失（不等于被证伪）"
    visible = result.collected if result.collected is not None else _parse_visible(out)
    if visible == 0:
        return Verdict.FAIL, "flutter 事件流中可见测试数为 0（已排除隐藏用例）"
    if result.exit_code != 0:
        return Verdict.FAIL, "flutter 有测试结果非成功"
    return Verdict.PASS, f"flutter 通过，可见 {visible} 个测试"


PACKAGE = "dart"
