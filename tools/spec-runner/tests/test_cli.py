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
