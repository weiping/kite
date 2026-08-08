"""审计包（audit-seal）：收集每次变更的审计制品 + 生成 CycloneDX AI-BOM。

原则（L1.5 出口准则）：只收集不生产，全部用现成标准。
- 制品只存引用（evidence/risk/shadow 等），不复制内容（轨迹外置，脱敏在采集侧）
- AI-BOM 用 CycloneDX 格式（模型/工具/提示词作为组件），不自造格式
"""
from __future__ import annotations


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
