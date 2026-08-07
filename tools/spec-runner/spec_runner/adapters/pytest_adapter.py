"""pytest 适配器：退出码到五态。

关键坑（方案反复强调）：pytest 对不存在的测试名返回 4，和真正的用法错误共用同一个退出码；
缺失的测试文件也是 4。只看退出码会把"测试被删了"这个契约缺陷伪装成"环境有问题"，
必须再看输出里有没有未找到标记。
"""
from __future__ import annotations

import re

from spec_runner.adapters.base import ExecResult
from spec_runner.verdict import Verdict

_NOT_FOUND_MARKERS = ("not found", "no tests ran")
_COLLECTED_RE = re.compile(r"collected\s+(\d+)\s+items?", re.I)
# -q 模式下 pytest 不输出 collected 行，改从汇总行兜底：N passed/failed/error/skipped/...
_SUMMARY_RE = re.compile(r"(\d+)\s+(passed|failed|error|skipped|deselected|xfailed|xpassed)", re.I)


def _parse_collected(stdout: str) -> int:
    m = _COLLECTED_RE.search(stdout)
    if m:
        return int(m.group(1))
    return sum(int(n) for n, _ in _SUMMARY_RE.findall(stdout))


def classify(result: ExecResult) -> tuple[Verdict, str]:
    code = result.exit_code
    collected = result.collected if result.collected is not None else _parse_collected(result.stdout)
    if code == 0:
        if collected > 0:
            return Verdict.PASS, f"pytest 退出 0，收集 {collected} 个测试"
        return Verdict.FAIL, "pytest 退出 0 但收集数为 0，选择器命中零个测试（契约缺陷）"
    if code == 1:
        if "no module named pytest" in (result.stdout + "\n" + result.stderr).lower():
            return Verdict.UNCERTAIN, "pytest 未安装（No module named pytest），工具链缺失"
        return Verdict.FAIL, "pytest 退出 1，有测试失败"
    if code == 5:
        return Verdict.FAIL, "pytest 退出 5，未收集到测试"
    if code == 4:
        out = (result.stdout + "\n" + result.stderr).lower()
        if any(m in out for m in _NOT_FOUND_MARKERS):
            return Verdict.FAIL, "pytest 退出 4 且输出含未找到标记，悬空选择器"
        return Verdict.UNCERTAIN, "pytest 退出 4，用法错误或工具链问题"
    if code in (2, 3):
        return Verdict.UNCERTAIN, f"pytest 退出 {code}，中断或内部错误"
    return Verdict.UNCERTAIN, f"pytest 退出 {code}，未知退出码"


PACKAGE = "py"
