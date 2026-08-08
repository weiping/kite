"""风险分级：汇总变更 input → opa 评估 policy/risk.rego → {level, deny}。

L1.5 风险分级接线。input 复用 affected（changed_files/lines）；
dangling_selectors/boundary_violations 阶段1占位（见 affected.py 注释），阶段2实填。
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from spec_runner.contract import parse_contract_file

POLICY_DIR = Path(__file__).resolve().parents[3] / "policy"
SPECS_DIR = POLICY_DIR.parent / "specs"

# 不需任何 spec 覆盖的自由区（元文件 / 文档 / 配置 / 工具）
WHITELIST_DIRS = (
    "specs/", "knowledge/", "policy/", "charter/", "docs/",
    ".github/", "tools/", "rules/", "evals/", ".pi/", ".agents/",
)
WHITELIST_FILES = (
    "AGENTS.md", "SOUL.md", "USER.md", "MEMORY.md", "README.md", "BOOTSTRAP.md",
    "pubspec.yaml", "pyproject.toml", "Cargo.toml", "Cargo.lock", ".gitignore",
)


def collect_risk_input() -> dict:
    """汇总 risk.rego 的 input：vs base 的 committed 改动 + 实填 boundary/dangling。"""
    data = _collect_changes_vs_base()
    data["boundary_violations"] = _count_boundary_violations(data["changed_files"])
    data["dangling_selectors"] = _collect_dangling_selectors()
    return data


def _collect_changes_vs_base() -> dict:
    """vs origin/main 的 committed 改动（PR 真实改动；避开 CI 工作区副作用如 pub get 重生成 lock）。"""
    base = _detect_base_ref()
    names = _git(["diff", "--name-only", f"{base}...HEAD"])
    numstat = _git(["diff", "--numstat", f"{base}...HEAD"])
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


def _detect_base_ref() -> str:
    for ref in ("origin/main", "origin/master"):
        if _git(["rev-parse", "--verify", ref]).strip():
            return ref
    return "HEAD~1"


def _git(args: list[str]) -> str:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return r.stdout if r.returncode == 0 else ""


def _count_boundary_violations(changed_files: list[str], specs_dir: Path | None = None) -> int:
    allowed = _collect_all_allowed(specs_dir)
    n = 0
    for f in changed_files:
        f = f.replace("\\", "/")
        if f in allowed or _is_whitelisted(f):
            continue
        n += 1
    return n


def _collect_all_allowed(specs_dir: Path | None = None) -> set[str]:
    specs_dir = specs_dir or SPECS_DIR
    allowed: set[str] = set()
    for spec in Path(specs_dir).glob("*.spec.md"):
        try:
            contract = parse_contract_file(spec)
        except Exception:
            continue
        allowed.update(p.replace("\\", "/") for p in contract.allowed_changes)
    return allowed


def _is_whitelisted(path: str) -> bool:
    if any(path.startswith(d) for d in WHITELIST_DIRS):
        return True
    if "/" not in path and (path in WHITELIST_FILES or path.endswith(".md")):
        return True
    return False


def _collect_dangling_selectors(specs_dir: Path | None = None, root: Path | None = None) -> list[str]:
    """扫所有 specs 的 scenario test selector，文件不存在或函数不存在（py）→ dangling。"""
    specs_dir = specs_dir or SPECS_DIR
    root = Path(root) if root else SPECS_DIR.parent
    dangling: list[str] = []
    for spec in Path(specs_dir).glob("*.spec.md"):
        try:
            contract = parse_contract_file(spec)
        except Exception:
            continue
        for scenario in contract.scenarios:
            sel = scenario.test
            if not sel.filter:
                continue
            if "::" in sel.filter:
                file_part, func = sel.filter.split("::", 1)
            else:
                file_part, func = sel.filter, ""
            if file_part and not (root / file_part).exists():
                dangling.append(f"{spec.name}:{sel.filter}")
                continue
            # 函数级（py）：查 def <func>(
            if func and sel.package == "py" and file_part:
                try:
                    content = (root / file_part).read_text(encoding="utf-8")
                except Exception:
                    content = ""
                if not re.search(rf"\bdef\s+{re.escape(func)}\s*\(", content):
                    dangling.append(f"{spec.name}:{sel.filter}")
    return dangling


def evaluate_risk(input_data: dict, policy: Path | None = None) -> dict:
    """opa 评估 risk.rego → {level, deny}。opa 缺失抛 FileNotFoundError。"""
    opa = shutil.which("opa")
    if opa is None:
        raise FileNotFoundError(
            "opa 未安装：brew install opa（CI 用 open-policy-agent/setup-opa action）")
    policy = policy or (POLICY_DIR / "risk.rego")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(input_data, f)
        input_file = f.name
    try:
        proc = subprocess.run(
            [opa, "eval", "--format=json", "--data", str(policy),
             "--input", input_file, "data.kite.risk"],
            capture_output=True, text=True)
    finally:
        Path(input_file).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise RuntimeError(f"opa eval 失败（退出 {proc.returncode}）: {proc.stderr}")
    val = json.loads(proc.stdout)["result"][0]["expressions"][0]["value"]
    return {"level": val.get("level"), "deny": list(val.get("deny", []))}


def _append_shadow(result: dict, input_data: dict, log_dir: Path | None = None) -> None:
    """追加影子记录到 .out/shadow.jsonl（L1→L1.5 切换准入用）。"""
    import subprocess
    import time
    log_dir = log_dir or Path(".out")
    log_dir.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(
        ["git", "rev-parse", "--short=10", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    record = {
        "ts": int(time.time()),
        "commit": commit,
        "level": result.get("level"),
        "deny": result.get("deny", []),
        "changed_files": input_data.get("changed_files", []),
        "human_decision": None,  # PR 合并时回填（阶段后续）
    }
    with (log_dir / "shadow.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
