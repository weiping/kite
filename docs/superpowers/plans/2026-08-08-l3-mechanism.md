# L3 机制（charter-lint + monthly-audit）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use checkbox (`- [ ]`).

**Goal:** L3 搭机制待用（L2 达标才切换）。① `charter-lint` 检查 requirements 的 Source Trace 引用 charter（L3 一致性论证来源）。② `monthly-audit` 月度累积效应审计骨架（shadow 趋势 + 变更计数，月度 cron）。

**Architecture:** 新增 `spec_runner/charter.py`（charter_lint）+ `spec_runner/monthly.py`（monthly_audit）。charter_lint 扫 requirements 检查 charter 引用（弱，确定性）。monthly_audit 汇总 shadow_report + git log 月度变更计数。两个 CLI 子命令 + monthly.yml 月度 cron。

**Tech Stack:** Python（spec-runner）· pytest（TDD）· GitHub Actions monthly cron

**L3 范围**：搭机制不实跑（L2 达标才切换）。charter-lint 弱（检查引用，不语义判断）。monthly-audit 轻（shadow 趋势 + 变更计数，逃逸追踪待 L2 达标后补）。

---

## File Structure

- **Create:** `tools/spec-runner/spec_runner/charter.py` — charter_lint
- **Create:** `tools/spec-runner/spec_runner/monthly.py` — monthly_audit
- **Modify:** `tools/spec-runner/spec_runner/cli.py` — 加 charter-lint + monthly-audit 子命令
- **Test:** `tools/spec-runner/tests/test_cli.py`
- **Create:** `.github/workflows/monthly.yml` — 月度 cron

---

## Task 1: charter_lint（requirements charter 引用检查）

**Files:**
- Create: `tools/spec-runner/spec_runner/charter.py`
- Test: `tools/spec-runner/tests/test_cli.py`

- [ ] **Step 1: 写失败测试**

追加到 `tools/spec-runner/tests/test_cli.py`：

```python
def test_charter_lint_检查requirements引用charter(tmp_path):
    from spec_runner.charter import charter_lint
    reqdir = tmp_path / "requirements"
    reqdir.mkdir()
    (reqdir / "with.md").write_text(
        "## Source Trace\n- stated: charter 第1条（用户数据属用户）\n", encoding="utf-8")
    (reqdir / "without.md").write_text(
        "## Source Trace\n- stated: prd §1\n", encoding="utf-8")
    (reqdir / "notrace.md").write_text("# 无 Source Trace\n", encoding="utf-8")
    r = charter_lint(reqdir)
    assert r["checked"] == 3
    assert r["with_charter"] == 1
    assert len(r["issues"]) == 2  # without + notrace
```

- [ ] **Step 2: 跑红**

Run: `.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py::test_charter_lint -v`
Expected: FAIL — `ModuleNotFoundError: spec_runner.charter`

- [ ] **Step 3: 实现**

Create `tools/spec-runner/spec_runner/charter.py`：

```python
"""charter-lint：L3 需求候选的宪章一致性论证检查。

index.md L3：Agent 发起的需求候选必须逐条论证与使命宪章的一致性。
本工具做弱检查（确定性）：扫 requirements 的 Source Trace 是否引用 charter。
语义级一致性论证由 Agent 在生成需求时做（charter_consistency 段），本工具检查"引用存在"。
"""
from __future__ import annotations

from pathlib import Path


def charter_lint(requirements_dir, charter_keyword: str = "charter") -> dict:
    """检查 requirements 的 Source Trace 引用 charter（L3 一致性论证来源）。"""
    issues: list[str] = []
    checked = 0
    with_charter = 0
    for req in sorted(Path(requirements_dir).glob("*.md")):
        text = req.read_text(encoding="utf-8")
        checked += 1
        if "## Source Trace" not in text:
            issues.append(f"{req.name}: 缺 Source Trace（无来源标注）")
            continue
        if charter_keyword in text.lower():
            with_charter += 1
        else:
            issues.append(f"{req.name}: Source Trace 未引用 charter（L3 一致性论证缺）")
    return {
        "checked": checked,
        "with_charter": with_charter,
        "coverage": with_charter / checked if checked else 0,
        "issues": issues,
    }
```

- [ ] **Step 4: 跑绿 + commit**

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py::test_charter_lint -v
git add tools/spec-runner/spec_runner/charter.py tools/spec-runner/tests/test_cli.py
git commit -m "feat(spec-runner): charter_lint（requirements charter 引用检查，L3 一致性）"
```

---

## Task 2: monthly_audit（月度累积效应审计骨架）

**Files:**
- Create: `tools/spec-runner/spec_runner/monthly.py`
- Test: `tools/spec-runner/tests/test_cli.py`

- [ ] **Step 1: 写失败测试**

追加：

```python
def test_monthly_audit_汇总shadow和变更计数(monkeypatch, tmp_path):
    from spec_runner import monthly
    shadow_file = tmp_path / "shadow.jsonl"
    shadow_file.write_text(
        '{"ts":1,"commit":"a","level":"R0","deny":[],"changed_files":[],"human_decision":null}\n',
        encoding="utf-8")
    monkeypatch.setattr(monthly, "_git_log_since", lambda since: "abc1234 msg1\ndef5678 msg2\n")
    r = monthly.monthly_audit(shadow_file, since="1 month ago")
    assert r["commits"] == 2
    assert r["shadow"]["total"] == 1
    assert r["escape_defects"] is None  # 待 L2 达标后追踪
```

- [ ] **Step 2: 跑红 + Step 3 实现 + Step 4 绿 commit**

Create `tools/spec-runner/spec_runner/monthly.py`：

```python
"""monthly-audit：L3 月度累积效应审计骨架。

L3 反馈周期月级（index.md），必须配月级检测。汇总 shadow 趋势 + 变更计数。
逃逸缺陷追踪待 L2 达标后补（当前 None）。
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from spec_runner.shadow import shadow_report


def monthly_audit(shadow_jsonl, since: str = "1 month ago") -> dict:
    """月度累积效应审计：shadow 趋势 + 变更计数。"""
    return {
        "period": since,
        "commits": len(_git_log_since(since)),
        "shadow": shadow_report(shadow_jsonl),
        "escape_defects": None,  # 待 L2 达标后追踪
    }


def _git_log_since(since: str) -> list[str]:
    try:
        r = subprocess.run(["git", "log", "--oneline", f"--since={since}"],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return []
    return [l for l in r.stdout.splitlines() if l.strip()]
```

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py -k "charter_lint or monthly_audit" -v
git add tools/spec-runner/spec_runner/monthly.py tools/spec-runner/tests/test_cli.py
git commit -m "feat(spec-runner): monthly_audit（月度累积效应审计骨架，shadow + 变更计数）"
```

---

## Task 3: CLI 子命令（charter-lint + monthly-audit）

**Files:**
- Modify: `tools/spec-runner/spec_runner/cli.py`
- Test: `tools/spec-runner/tests/test_cli.py`

- [ ] **Step 1: 写失败测试**

追加：

```python
def test_charter_lint命令(monkeypatch, capsys):
    from spec_runner import charter
    monkeypatch.setattr(charter, "charter_lint", lambda d: {
        "checked": 2, "with_charter": 2, "coverage": 1.0, "issues": []})
    assert cli.main(["charter-lint", "knowledge/requirements"]) == 0
    assert "coverage" in capsys.readouterr().out


def test_monthly_audit命令(monkeypatch, capsys):
    from spec_runner import monthly
    monkeypatch.setattr(monthly, "monthly_audit", lambda shadow, since="1 month ago": {
        "period": "1 month ago", "commits": 5,
        "shadow": {"total": 0}, "escape_defects": None})
    assert cli.main(["monthly-audit", ".out/shadow.jsonl"]) == 0
    assert "commits" in capsys.readouterr().out
```

- [ ] **Step 2: 跑红 + Step 3 实现**

cli.py 加 subparser + dispatch + 两个 cmd：

```python
    p_charter = sub.add_parser("charter-lint", help="L3 需求 charter 一致性检查（Source Trace 引用 charter）")
    p_charter.add_argument("requirements", help="requirements 目录")
    p_monthly = sub.add_parser("monthly-audit", help="L3 月度累积效应审计（shadow 趋势 + 变更计数）")
    p_monthly.add_argument("shadow", help="shadow.jsonl 路径")
    p_monthly.add_argument("--since", default="1 month ago")

# dispatch 加 "charter-lint": cmd_charter_lint, "monthly-audit": cmd_monthly_audit

def cmd_charter_lint(args) -> int:
    from spec_runner.charter import charter_lint
    print(json.dumps(charter_lint(args.requirements), ensure_ascii=False, indent=2))
    return 0

def cmd_monthly_audit(args) -> int:
    from spec_runner.monthly import monthly_audit
    print(json.dumps(monthly_audit(args.shadow, since=args.since), ensure_ascii=False, indent=2))
    return 0
```

- [ ] **Step 4: 跑绿 + 全量回归 + commit**

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/test_cli.py -k "charter or monthly" -v
.venv/bin/python -m pytest tools/spec-runner/tests/ -q
git add tools/spec-runner/spec_runner/cli.py tools/spec-runner/tests/test_cli.py
git commit -m "feat(spec-runner): charter-lint + monthly-audit 子命令"
```

---

## Task 4: monthly.yml 月度 cron

**Files:**
- Create: `.github/workflows/monthly.yml`

- [ ] **Step 1: 创建 monthly.yml**

```yaml
name: monthly
# L3 月度累积效应审计（index.md：L3 反馈周期月级，必须配月级检测）。出报告，不阻断。
on:
  schedule:
    - cron: "0 3 1 * *"  # 每月 1 号 3 点
  workflow_dispatch: {}
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {fetch-depth: 0}
      - uses: actions/setup-python@v5
        with: {python-version: '3.13'}
      - name: 装 spec-runner
        run: python -m pip install -e "tools/spec-runner[test]" hypothesis
      - name: 月度累积效应审计（L3）
        run: |
          python -m spec_runner risk > .out/risk.json || true
          python -m spec_runner monthly-audit .out/shadow.jsonl || true
      - name: charter 一致性检查
        run: python -m spec_runner charter-lint knowledge/requirements || true
```

- [ ] **Step 2: push PR + merge**

```bash
cd ~/workspace/dev/kite
git checkout -b l3-mechanism
git add .github/workflows/monthly.yml
git commit -m "ci(l3): monthly.yml 月度累积效应审计 cron（charter-lint + monthly-audit）"
git push "https://x-access-token:$(gh auth token)@github.com/weiping/kite.git" l3-mechanism
gh pr create --title "L3 机制：charter-lint + monthly-audit（搭机制待用）" --body "L3 月度审计 + 宪章一致性检查骨架" --base main --head l3-mechanism
```

R3（新 workflow）→ 自审 merge。

---

## Self-Review

**1. Spec coverage：** L3 机制最小——charter-lint（Task1 弱检查 requirements 引用 charter）+ monthly-audit（Task2 shadow + 变更计数骨架）+ CLI（Task3）+ monthly.yml cron（Task4）。需求候选管线（净化/论证）大件，骨架后续。

**2. Placeholder scan：** 无 TBD。escape_defects=None 明标"待 L2 达标后追踪"。

**3. Type consistency：** `charter_lint(requirements_dir) -> {checked, with_charter, coverage, issues}`、`monthly_audit(shadow_jsonl, since) -> {period, commits, shadow, escape_defects}` 一致。
