# L2-1 回归有效性验证 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use checkbox (`- [ ]`).

**Goal:** spec-runner 加 `regression-check` 子命令，验证"修复真的让测试从红变绿、且测试确实在测这个修复"（反自洽链层3，index.md 点名"整条链最省钱"）。

**Architecture:** 新增 `spec_runner/regression.py`。`regression_check(spec)` 假设工作区含修复（git diff 有改动）：`git stash`（还原）→ `run_contract`（期望红 FAIL）→ `git stash pop`（恢复）→ `run_contract`（期望绿 PASS）。`_regression_report` 比对 before/after：每个 scenario `before=FAIL && after=PASS` 才算有效（before=PASS 说明测试没测这个 bug = 自洽但不正确）。

**Tech Stack:** Python（spec-runner）· git stash（状态切换）· pytest（TDD）

**L2 反自洽链层3 规则**：修复前相关测试必须红；修复后必须绿；还原必须再红（第三段 = before 的还原红，两次机械执行证明三段）。零模型调用。

**范围**：regression-check 工具（工作区修复假设）。CI 接线因 PR 工作区干净（stash 无效）留后续——本工具主要用于 Agent 修复任务的本地/会话内验证（修完跑一遍再 commit）。

---

## File Structure

- **Create:** `tools/spec-runner/spec_runner/regression.py` — regression_check + _regression_report + _git
- **Modify:** `tools/spec-runner/spec_runner/cli.py` — 加 regression-check 子命令 + cmd_regression_check
- **Test:** `tools/spec-runner/tests/test_cli.py` — regression 测试

---

## Task 1: _regression_report（before/after → 有效判定，纯函数）

**Files:**
- Create: `tools/spec-runner/spec_runner/regression.py`
- Test: `tools/spec-runner/tests/test_cli.py`

- [ ] **Step 1: 写失败测试**

追加到 `tools/spec-runner/tests/test_cli.py`：

```python
def test_regression_report_还原红修复绿_有效():
    from spec_runner.regression import _regression_report
    from spec_runner.runner import ScenarioResult
    from spec_runner.verdict import Verdict
    before = [ScenarioResult("场景", "py", "f", Verdict.FAIL, "bug 在")]
    after = [ScenarioResult("场景", "py", "f", Verdict.PASS, "修了")]
    report = _regression_report(before, after)
    assert report["valid"] is True
    assert report["results"][0]["before"] == "fail" and report["results"][0]["after"] == "pass"


def test_regression_report_还原就绿_无效（测试没测bug）():
    from spec_runner.regression import _regression_report
    from spec_runner.runner import ScenarioResult
    from spec_runner.verdict import Verdict
    before = [ScenarioResult("场景", "py", "f", Verdict.PASS, "还原也过")]
    after = [ScenarioResult("场景", "py", "f", Verdict.PASS, "修复也过")]
    report = _regression_report(before, after)
    assert report["valid"] is False  # before PASS = 测试没测这个 bug
```

- [ ] **Step 2: 跑红**

Run: `.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py -k "regression_report" -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'spec_runner.regression'`

- [ ] **Step 3: 实现**

Create `tools/spec-runner/spec_runner/regression.py`：

```python
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
```

- [ ] **Step 4: 跑绿 + commit**

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py -k "regression_report" -v
git add tools/spec-runner/spec_runner/regression.py tools/spec-runner/tests/test_cli.py
git commit -m "feat(spec-runner): _regression_report 回归有效性判定（before FAIL + after PASS）"
```

---

## Task 2: regression_check（git stash/pop + run_contract）

**Files:**
- Modify: `tools/spec-runner/spec_runner/regression.py`
- Test: `tools/spec-runner/tests/test_cli.py`

- [ ] **Step 1: 写失败测试**

追加到 `tools/spec-runner/tests/test_cli.py`：

```python
def test_regression_check_stash还原pop恢复跑两轮(monkeypatch):
    from spec_runner import regression
    from spec_runner.runner import ScenarioResult
    from spec_runner.verdict import Verdict
    calls = []
    monkeypatch.setattr(regression, "_git", lambda args: calls.append(tuple(args)) or "")
    # 第一次 run_contract（还原态）FAIL，第二次（修复态）PASS
    states = iter([
        [ScenarioResult("s", "py", "f", Verdict.FAIL, "bug 在")],
        [ScenarioResult("s", "py", "f", Verdict.PASS, "修了")],
    ])
    monkeypatch.setattr(regression, "run_contract", lambda contract, execute: next(states))
    report = regression.regression_check("fake.spec.md")
    assert report["valid"] is True
    assert ("stash",) in calls and ("stash", "pop") in calls
```

- [ ] **Step 2: 跑红**

Run: `.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py::test_regression_check_stash还原pop恢复跑两轮 -v`
Expected: FAIL — `AttributeError: module 'spec_runner.regression' has no attribute 'regression_check'`

- [ ] **Step 3: 实现**

追加到 `tools/spec-runner/spec_runner/regression.py`（顶部加 import，`_regression_report` 之后加函数）：

顶部 import 区加：

```python
import subprocess
from pathlib import Path

from spec_runner.contract import parse_contract_file
from spec_runner.runner import default_execute, run_contract
```

`_regression_report` 之后加：

```python
def regression_check(spec_path: str | Path, execute=default_execute) -> dict:
    """回归有效性验证：假设工作区含修复，stash 还原 → 跑（期望红）→ pop 恢复 → 跑（期望绿）。"""
    contract = parse_contract_file(spec_path)
    _git(["stash"])                        # 还原修复
    before = run_contract(contract, execute)
    _git(["stash", "pop"])                 # 恢复修复
    after = run_contract(contract, execute)
    return _regression_report(before, after)


def _git(args: list[str]) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return r.stdout if r.returncode == 0 else ""
```

- [ ] **Step 4: 跑绿 + 全量回归 + commit**

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py -k "regression" -v
.venv/bin/python -m pytest tools/spec-runner/tests/ -q
git add tools/spec-runner/spec_runner/regression.py tools/spec-runner/tests/test_cli.py
git commit -m "feat(spec-runner): regression_check（git stash/pop + run_contract 两轮）"
```

---

## Task 3: regression-check CLI 子命令

**Files:**
- Modify: `tools/spec-runner/spec_runner/cli.py`
- Test: `tools/spec-runner/tests/test_cli.py`

- [ ] **Step 1: 写失败测试**

追加到 `tools/spec-runner/tests/test_cli.py`：

```python
def test_regression_check命令_valid退出0_invalid退出1(monkeypatch, capsys):
    from spec_runner import regression
    # valid 场景
    monkeypatch.setattr(regression, "regression_check", lambda spec: {"valid": True, "results": []})
    assert cli.main(["regression-check", "fake.spec.md"]) == 0
    capsys.readouterr()
    # invalid 场景（测试没测 bug）
    monkeypatch.setattr(regression, "regression_check",
                        lambda spec: {"valid": False, "results": [{"scenario": "s", "before": "pass", "after": "pass", "valid": False}]})
    assert cli.main(["regression-check", "fake.spec.md"]) == 1
```

- [ ] **Step 2: 跑红**

Run: `.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py::test_regression_check命令_valid退出0_invalid退出1 -v`
Expected: FAIL — argparse `invalid choice: 'regression-check'`

- [ ] **Step 3: 实现**

Modify `tools/spec-runner/spec_runner/cli.py`：

(a) subparser 区（`p_audit` 之后）加：

```python
    p_reg = sub.add_parser("regression-check",
                           help="回归有效性验证（L2 反自洽层3）：修复前红/后绿/还原红")
    p_reg.add_argument("spec", help="契约文件（绑定测试，假设工作区含修复）")
```

(b) dispatch dict 加 `"regression-check": cmd_regression_check,`

(c) `cmd_audit_seal` 之后加：

```python
def cmd_regression_check(args) -> int:
    from spec_runner.regression import regression_check
    report = regression_check(args.spec)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1
```

- [ ] **Step 4: 跑绿 + 全量回归 + commit**

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py -k "regression" -v
.venv/bin/python -m pytest tools/spec-runner/tests/ -q
git add tools/spec-runner/spec_runner/cli.py tools/spec-runner/tests/test_cli.py
git commit -m "feat(spec-runner): regression-check 子命令（valid 退 0 / invalid 退 1）"
```

---

## Task 4: 用法文档（CI 接线留后续）

**Files:**
- Modify: `tools/spec-runner/README.md`（或 verify.yml 注释）

> regression-check 假设工作区含修复（未 commit），CI 的 PR 工作区干净（stash 无效）。所以本工具主要用于 **Agent 修复任务的会话内验证**（修完跑一遍再 commit），不直接接 CI。CI 接线需改成 commit-ref 模式（HEAD vs HEAD~1），留 L2 后续。

- [ ] **Step 1: README 加用法**

在 `tools/spec-runner/README.md` 加一节：

```markdown
## regression-check（L2 回归有效性验证）

验证修复真的让测试从红变绿、且测试确实在测这个修复（反自洽链层3）。

    spec-runner regression-check <spec>

假设工作区含修复（git diff 有改动）。stash 还原跑测试（期望红）→ pop 恢复跑（期望绿）。
before=FAIL + after=PASS 才有效；before=PASS 说明测试没测这个 bug（自洽但不正确）→ 退 1。

主要给 Agent 修复任务用：修完跑一遍再 commit。CI 接线（commit-ref 模式）留后续。
```

- [ ] **Step 2: commit + push 走 PR**

```bash
cd ~/workspace/dev/kite
git add tools/spec-runner/README.md
git commit -m "docs(spec-runner): regression-check 用法（L2 反自洽层3）"
git push "https://x-access-token:$(gh auth token)@github.com/weiping/kite.git" l2-1-regression
gh pr create --title "L2-1: 回归有效性验证（反自洽链层3）" --body "regression-check 子命令" --base main --head l2-1-regression
```

---

## Self-Review

**1. Spec coverage：** L2-1 回归有效性验证 = regression-check 工具。`_regression_report`（Task1 判定）+ `regression_check`（Task2 stash/pop 两轮）+ CLI（Task3）+ 用法（Task4）。反自洽层3 三段规则（前红/后绿/还原红）由 before FAIL + after PASS 覆盖（还原红 = before）。

**2. Placeholder scan：** 无 TBD。每步完整代码。Task4 明确 CI 接线留后续（commit-ref 模式）。

**3. Type consistency：** `_regression_report(before, after) -> dict`、`regression_check(spec_path, execute=default_execute) -> dict`、`cmd_regression_check(args) -> int`（0/1）一致。测试 monkeypatch 签名匹配（`regression._git`、`regression.run_contract`、`regression.regression_check`）。
