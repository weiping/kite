"""semgrep 适配器：让不变量也能被契约绑定（REQ-INV-* 与功能需求共用三态追溯）。"""
from __future__ import annotations

from spec_runner.adapters.base import ExecResult
from spec_runner.verdict import Verdict


def classify(result: ExecResult) -> tuple[Verdict, str]:
    code = result.exit_code
    if code == 0:
        return Verdict.PASS, "semgrep 无发现"
    if code == 1:
        return Verdict.FAIL, "semgrep 有发现，违反不变量"
    if code == 2:
        return Verdict.UNCERTAIN, "semgrep 退出 2，规则文件错误"
    return Verdict.UNCERTAIN, f"semgrep 退出 {code}，未知退出码"


PACKAGE = "semgrep"
