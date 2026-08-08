"""回归有效性验证（L2 反自洽链层3）。

规则：修复前测试必须红、修复后必须绿、还原必须再红。
before(还原)=FAIL + after(修复)=PASS 才算有效——before=PASS 说明测试没测这个 bug
（自洽但不正确）。零模型调用，两次机械执行。
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from spec_runner.contract import parse_contract_file
from spec_runner.runner import ScenarioResult, default_execute, run_contract
from spec_runner.verdict import Verdict


def _regression_report(before: list[ScenarioResult], after: list[ScenarioResult]) -> dict:
    """比对还原态（before）与修复态（after），判定回归有效性。"""
    results = []
    valid = True
    for b, a in zip(before, after):
        ok = b.verdict is Verdict.FAIL and a.verdict is Verdict.PASS
        valid = valid and ok
        results.append({
            "scenario": b.scenario,
            "before": b.verdict.value,   # 还原态（期望 fail）
            "after": a.verdict.value,    # 修复态（期望 pass）
            "valid": ok,
        })
    return {"valid": valid, "results": results}


def regression_check(spec_path: str | Path, execute=default_execute) -> dict:
    """回归有效性验证：假设工作区含修复，stash 还原 → 跑（期望红）→ pop 恢复 → 跑（期望绿）。"""
    contract = parse_contract_file(spec_path)
    _git(["stash"])                        # 还原修复
    before = run_contract(contract, execute)
    _git(["stash", "pop"])                 # 恢复修复
    after = run_contract(contract, execute)
    return _regression_report(before, after)


def _git(args: list[str]) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return r.stdout if r.returncode == 0 else ""
