"""契约解析：把 specs/*.spec.md 解析成结构化的 Contract。"""
from pathlib import Path

from spec_runner.contract import Contract, parse_contract, parse_contract_file


SAMPLE = """\
---
spec: task
name: "离线笔记冲突合并"
satisfies: [REQ-SYNC-CONFLICT]
risk: A
---

## Intent
合并两条笔记。

## Decisions
- 保留两份并标记冲突

## Boundaries

### Allowed Changes
- services/api/sync.py
- apps/mobile/lib/sync/merge.dart
- tests/sync/test_merge.py
- apps/mobile/test/sync/merge_test.dart

### Forbidden
- 不读取系统时间
- 不在合并中发起网络或数据库访问

## Completion Criteria

Scenario: 合并与到达顺序无关
  Test:
    Package: py
    Filter: tests/sync/test_merge.py::test_merge_is_commutative
    Level: property
    Targets: services/api/sync.py
  Given 任意一对笔记版本
  When 以两种顺序分别合并
  Then 两次结果相等

Scenario: 冲突时两份正文都在
  Test:
    Package: py
    Filter: tests/sync/test_merge.py::test_keeps_both_bodies
    Level: unit
    Targets: services/api/sync.py
  Given 一条笔记的两个版本正文不同
  When 合并
  Then 两份正文都保留并标记冲突
"""


def test_解析_frontmatter():
    c = parse_contract(SAMPLE)
    assert c.spec == "task"
    assert c.name == "离线笔记冲突合并"
    assert c.satisfies == ("REQ-SYNC-CONFLICT",)
    assert c.risk == "A"


def test_解析边界():
    c = parse_contract(SAMPLE)
    assert c.allowed_changes == (
        "services/api/sync.py",
        "apps/mobile/lib/sync/merge.dart",
        "tests/sync/test_merge.py",
        "apps/mobile/test/sync/merge_test.dart",
    )
    assert c.forbidden == ("不读取系统时间", "不在合并中发起网络或数据库访问")


def test_解析多场景与测试选择器():
    c = parse_contract(SAMPLE)
    assert len(c.scenarios) == 2
    s0 = c.scenarios[0]
    assert s0.name == "合并与到达顺序无关"
    assert s0.test.package == "py"
    assert s0.test.filter == "tests/sync/test_merge.py::test_merge_is_commutative"
    assert s0.test.level == "property"
    assert s0.test.targets == ("services/api/sync.py",)
    assert s0.given == "任意一对笔记版本"
    assert s0.when == "以两种顺序分别合并"
    assert s0.then == "两次结果相等"


def test_第二个场景是例子级():
    c = parse_contract(SAMPLE)
    s1 = c.scenarios[1]
    assert s1.name == "冲突时两份正文都在"
    assert s1.test.level == "unit"


def test_解析真实仓库契约():
    repo_root = Path(__file__).resolve().parents[3]
    c = parse_contract_file(repo_root / "specs" / "task-sync-conflict.spec.md")
    assert c.satisfies == ("REQ-SYNC-CONFLICT",)
    assert "services/api/sync.py" in c.allowed_changes
    assert len(c.scenarios) >= 1
    assert c.scenarios[0].test.package == "py"
    assert c.scenarios[0].test.level == "property"


def test_缺_frontmatter_报错():
    import pytest
    with pytest.raises(ValueError):
        parse_contract("没有 frontmatter 的文本")
