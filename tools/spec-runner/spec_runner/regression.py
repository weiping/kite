"""回归有效性验证（L2 反自洽链层3）。

规则：修复前测试必须红、修复后必须绿、还原必须再红。
before(还原)=FAIL + after(修复)=PASS 才算有效——before=PASS 说明测试没测这个 bug
（自洽但不正确）。零模型调用，两次机械执行。
"""
from __future__ import annotations

from spec_runner.runner import ScenarioResult
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
