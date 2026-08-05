"""runner：对契约的每个 scenario 调对应执行器，把机械结果映射回五态，汇总成 evidence。

执行器（execute）是注入的，默认实现 default_execute 用 subprocess 调真实工具链，
这样测试可注入假执行器不依赖环境，而真实运行仍走 subprocess。
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from spec_runner.adapters import ADAPTERS
from spec_runner.adapters.base import ExecResult
from spec_runner.contract import Contract, TestSelector
from spec_runner.verdict import Verdict

Execute = Callable[[TestSelector], ExecResult]


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    package: str
    filter: str
    verdict: Verdict
    reason: str

    def to_gate_row(self) -> dict:
        return {"scenario": self.scenario, "verdict": self.verdict, "reason": self.reason}


def run_contract(contract: Contract, execute: Execute) -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    for sc in contract.scenarios:
        adapter = ADAPTERS.get(sc.test.package)
        if adapter is None:
            results.append(ScenarioResult(sc.name, sc.test.package, sc.test.filter,
                                          Verdict.UNCERTAIN, f"未注册执行器: {sc.test.package}"))
            continue
        verdict, reason = adapter.classify(execute(sc.test))
        results.append(ScenarioResult(sc.name, sc.test.package, sc.test.filter, verdict, reason))
    return results


def to_evidence(contract: Contract, results: list[ScenarioResult]) -> dict:
    return {
        "contract": contract.name,
        "results": [
            {
                "scenario": r.scenario,
                "package": r.package,
                "filter": r.filter,
                "verdict": r.verdict.value,
                "reason": r.reason,
            }
            for r in results
        ],
    }


def default_execute(selector: TestSelector) -> ExecResult:
    pkg = selector.package
    filt = selector.filter
    cwd = None
    if pkg == "py":
        cmd = [sys.executable, "-m", "pytest", "-q", filt]
    elif pkg == "dart":
        # flutter test 需在项目根跑；filter 形如 [apps/mobile/]test/x.dart::test_name
        filt_rel = filt[len("apps/mobile/"):] if filt.startswith("apps/mobile/") else filt
        if "::" in filt_rel:
            path, test_name = filt_rel.split("::", 1)
            cmd = ["flutter", "test", path, "--plain-name", test_name]
        else:
            cmd = ["flutter", "test", filt_rel]
        cwd = "apps/mobile"
    elif pkg == "semgrep":
        cmd = ["semgrep", "--config", filt]
    else:
        return ExecResult(exit_code=99, stderr=f"未知执行器 Package: {pkg}")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    except FileNotFoundError:
        return ExecResult(exit_code=127, stderr=f"命令不存在: {cmd[0]}")
    return ExecResult(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
