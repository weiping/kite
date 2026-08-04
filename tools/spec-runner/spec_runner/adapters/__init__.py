"""执行器注册表：契约里 Test.Package 字段直接当作判别式。

py        → pytest
dart      → flutter test
semgrep   → 让静态不变量也能被契约绑定
"""
from __future__ import annotations

from types import SimpleNamespace

from . import flutter_adapter, pytest_adapter, semgrep_adapter

ADAPTERS: dict[str, SimpleNamespace] = {
    "py": pytest_adapter,
    "dart": flutter_adapter,
    "semgrep": semgrep_adapter,
}


def classify(package: str, exit_code: int, stdout: str = "", stderr: str = "", collected: int | None = None):
    from spec_runner.adapters.base import ExecResult
    adapter = ADAPTERS.get(package)
    if adapter is None:
        from spec_runner.verdict import Verdict
        return Verdict.UNCERTAIN, f"未知执行器 Package: {package}"
    return adapter.classify(ExecResult(exit_code, stdout, stderr, collected))
