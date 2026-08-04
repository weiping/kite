"""边界强制：契约 Allowed Changes 之外的改动即判失败，只看路径与语言无关。"""
import json
from pathlib import Path

import pytest

from spec_runner.boundary import (
    allowed_changes,
    assert_no_boundary_violation,
    find_violations,
    is_test_path,
)
from spec_runner.contract import parse_contract

CONTRACT_TEXT = """\
---
spec: task
name: "t"
satisfies: []
---

## Boundaries

### Allowed Changes
- services/api/sync.py
- apps/mobile/lib/sync/merge.dart
- tests/sync/test_merge.py
- apps/mobile/test/sync/merge_test.dart

## Completion Criteria
"""


def test_is_test_path_识别各种测试路径():
    assert is_test_path("tests/sync/test_merge.py")
    assert is_test_path("apps/mobile/test/sync/merge_test.dart")
    assert is_test_path("test_foo.py")
    assert is_test_path("foo_test.dart")
    assert not is_test_path("services/api/sync.py")
    assert not is_test_path("apps/mobile/lib/sync/merge.dart")


def test_allowed_changes_默认返回全部():
    c = parse_contract(CONTRACT_TEXT)
    assert len(allowed_changes(c)) == 4


def test_allowed_changes_only_impl_滤掉测试目录():
    # repro-gate.sh 的关键：只还原实现路径，不还原测试路径
    c = parse_contract(CONTRACT_TEXT)
    impl = allowed_changes(c, only_impl=True)
    assert impl == ["services/api/sync.py", "apps/mobile/lib/sync/merge.dart"]


def test_find_violations_找出越界文件():
    allowed = ["services/api/sync.py", "apps/mobile/lib/sync/merge.dart"]
    changed = ["services/api/sync.py", "services/api/settings.py"]
    assert find_violations(changed, allowed) == ["services/api/settings.py"]


def test_find_violations_无越界返回空():
    allowed = ["services/api/sync.py"]
    assert find_violations(["services/api/sync.py"], allowed) == []


def test_assert_no_violation_无违规则通过(tmp_path: Path):
    f = tmp_path / "lifecycle.json"
    f.write_text(json.dumps({"violations": []}))
    assert_no_boundary_violation(f)  # 不抛


def test_assert_no_violation_有违规则退出码1(tmp_path: Path):
    f = tmp_path / "lifecycle.json"
    f.write_text(json.dumps({
        "violations": [{"path": "services/api/settings.py", "reason": "not covered"}],
    }))
    with pytest.raises(SystemExit) as exc:
        assert_no_boundary_violation(f)
    assert exc.value.code == 1
