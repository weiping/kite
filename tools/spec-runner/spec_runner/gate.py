"""五态门禁。

判定处置规则（方案「五态怎么处置」）：
- fail、skip、pendingreview：永远阻断。跳过不等于通过，这一条不设开关。
- uncertain：L1/L1.5 升级人审；L2/L3 无人兜底，同样阻断。
- pass：放行。
"""
from __future__ import annotations

from spec_runner.verdict import Verdict

DENY_ALWAYS = {Verdict.SKIP, Verdict.PENDING_REVIEW}


def gate(results, level: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for r in results:
        v = r["verdict"]
        scenario = r["scenario"]
        reason = r.get("reason", "")
        if v == Verdict.FAIL:
            problems.append(f"[fail] {scenario}: {reason}")
        elif v in DENY_ALWAYS:
            problems.append(f"[{v}] {scenario}: 跳过不等于通过")
        elif v == Verdict.UNCERTAIN:
            if level in ("L2", "L3"):
                problems.append(f"[uncertain] {scenario}: 无人兜底，升级人审")
            else:
                problems.append(f"[uncertain→人审] {scenario}: {reason}")
    return (not problems), problems
