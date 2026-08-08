"""风险分级：汇总变更 input → opa 评估 policy/risk.rego → {level, deny}。

L1.5 风险分级接线。input 复用 affected（changed_files/lines）；
dangling_selectors/boundary_violations 阶段1占位（见 affected.py 注释），阶段2实填。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from spec_runner.affected import collect_affected

POLICY_DIR = Path(__file__).resolve().parents[3] / "policy"


def collect_risk_input() -> dict:
    """汇总 risk.rego 的 input（复用 affected.collect_affected）。"""
    return collect_affected()


def evaluate_risk(input_data: dict, policy: Path | None = None) -> dict:
    """opa 评估 risk.rego → {level, deny}。opa 缺失抛 FileNotFoundError。"""
    opa = shutil.which("opa")
    if opa is None:
        raise FileNotFoundError(
            "opa 未安装：brew install opa（CI 用 open-policy-agent/setup-opa action）")
    policy = policy or (POLICY_DIR / "risk.rego")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(input_data, f)
        input_file = f.name
    try:
        proc = subprocess.run(
            [opa, "eval", "--format=json", "--data", str(policy),
             "--input", input_file, "data.kite.risk"],
            capture_output=True, text=True)
    finally:
        Path(input_file).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise RuntimeError(f"opa eval 失败（退出 {proc.returncode}）: {proc.stderr}")
    val = json.loads(proc.stdout)["result"][0]["expressions"][0]["value"]
    return {"level": val.get("level"), "deny": list(val.get("deny", []))}
