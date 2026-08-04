"""affected：从 git diff 收集受影响路径，输出给策略门禁（OPA/conftest）。

risk.rego 需要：changed_files、changed_lines、dangling_selectors、boundary_violations。
dangling_selectors 与 boundary_violations 由 spec-gate/边界强制填，这里先占位。
"""
from __future__ import annotations

import subprocess


def collect_affected() -> dict:
    names = _git(["diff", "--name-only", "HEAD"])
    numstat = _git(["diff", "--numstat", "HEAD"])
    changed_lines = 0
    for line in numstat.splitlines():
        parts = line.split()
        if parts and parts[0].isdigit():
            changed_lines += int(parts[0])
    return {
        "changed_files": [n for n in names.splitlines() if n.strip()],
        "changed_lines": changed_lines,
        "dangling_selectors": [],
        "boundary_violations": 0,
    }


def _git(args: list[str]) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return r.stdout if r.returncode == 0 else ""
