"""风险分级：汇总变更 input → opa 评估 policy/risk.rego → {level, deny}。

L1.5 风险分级接线。input 复用 affected（changed_files/lines）；
dangling_selectors/boundary_violations 阶段1占位（见 affected.py 注释），阶段2实填。
"""
from __future__ import annotations

from spec_runner.affected import collect_affected


def collect_risk_input() -> dict:
    """汇总 risk.rego 的 input（复用 affected.collect_affected）。"""
    return collect_affected()
