"""边界强制。

只看路径，与语言无关，零适配成本——这是「Agent 改了不该改的东西」最便宜的拦截手段。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from spec_runner.contract import Contract


def is_test_path(path: str) -> bool:
    p = path.replace("\\", "/")
    parts = p.split("/")
    name = parts[-1]
    if "tests" in parts or "test" in parts:
        return True
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if name.endswith("_test.dart"):
        return True
    return False


def allowed_changes(contract: Contract, only_impl: bool = False) -> list[str]:
    if not only_impl:
        return list(contract.allowed_changes)
    return [p for p in contract.allowed_changes if not is_test_path(p)]


def find_violations(changed: list[str], allowed: list[str]) -> list[str]:
    allowed_set = {p.replace("\\", "/") for p in allowed}
    return [
        p for p in changed
        if p.replace("\\", "/") not in allowed_set
    ]


def assert_no_boundary_violation(lifecycle_path: str | Path) -> None:
    """读 agent-spec lifecycle 输出的 JSON，有边界违规则以退出码 1 终止。"""
    data = json.loads(Path(lifecycle_path).read_text(encoding="utf-8"))
    violations = data.get("violations")
    if isinstance(violations, list) and violations:
        for v in violations:
            path = v.get("path", "?") if isinstance(v, dict) else str(v)
            reason = v.get("reason", "not covered by any allowed boundary") if isinstance(v, dict) else ""
            print(f"[FAIL] [boundaries] {path}\n    reason: {reason}", file=sys.stderr)
        sys.exit(1)
    if isinstance(data.get("boundary_violations"), int) and data["boundary_violations"] > 0:
        print(f"[FAIL] [boundaries] {data['boundary_violations']} 处越界", file=sys.stderr)
        sys.exit(1)
