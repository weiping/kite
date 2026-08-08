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
