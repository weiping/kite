"""执行器适配的公共类型。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from spec_runner.verdict import Verdict


@dataclass(frozen=True)
class ExecResult:
    """一次外部执行的原始结果。collected 由调用方解析后传入，否则各 adapter 自行从输出解析。"""
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    collected: int | None = None


class Adapter(Protocol):
    package: str

    def classify(self, result: ExecResult) -> tuple[Verdict, str]:
        """把执行结果映射到五态判定 + 人类可读的理由。"""
        ...


def combined(result: ExecResult) -> str:
    return f"{result.stdout}\n{result.stderr}"
