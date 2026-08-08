"""CLI 子命令测试。run 用真实 pytest 跑临时测试，验证完整链路。"""
import json
from pathlib import Path

from spec_runner import cli
from spec_runner import affected as affected_mod


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


PASSING_SPEC = """\
---
spec: task
name: "端到端"
satisfies: []
---

## Boundaries

### Allowed Changes
- services/calc.py
- tests/test_calc.py

## Completion Criteria

Scenario: 加法正确
  Test:
    Package: py
    Filter: {filter}
    Level: unit
    Targets: services/calc.py
  Given 两个数
  When 相加
  Then 得到和
"""


def test_run_端到端_产出evidence且全pass(tmp_path: Path, monkeypatch):
    tests = _write(tmp_path / "tests" / "test_calc.py",
                   "def test_add():\n    assert 1 + 1 == 2\n")
    spec = _write(tmp_path / "specs" / "calc.spec.md", PASSING_SPEC.format(filter=str(tests)))
    out = tmp_path / ".out"
    monkeypatch.chdir(tmp_path)

    code = cli.main(["run", str(spec), "--out", str(out)])
    assert code == 0
    evidence = json.loads((out / "calc.evidence.json").read_text(encoding="utf-8"))
    assert evidence["results"][0]["verdict"] == "pass"


def test_gate_全pass_放行(tmp_path: Path):
    f = _write(tmp_path / "e.json", json.dumps({"results": [
        {"scenario": "a", "verdict": "pass", "reason": ""},
    ]}))
    assert cli.main(["gate", str(f), "--level", "L1"]) == 0


def test_gate_有fail_返回1(tmp_path: Path, capsys):
    f = _write(tmp_path / "e.json", json.dumps({"results": [
        {"scenario": "a", "verdict": "fail", "reason": "断言失败"},
    ]}))
    assert cli.main(["gate", str(f), "--level", "L1"]) == 1
    err = capsys.readouterr().err
    assert "[fail]" in err


def test_allowed_changes_only_impl(tmp_path: Path, capsys):
    spec = _write(tmp_path / "c.spec.md", """\
---
spec: task
name: t
satisfies: []
---

## Boundaries

### Allowed Changes
- services/a.py
- tests/test_a.py

## Completion Criteria
""")
    assert cli.main(["allowed-changes", str(spec), "--only-impl"]) == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out == ["services/a.py"]


def test_assert_no_violation_通过(tmp_path: Path):
    f = _write(tmp_path / "lc.json", json.dumps({"violations": []}))
    assert cli.main(["assert-no-boundary-violation", str(f)]) == 0


def test_assert_no_violation_退出1(tmp_path: Path):
    f = _write(tmp_path / "lc.json", json.dumps(
        {"violations": [{"path": "services/x.py", "reason": "not covered"}]}))
    assert cli.main(["assert-no-boundary-violation", str(f)]) == 1


def test_affected_从git_diff收集(monkeypatch):
    monkeypatch.setattr(affected_mod, "_git", lambda args: {
        ("diff", "--name-only", "HEAD"): "services/a.py\nconfig/sdui/page.json\n",
        ("diff", "--numstat", "HEAD"): "12   3   services/a.py\n0    0   config/sdui/page.json\n",
    }.get(tuple(args), ""))
    data = affected_mod.collect_affected()
    assert data["changed_files"] == ["services/a.py", "config/sdui/page.json"]
    assert data["changed_lines"] == 12
    assert data["boundary_violations"] == 0


def test_collect_risk_input_复用affected结构(monkeypatch):
    from spec_runner import risk
    monkeypatch.setattr(risk, "collect_affected", lambda: {
        "changed_files": ["services/a.py", "policy/risk.rego"],
        "changed_lines": 42,
        "dangling_selectors": [],
        "boundary_violations": 0,
    })
    data = risk.collect_risk_input()
    assert data["changed_files"] == ["services/a.py", "policy/risk.rego"]
    assert data["changed_lines"] == 42
    assert "dangling_selectors" in data and "boundary_violations" in data
