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


def test_collect_risk_input_用vs_base改动(monkeypatch):
    from spec_runner import risk
    monkeypatch.setattr(risk, "_collect_changes_vs_base", lambda: {
        "changed_files": ["services/a.py", "policy/risk.rego"],
        "changed_lines": 42,
        "dangling_selectors": [],
        "boundary_violations": 0,
    })
    data = risk.collect_risk_input()
    assert data["changed_files"] == ["services/a.py", "policy/risk.rego"]
    assert data["changed_lines"] == 42


def test_collect_changes_vs_base_用git_diff_origin_main(monkeypatch):
    from spec_runner import risk
    monkeypatch.setattr(risk, "_detect_base_ref", lambda: "origin/main")

    def fake_git(args):
        if args == ["diff", "--name-only", "origin/main...HEAD"]:
            return "services/a.py\n"
        if args == ["diff", "--numstat", "origin/main...HEAD"]:
            return "10\t2\tservices/a.py\n"
        return ""
    monkeypatch.setattr(risk, "_git", fake_git)
    data = risk._collect_changes_vs_base()
    assert data["changed_files"] == ["services/a.py"]
    assert data["changed_lines"] == 10


def test_opa缺失_抛明确错误(monkeypatch):
    from spec_runner import risk
    monkeypatch.setattr(risk.shutil, "which", lambda _: None)
    try:
        risk.evaluate_risk({"changed_files": [], "changed_lines": 0})
    except FileNotFoundError as e:
        assert "opa" in str(e) and "install" in str(e).lower()
    else:
        raise AssertionError("应抛 FileNotFoundError")


def test_risk命令_输出level且deny空时退出0(monkeypatch, capsys):
    from spec_runner import risk
    monkeypatch.setattr(risk, "collect_risk_input", lambda: {
        "changed_files": ["docs/x.md"], "changed_lines": 2,
        "dangling_selectors": [], "boundary_violations": 0})
    monkeypatch.setattr(risk, "evaluate_risk", lambda data, policy=None: {
        "level": "R0", "deny": []})
    code = cli.main(["risk"])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["level"] == "R0" and out["deny"] == []


def test_risk命令_deny非空时退出1(monkeypatch, capsys):
    from spec_runner import risk
    monkeypatch.setattr(risk, "collect_risk_input", lambda: {
        "changed_files": ["docs/x.md"], "changed_lines": 1,
        "dangling_selectors": ["坏选择器"], "boundary_violations": 0})
    monkeypatch.setattr(risk, "evaluate_risk", lambda data, policy=None: {
        "level": "R0", "deny": ["测试选择器不存在: 坏选择器"]})
    code = cli.main(["risk"])
    assert code == 1


def test_risk命令_opa缺失时退出2(monkeypatch, capsys):
    from spec_runner import risk
    monkeypatch.setattr(risk, "collect_risk_input", lambda: {
        "changed_files": [], "changed_lines": 0,
        "dangling_selectors": [], "boundary_violations": 0})

    def _raise(data, policy=None):
        raise FileNotFoundError("opa 未安装")
    monkeypatch.setattr(risk, "evaluate_risk", _raise)
    code = cli.main(["risk"])
    assert code == 2
    assert "opa" in capsys.readouterr().err


def test_count_boundary_violations_白名单与allowed不算越界(tmp_path):
    from spec_runner import risk
    specdir = tmp_path / "specs"
    specdir.mkdir()
    (specdir / "t.spec.md").write_text(
        "---\nspec: task\nname: t\nsatisfies: []\n---\n\n"
        "## Boundaries\n\n### Allowed Changes\n- services/a.py\n\n"
        "## Completion Criteria\n", encoding="utf-8")
    # docs/x.md 白名单；services/a.py allowed；services/b.py 越界；README.md 白名单
    n = risk._count_boundary_violations(
        ["docs/x.md", "services/a.py", "services/b.py", "README.md"],
        specs_dir=specdir)
    assert n == 1


def test_collect_risk_input_填boundary_violations(monkeypatch, tmp_path):
    from spec_runner import risk
    monkeypatch.setattr(risk, "_collect_changes_vs_base", lambda: {
        "changed_files": ["services/b.py"], "changed_lines": 1,
        "dangling_selectors": [], "boundary_violations": 0})
    monkeypatch.setattr(risk, "_count_boundary_violations", lambda files, specs_dir=None: 1)
    data = risk.collect_risk_input()
    assert data["boundary_violations"] == 1


def test_risk命令追加影子记录(monkeypatch, tmp_path, capsys):
    from spec_runner import risk
    monkeypatch.setattr(risk, "collect_risk_input", lambda: {
        "changed_files": ["docs/x.md"], "changed_lines": 2,
        "dangling_selectors": [], "boundary_violations": 0})
    monkeypatch.setattr(risk, "evaluate_risk", lambda d, policy=None: {
        "level": "R0", "deny": []})
    monkeypatch.chdir(tmp_path)
    cli.main(["risk"])
    capsys.readouterr()  # 清 stdout
    shadow_file = tmp_path / ".out" / "shadow.jsonl"
    assert shadow_file.exists()
    rec = json.loads(shadow_file.read_text().strip().splitlines()[-1])
    assert rec["level"] == "R0" and rec["changed_files"] == ["docs/x.md"]
    assert "ts" in rec and "commit" in rec


def test_collect_ai_bom_返回CycloneDX格式():
    from spec_runner.audit_seal import collect_ai_bom
    bom = collect_ai_bom()
    assert bom["bomFormat"] == "CycloneDX"
    assert bom["specVersion"] == "1.5"
    names = [c["name"] for c in bom["components"]]
    assert "sherpa-onnx-whisper-small" in names  # 端侧转写模型
    assert "agent-spec" in names                  # 意图编译器
    assert "spec-runner" in names                 # 执行器
    assert "opa" in names                         # 策略评估
    for c in bom["components"]:
        assert c["type"] in ("application", "data", "library")
        assert "bom-ref" in c


def test_collect_audit_package_含制品引用与ai_bom():
    from spec_runner.audit_seal import collect_audit_package
    pkg = collect_audit_package(commit="abc1234567", risk_level="R0")
    assert pkg["commit"] == "abc1234567"
    assert pkg["risk_level"] == "R0"
    assert isinstance(pkg["timestamp"], int)
    arts = pkg["artifacts"]
    assert arts["evidence"] == ".out/evidence.json"
    assert arts["risk"] == ".out/risk.json"
    assert arts["shadow"] == ".out/shadow.jsonl"
    assert "design_lint" in arts and "evals" in arts and "mutation" in arts
    assert pkg["ai_bom"]["bomFormat"] == "CycloneDX"


def test_audit_seal命令_写出审计包(monkeypatch, tmp_path, capsys):
    from spec_runner import audit_seal
    monkeypatch.setattr(audit_seal, "collect_audit_package", lambda commit, risk_level: {
        "commit": commit, "risk_level": risk_level, "timestamp": 1,
        "artifacts": {}, "ai_bom": {"bomFormat": "CycloneDX"}})
    monkeypatch.setattr(audit_seal, "get_commit", lambda: "short12345")
    monkeypatch.chdir(tmp_path)
    code = cli.main(["audit-seal"])
    assert code == 0
    capsys.readouterr()
    pkg_file = tmp_path / ".out" / "audit" / "short12345.json"
    assert pkg_file.exists()
    pkg = json.loads(pkg_file.read_text())
    assert pkg["commit"] == "short12345"


def test_collect_dangling_selectors_检测不存在文件(tmp_path):
    from spec_runner import risk
    specdir = tmp_path / "specs"
    specdir.mkdir()
    (specdir / "t.spec.md").write_text(
        "---\nspec: task\nname: t\nsatisfies: []\n---\n\n"
        "## Completion Criteria\n\n"
        "Scenario: 有测试\n  Test:\n    Package: py\n    Filter: tests/exist.py::test_a\n    Level: unit\n"
        "  Given x\n  When y\n  Then z\n\n"
        "Scenario: 无测试\n  Test:\n    Package: py\n    Filter: tests/missing.py::test_b\n    Level: unit\n"
        "  Given x\n  When y\n  Then z\n", encoding="utf-8")
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests" / "exist.py").write_text("def test_a(): pass")
    dangling = risk._collect_dangling_selectors(specs_dir=specdir, root=tmp_path)
    assert len(dangling) == 1
    assert "missing.py" in dangling[0]


def test_collect_risk_input_填dangling(monkeypatch):
    from spec_runner import risk
    monkeypatch.setattr(risk, "_collect_changes_vs_base", lambda: {
        "changed_files": [], "changed_lines": 0,
        "dangling_selectors": [], "boundary_violations": 0})
    monkeypatch.setattr(risk, "_collect_dangling_selectors",
                        lambda specs_dir=None, root=None: ["t.spec.md:missing.py::test"])
    data = risk.collect_risk_input()
    assert data["dangling_selectors"] == ["t.spec.md:missing.py::test"]


def test_retention_按risk_level():
    import time
    from spec_runner.audit_seal import _retention
    now = int(time.time())
    assert _retention("R3") == {"policy": "permanent", "expire": None}
    assert _retention("R2") == {"policy": "permanent", "expire": None}
    r1 = _retention("R1")
    assert r1["policy"] == "2y" and r1["expire"] > now
    r0 = _retention("R0")
    assert r0["policy"] == "6m" and r0["expire"] > now


def test_collect_audit_package_含retention():
    from spec_runner.audit_seal import collect_audit_package
    pkg = collect_audit_package(commit="abc", risk_level="R3")
    assert pkg["retention"]["policy"] == "permanent"
    pkg0 = collect_audit_package(commit="abc", risk_level="R0")
    assert pkg0["retention"]["policy"] == "6m"


def test_audit_seal命令_archive入库(monkeypatch, tmp_path, capsys):
    from spec_runner import audit_seal
    monkeypatch.setattr(audit_seal, "collect_audit_package", lambda commit, risk_level: {
        "commit": commit, "risk_level": risk_level, "timestamp": 1,
        "artifacts": {}, "ai_bom": {"bomFormat": "CycloneDX"},
        "retention": {"policy": "6m"}})
    monkeypatch.setattr(audit_seal, "get_commit", lambda: "arch12345")
    monkeypatch.chdir(tmp_path)
    # 默认写 .out/audit/（CI artifact）
    assert cli.main(["audit-seal"]) == 0
    capsys.readouterr()
    assert (tmp_path / ".out" / "audit" / "arch12345.json").exists()
    # --archive 入库 audit-seal/（永久保留）
    assert cli.main(["audit-seal", "--archive"]) == 0
    capsys.readouterr()
    assert (tmp_path / "audit-seal" / "arch12345.json").exists()


def test_collect_ai_bom_sherpa版本从pubspec动态提():
    from spec_runner.audit_seal import collect_ai_bom
    bom = collect_ai_bom()
    sherpa = [c for c in bom["components"] if c["name"] == "sherpa_onnx"]
    assert sherpa, "应有 sherpa_onnx 组件（库）"
    assert sherpa[0].get("version"), "sherpa_onnx 应有动态版本（从 pubspec 提）"


def test_collect_dangling_selectors_函数级py(tmp_path):
    from spec_runner import risk
    specdir = tmp_path / "specs"
    specdir.mkdir()
    (specdir / "t.spec.md").write_text(
        "---\nspec: task\nname: t\nsatisfies: []\n---\n\n"
        "## Completion Criteria\n\n"
        "Scenario: 函数在\n  Test:\n    Package: py\n    Filter: tests/exist.py::test_present\n    Level: unit\n"
        "  Given x\n  When y\n  Then z\n\n"
        "Scenario: 函数不在\n  Test:\n    Package: py\n    Filter: tests/exist.py::test_absent\n    Level: unit\n"
        "  Given x\n  When y\n  Then z\n", encoding="utf-8")
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests" / "exist.py").write_text("def test_present(): pass\n")
    dangling = risk._collect_dangling_selectors(specs_dir=specdir, root=tmp_path)
    assert len(dangling) == 1
    assert "test_absent" in dangling[0]


def test_regression_report_还原红修复绿_有效():
    from spec_runner.regression import _regression_report
    from spec_runner.runner import ScenarioResult
    from spec_runner.verdict import Verdict
    before = [ScenarioResult("场景", "py", "f", Verdict.FAIL, "bug 在")]
    after = [ScenarioResult("场景", "py", "f", Verdict.PASS, "修了")]
    report = _regression_report(before, after)
    assert report["valid"] is True
    assert report["results"][0]["before"] == "fail" and report["results"][0]["after"] == "pass"


def test_regression_report_还原就绿无效_测试没测bug():
    from spec_runner.regression import _regression_report
    from spec_runner.runner import ScenarioResult
    from spec_runner.verdict import Verdict
    before = [ScenarioResult("场景", "py", "f", Verdict.PASS, "还原也过")]
    after = [ScenarioResult("场景", "py", "f", Verdict.PASS, "修复也过")]
    report = _regression_report(before, after)
    assert report["valid"] is False  # before PASS = 测试没测这个 bug


def test_regression_check_stash还原pop恢复跑两轮(monkeypatch):
    from spec_runner import regression
    from spec_runner.runner import ScenarioResult
    from spec_runner.verdict import Verdict
    calls = []
    monkeypatch.setattr(regression, "_git", lambda args: calls.append(tuple(args)) or "")
    monkeypatch.setattr(regression, "parse_contract_file", lambda spec: "fake_contract")
    states = iter([
        [ScenarioResult("s", "py", "f", Verdict.FAIL, "bug 在")],
        [ScenarioResult("s", "py", "f", Verdict.PASS, "修了")],
    ])
    monkeypatch.setattr(regression, "run_contract", lambda contract, execute: next(states))
    report = regression.regression_check("fake.spec.md")
    assert report["valid"] is True
    assert ("stash",) in calls and ("stash", "pop") in calls


def test_regression_check命令_valid退出0_invalid退出1(monkeypatch, capsys):
    from spec_runner import regression
    monkeypatch.setattr(regression, "regression_check", lambda spec: {"valid": True, "results": []})
    assert cli.main(["regression-check", "fake.spec.md"]) == 0
    capsys.readouterr()
    monkeypatch.setattr(regression, "regression_check",
                        lambda spec: {"valid": False, "results": [{"scenario": "s", "before": "pass", "after": "pass", "valid": False}]})
    assert cli.main(["regression-check", "fake.spec.md"]) == 1


def test_provenance_lint_缺SourceTrace_报错(tmp_path):
    from spec_runner.provenance import provenance_lint
    (tmp_path / "bad.md").write_text("# 没SourceTrace\n", encoding="utf-8")
    r = provenance_lint(tmp_path)
    assert not r["valid"]
    assert "Source Trace" in r["issues"][0]


def test_provenance_lint_缺stated_报错(tmp_path):
    from spec_runner.provenance import provenance_lint
    (tmp_path / "bad.md").write_text("## Source Trace\n- inferred(高): x\n", encoding="utf-8")
    r = provenance_lint(tmp_path)
    assert not r["valid"]  # 缺 stated（人说的来源）


def test_provenance_lint_低中置信收集升人审(tmp_path):
    from spec_runner.provenance import provenance_lint
    (tmp_path / "ok.md").write_text(
        "## Source Trace\n- stated: prd §1\n- inferred(高): a\n- inferred(低): b\n- inferred(中): c\n",
        encoding="utf-8")
    r = provenance_lint(tmp_path)
    assert r["valid"]  # 有 stated，valid
    assert len(r["low_confidence"]) == 2  # 低 + 中 置信收集


def test_provenance_lint命令_valid退出0_低置信列出(monkeypatch, capsys):
    from spec_runner import provenance
    monkeypatch.setattr(provenance, "provenance_lint", lambda d: {
        "valid": True, "issues": [], "low_confidence": ["req.md: inferred(低): x"]})
    assert cli.main(["provenance-lint", "knowledge/requirements"]) == 0
    assert "inferred(低)" in capsys.readouterr().out


def test_provenance_lint命令_invalid退出1(monkeypatch):
    from spec_runner import provenance
    monkeypatch.setattr(provenance, "provenance_lint", lambda d: {
        "valid": False, "issues": ["bad.md: 缺 Source Trace"], "low_confidence": []})
    assert cli.main(["provenance-lint", "knowledge/requirements"]) == 1


def test_shadow_report_统计level分布(tmp_path):
    from spec_runner.shadow import shadow_report
    f = tmp_path / "shadow.jsonl"
    f.write_text(
        '{"ts":1,"commit":"a","level":"R0","deny":[],"changed_files":[],"human_decision":null}\n'
        '{"ts":2,"commit":"b","level":"R1","deny":["x"],"changed_files":[],"human_decision":null}\n'
        '{"ts":3,"commit":"c","level":"R0","deny":[],"changed_files":[],"human_decision":null}\n',
        encoding="utf-8")
    r = shadow_report(f)
    assert r["total"] == 3
    assert r["by_level"] == {"R0": 2, "R1": 1}
    assert r["deny_rate"] == 1 / 3


def test_shadow_report_一致性_human_decision(tmp_path):
    from spec_runner.shadow import shadow_report
    f = tmp_path / "shadow.jsonl"
    f.write_text(
        '{"ts":1,"commit":"a","level":"R0","deny":[],"changed_files":[],"human_decision":"auto"}\n'
        '{"ts":2,"commit":"b","level":"R1","deny":[],"changed_files":[],"human_decision":"review"}\n'
        '{"ts":3,"commit":"c","level":"R0","deny":[],"changed_files":[],"human_decision":"review"}\n',
        encoding="utf-8")
    r = shadow_report(f)
    assert r["consistency"]["compared"] == 3
    assert r["consistency"]["match"] == 2  # R0→auto / R1→review 一致；R0→review 不一致


def test_shadow_report命令(monkeypatch, capsys):
    from spec_runner import shadow
    monkeypatch.setattr(shadow, "shadow_report", lambda f: {
        "total": 5, "by_level": {"R0": 5}, "deny_rate": 0.0,
        "consistency": {"compared": 0, "match": 0, "rate": None}})
    assert cli.main(["shadow-report", ".out/shadow.jsonl"]) == 0
    out = capsys.readouterr().out
    assert "total" in out and "R0" in out
