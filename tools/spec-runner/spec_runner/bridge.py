"""bridge：把 spec-runner 的执行结果注入 agent-spec，消除 verify 的 skip。

agent-spec 的 verify 对 Python/Dart 判 skip（"no verifier covered"），因为它的内置
verifier 不跑 pytest/flutter。bridge 在这里补位：用 spec-runner 跑契约绑定的测试，
把结果伪装成 agent-spec 的 AI decisions（model=spec-runner），经 resolve-ai 注入，
得到一份真正反映代码行为的 verification report。

这是方案「执行器外接」的工程闭环：agent-spec 管契约/追溯，spec-runner 管执行。
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from spec_runner.contract import parse_contract_file
from spec_runner.runner import default_execute, run_contract
from spec_runner.verdict import Verdict


def make_decisions(results) -> list[dict]:
    """把 spec-runner 的 ScenarioResult 列表转成 agent-spec resolve-ai 的 decisions 数组。"""
    return [
        {
            "scenario_name": r.scenario,
            "verdict": r.verdict.value,
            "reasoning": r.reason,
            "model": "spec-runner",
            "confidence": 1.0 if r.verdict is Verdict.PASS else 0.0,
        }
        for r in results
    ]


def bridge(spec_path: str | Path, code: str = ".") -> int:
    contract = parse_contract_file(spec_path)
    decisions = make_decisions(run_contract(contract, default_execute))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(decisions, f, ensure_ascii=False)
        dec_path = f.name
    try:
        proc = subprocess.run(
            ["agent-spec", "resolve-ai", "--decisions", dec_path, str(spec_path),
             "--code", code, "--format", "json"],
            capture_output=True, text=True,
        )
    finally:
        Path(dec_path).unlink(missing_ok=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode
