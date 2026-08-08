"""审计包（audit-seal）：收集每次变更的审计制品 + 生成 CycloneDX AI-BOM。

原则（L1.5 出口准则）：只收集不生产，全部用现成标准。
- 制品只存引用（evidence/risk/shadow 等），不复制内容（轨迹外置，脱敏在采集侧）
- AI-BOM 用 CycloneDX 格式（模型/工具/提示词作为组件），不自造格式
"""
from __future__ import annotations

import subprocess
import time


def collect_ai_bom() -> dict:
    """生成 CycloneDX AI-BOM：kite 的模型/工具作为组件。"""
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "components": [
            {"type": "data", "name": "sherpa-onnx-whisper-small",
             "bom-ref": "model:whisper-small",
             "description": "端侧语音转写模型（DEC-CAP-TRANSCRIPTION 选 A）"},
            {"type": "application", "name": "agent-spec",
             "bom-ref": "tool:agent-spec",
             "description": "意图编译器（规约→契约）"},
            {"type": "application", "name": "spec-runner",
             "bom-ref": "tool:spec-runner",
             "description": "契约执行器 + 五态门禁 + 风险分级"},
            {"type": "application", "name": "opa",
             "bom-ref": "tool:opa",
             "description": "Rego 策略评估（risk.rego 风险分级）"},
        ],
    }


def collect_audit_package(commit: str, risk_level: str) -> dict:
    """收集审计包：制品引用（外置）+ AI-BOM + 元数据。

    制品只存引用路径，不复制内容（L1.5：轨迹外置，脱敏在采集侧）。
    """
    return {
        "commit": commit,
        "timestamp": int(time.time()),
        "risk_level": risk_level,
        "artifacts": {
            "evidence": ".out/evidence.json",       # 五态判定 + 覆盖矩阵
            "risk": ".out/risk.json",               # 风险分级 level/deny
            "shadow": ".out/shadow.jsonl",          # 影子记录
            "design_lint": "docs/ixd/DESIGN.md（verify.yml @google/design.md lint）",
            "evals": "evals/",                       # 评测跑分
            "mutation": ".github/workflows/nightly.yml",  # 变异得分
        },
        "ai_bom": collect_ai_bom(),
    }


def get_commit() -> str:
    """当前 commit 短 SHA（审计包文件名 + 元数据）。"""
    return subprocess.run(
        ["git", "rev-parse", "--short=10", "HEAD"],
        capture_output=True, text=True).stdout.strip() or "unknown"
