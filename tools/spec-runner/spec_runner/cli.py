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

    p_risk = sub.add_parser("risk", help="风险分级：评估 policy/risk.rego → {level, deny}")
    p_risk.add_argument("--policy", default=None, help="risk.rego 路径（默认 policy/risk.rego）")

    p_audit = sub.add_parser("audit-seal", help="收集审计包（制品引用 + CycloneDX AI-BOM）→ .out/audit/<commit>.json")
    p_audit.add_argument("--archive", action="store_true", help="入库 audit-seal/（永久保留，默认 .out/ CI artifact）")

    p_reg = sub.add_parser("regression-check", help="回归有效性验证（L2 反自洽层3）：修复前红/后绿/还原红")
    p_reg.add_argument("spec", help="契约文件（绑定测试，假设工作区含修复）")

    p_prov = sub.add_parser("provenance-lint", help="需求 provenance 检查（L2 需求接受：Source Trace + 低/中置信升人审）")
    p_prov.add_argument("requirements", help="requirements 目录（knowledge/requirements）")

    p_shadow = sub.add_parser("shadow-report", help="影子运行观测（L1.5→L2 切换准入：level 分布 + 一致性）")
    p_shadow.add_argument("jsonl", help="shadow.jsonl 路径（.out/shadow.jsonl）")

    args = parser.parse_args(argv)
    return {
        "run": cmd_run,
        "gate": cmd_gate,
        "allowed-changes": cmd_allowed_changes,
        "assert-no-boundary-violation": cmd_assert,
        "affected": cmd_affected,
        "bridge": cmd_bridge,
        "risk": cmd_risk,
        "audit-seal": cmd_audit_seal,
        "regression-check": cmd_regression_check,
        "provenance-lint": cmd_provenance_lint,
        "shadow-report": cmd_shadow_report,
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


def cmd_risk(args) -> int:
    from spec_runner.risk import collect_risk_input, evaluate_risk, _append_shadow
    input_data = collect_risk_input()
    try:
        result = evaluate_risk(input_data, policy=Path(args.policy) if args.policy else None)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    _append_shadow(result, input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["deny"] else 0


def cmd_audit_seal(args) -> int:
    from spec_runner.audit_seal import collect_audit_package, get_commit
    commit = get_commit()
    risk_level = "?"
    risk_file = Path(".out/risk.json")
    if risk_file.exists():
        try:
            risk_level = json.loads(risk_file.read_text(encoding="utf-8")).get("level", "?")
        except Exception:
            pass
    pkg = collect_audit_package(commit, risk_level)
    out_dir = Path("audit-seal") if args.archive else Path(".out/audit")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{commit}.json"
    out_file.write_text(json.dumps(pkg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"audit_seal": str(out_file)}, ensure_ascii=False))
    return 0


def cmd_regression_check(args) -> int:
    from spec_runner.regression import regression_check
    report = regression_check(args.spec)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


def cmd_provenance_lint(args) -> int:
    from spec_runner.provenance import provenance_lint
    report = provenance_lint(args.requirements)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


def cmd_shadow_report(args) -> int:
    from spec_runner.shadow import shadow_report
    report = shadow_report(args.jsonl)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0
