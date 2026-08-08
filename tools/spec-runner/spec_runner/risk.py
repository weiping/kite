"""风险分级：汇总变更 input → opa 评估 policy/risk.rego → {level, deny}。

L1.5 风险分级接线。input 复用 affected（changed_files/lines）；
dangling_selectors/boundary_violations 阶段1占位（见 affected.py 注释），阶段2实填。
"""
from __future__ import annotations

import shutil
from pathlib import Path

from spec_runner.affected import collect_affected

POLICY_DIR = Path(__file__).resolve().parents[3] / "policy"


def collect_risk_input() -> dict:
    """汇总 risk.rego 的 input（复用 affected.collect_affected）。"""
    return collect_affected()


def evaluate_risk(input_data: dict, policy: Path | None = None) -> dict:
    """opa 评估 risk.rego → {level, deny}。opa 缺失抛 FileNotFoundError。"""
    if shutil.which("opa") is None:
        raise FileNotFoundError(
            "opa 未安装：brew install opa（CI 用 open-policy-agent/setup-opa action）")
    raise NotImplementedError("opa eval 待 Task 3 实现")
