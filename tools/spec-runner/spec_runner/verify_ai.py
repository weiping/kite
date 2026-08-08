"""verify-ai：L2 柱二层5（Verifier）+ 层6（独立裁决）的概率性裁决。

调智谱 GLM（key 从 ZHIPUAI_API_KEY 环境变量，绝不入仓）。对 spec 的 scenario：
- 层5 Verifier：给 scenario + targets 实现代码，问"有没有附带损害/越界"
- 层6 独立裁决：不假设契约对，独立推演合理行为 vs 契约，找契约洞
index.md：概率性只处理不确定项 + 高风险，零确定性无法判定的才调模型。
"""
from __future__ import annotations

import os


def _client():
    """惰性建智谱 client（key 从环境变量，绝不入仓）。"""
    from zhipuai import ZhipuAI
    return ZhipuAI(api_key=os.environ["ZHIPUAI_API_KEY"])


def _call_zhipu(prompt: str, model: str = "glm-4-flash", system: str | None = None) -> str:
    """调智谱，返回模型文本。缺 key 抛 RuntimeError（友好，不崩）。"""
    if not os.environ.get("ZHIPUAI_API_KEY"):
        raise RuntimeError("缺 ZHIPUAI_API_KEY 环境变量（智谱 GLM，绝不入仓）")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = _client().chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content


def layer5_verify(scenario: str, gwt: str, targets_code: str) -> dict:
    """层5 Verifier：检查实现有没有附带损害/越出契约边界（不质疑契约本身）。"""
    system = (
        "你是 Verifier（L2 反自洽链层5）。检查实现有没有【附带损害】（改坏别的）或"
        "【越界】（超出契约边界）。只看实现是否违背 scenario，不质疑契约本身。"
        "先给结论 VERIFY_OK/VERIFY_FAIL，再一句理由。"
    )
    prompt = (
        f"Scenario: {scenario}\nGiven/When/Then: {gwt}\n\n"
        f"实现代码:\n{targets_code}\n\n"
        "这个实现有没有附带损害或越界？"
    )
    text = _call_zhipu(prompt, system=system)
    ok = text.strip().upper().startswith("VERIFY_OK")
    return {"verdict": "pass" if ok else "concerns", "reasoning": text}


def layer6_adjudicate(scenario: str, gwt: str, requirement: str) -> dict:
    """层6 独立裁决：不假设契约对，独立推演合理行为 vs 契约，找契约洞。"""
    system = (
        "你是独立裁决者（L2 反自洽链层6）。【不假设契约是对的】。先独立推演这个需求"
        "的合理行为，再与契约对比，指出契约有没有漏。给结论 ADJUDICATE_OK（契约没问题）"
        "/ ADJUDICATE_CONCERN（契约有洞），再一句理由。"
    )
    prompt = (
        f"需求: {requirement}\n契约 Scenario: {scenario}\nGiven/When/Then: {gwt}\n\n"
        "独立推演合理行为，与契约对比，契约有没有洞？"
    )
    text = _call_zhipu(prompt, system=system)
    ok = text.strip().upper().startswith("ADJUDICATE_OK")
    return {"verdict": "pass" if ok else "concerns", "reasoning": text}


def verify_ai(spec_path) -> dict:
    """对 spec 的每个 scenario 跑层5 Verifier + 层6 独立裁决，汇总。"""
    from spec_runner.contract import parse_contract_file
    contract = parse_contract_file(spec_path)
    results = []
    for sc in contract.scenarios:
        gwt = f"Given {sc.given} When {sc.when} Then {sc.then}"
        l5 = layer5_verify(sc.name, gwt, targets_code="(targets 实现代码，运行时注入)")
        l6 = layer6_adjudicate(sc.name, gwt, requirement=contract.name)
        results.append({"scenario": sc.name, "layer5": l5, "layer6": l6})
    return {"contract": contract.name, "results": results}
