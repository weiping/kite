"""runner：对契约的每个 scenario 调对应执行器，汇总成 evidence。"""
from spec_runner.adapters.base import ExecResult
from spec_runner.contract import parse_contract
from spec_runner.runner import ScenarioResult, run_contract, to_evidence
from spec_runner.verdict import Verdict

MULTI = """\
---
spec: task
name: "多执行器示例"
satisfies: []
---

## Completion Criteria

Scenario: py 用例
  Test:
    Package: py
    Filter: tests/a.py::test_a
    Level: unit
    Targets: services/a.py
  Given x
  When y
  Then z

Scenario: dart 用例
  Test:
    Package: dart
    Filter: tests/b_test.dart
    Level: unit
    Targets: apps/mobile/lib/b.dart
  Given x
  When y
  Then z

Scenario: semgrep 不变量
  Test:
    Package: semgrep
    Filter: rules/no-clock.yaml
    Level: static
    Targets: services/a.py
  Given x
  When y
  Then z
"""


def _fake_execute(selector):
    if selector.package == "py":
        return ExecResult(0, "collected 1 items", collected=1)
    if selector.package == "dart":
        return ExecResult(127, stderr="flutter: command not found")
    return ExecResult(0, "")  # semgrep 无发现


def test_run_contract_按package分发到各adapter():
    c = parse_contract(MULTI)
    results = run_contract(c, _fake_execute)
    assert [r.package for r in results] == ["py", "dart", "semgrep"]
    assert results[0].verdict is Verdict.PASS
    # dart 命令不存在 → uncertain（对应附录三：Dart 侧因环境无 SDK 判不确定）
    assert results[1].verdict is Verdict.UNCERTAIN
    assert results[2].verdict is Verdict.PASS


def test_run_contract_未注册package判uncertain():
    c = parse_contract(MULTI.replace("Package: py", "Package: rust"))
    results = run_contract(c, lambda s: ExecResult(0, ""))
    assert results[0].verdict is Verdict.UNCERTAIN


def test_to_evidence_序列化且verdict为小写无下划线():
    c = parse_contract(MULTI)
    results = run_contract(c, _fake_execute)
    evidence = to_evidence(c, results)
    assert evidence["contract"] == "多执行器示例"
    verdicts = [r["verdict"] for r in evidence["results"]]
    assert verdicts == ["pass", "uncertain", "pass"]
    assert evidence["results"][0]["filter"] == "tests/a.py::test_a"


def test_ScenarioResult_可转gate输入():
    r = ScenarioResult(scenario="s", package="py", filter="f", verdict=Verdict.FAIL, reason="x")
    assert r.to_gate_row() == {"scenario": "s", "verdict": Verdict.FAIL, "reason": "x"}
