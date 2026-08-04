"""spec-runner 命令行入口。

子命令：
  run <specs> --out <dir>                 执行契约绑定的测试，产出 evidence.json
  gate <evidence.json> --level L1         五态门禁（返回退出码）
  allowed-changes <contract> [--only-impl] 打印契约允许的变更路径
  assert-no-boundary-violation <lifecycle.json>
  affected [--format json]                受影响路径（供策略门禁）
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from spec_runner.boundary import allowed_changes, assert_no_boundary_violation
from spec_runner.contract import parse_contract_file
from spec_runner.gate import gate
from spec_runner.runner import default_execute, run_contract, to_evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spec-runner", description="agent-spec 执行器适配与五态门禁")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="执行契约绑定的测试")
    p_run.add_argument("specs", help="specs 目录或单个 *.spec.md")
    p_run.add_argument("--out", default=".out")

    p_gate = sub.add_parser("gate", help="对 evidence 跑五态门禁")
    p_gate.add_argument("evidence")
    p_gate.add_argument("--level", default="L1")

    p_ac = sub.add_parser("allowed-changes", help="打印契约允许的变更路径")
    p_ac.add_argument("contract")
    p_ac.add_argument("--only-impl", action="store_true")

    sub.add_parser("assert-no-boundary-violation").add_argument("lifecycle")

    sub.add_parser("affected").add_argument("--format", default="json")

    p_bridge = sub.add_parser("bridge", help="跑 spec-runner 并注入 agent-spec resolve-ai")
    p_bridge.add_argument("spec")
    p_bridge.add_argument("--code", default=".")

    args = parser.parse_args(argv)
    return {
        "run": cmd_run,
        "gate": cmd_gate,
        "allowed-changes": cmd_allowed_changes,
        "assert-no-boundary-violation": cmd_assert,
        "affected": cmd_affected,
        "bridge": cmd_bridge,
    }[args.cmd](args)


def cmd_run(args) -> int:
    specs = Path(args.specs)
    files = sorted(specs.glob("*.spec.md")) if specs.is_dir() else [specs]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_results: list[dict] = []
    for f in files:
        contract = parse_contract_file(f)
        evidence = to_evidence(contract, run_contract(contract, default_execute))
        (out_dir / f"{_base_name(f)}.evidence.json").write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        all_results += evidence["results"]
    (out_dir / "evidence.json").write_text(
        json.dumps({"results": all_results}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def _base_name(path: Path) -> str:
    name = path.name
    suffix = ".spec.md"
    return name[:-len(suffix)] if name.endswith(suffix) else path.stem


def cmd_gate(args) -> int:
    data = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    ok, problems = gate(data["results"], level=args.level)
    for p in problems:
        print(p, file=sys.stderr)
    return 0 if ok else 1


def cmd_allowed_changes(args) -> int:
    contract = parse_contract_file(args.contract)
    for p in allowed_changes(contract, only_impl=args.only_impl):
        print(p)
    return 0


def cmd_assert(args) -> int:
    try:
        assert_no_boundary_violation(args.lifecycle)
        return 0
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1


def cmd_affected(args) -> int:
    from spec_runner.affected import collect_affected
    print(json.dumps(collect_affected(), ensure_ascii=False, indent=2))
    return 0


def cmd_bridge(args) -> int:
    from spec_runner.bridge import bridge
    return bridge(args.spec, code=args.code)
