"""解析 W3C DTCG（Design Token Common Format）令牌树。

DTCG 节点含 `$value` 与 `$type` 即为一个令牌；其余是分组（可嵌套）。
以 `$` 开头的键（$schema/$description 等）是元数据，跳过。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    path: tuple[str, ...]
    value: str
    type: str


def parse_tokens(dtcg: dict) -> list[Token]:
    out: list[Token] = []
    _walk(dtcg, (), out)
    return out


def _walk(node, prefix: tuple[str, ...], out: list[Token]) -> None:
    if not isinstance(node, dict):
        return
    if "$value" in node and "$type" in node:
        out.append(Token(prefix, str(node["$value"]), node["$type"]))
        return
    for key, child in node.items():
        if key.startswith("$"):
            continue
        _walk(child, prefix + (key,), out)
