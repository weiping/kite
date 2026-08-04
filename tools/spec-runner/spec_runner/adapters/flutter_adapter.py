"""flutter test 适配器。

关键坑（方案）：Flutter 机器可读输出里有隐藏用例——框架为每个测试文件生成一条加载用例并
标记为隐藏。调用方传入的 collected 必须是排除隐藏用例后的可见测试数；为 0 时判 fail。
"""
from __future__ import annotations

from spec_runner.adapters.base import ExecResult
from spec_runner.verdict import Verdict


def classify(result: ExecResult) -> tuple[Verdict, str]:
    out = (result.stdout + "\n" + result.stderr).lower()
    if result.exit_code == 127 or "command not found" in out or "not recognized" in out:
        return Verdict.UNCERTAIN, "flutter 命令不存在，工具链缺失（不等于被证伪）"
    visible = result.collected if result.collected is not None else 0
    if visible == 0:
        return Verdict.FAIL, "flutter 事件流中可见测试数为 0（已排除隐藏用例）"
    if result.exit_code != 0:
        return Verdict.FAIL, "flutter 有测试结果非成功"
    return Verdict.PASS, f"flutter 通过，可见 {visible} 个测试"


PACKAGE = "dart"
