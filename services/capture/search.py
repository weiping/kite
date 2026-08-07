"""本地关键词检索（M0）：item 库 + 查询 → 匹配项 + 来源。

字符 n-gram 匹配（中文分词简化，DEC-RET-SEARCH）。纯函数，离线可用。
charter 第4条：无匹配返回「未找到」，不编造；每条匹配附来源（item 本身）。
"""
from __future__ import annotations

from dataclasses import dataclass

from services.capture.classify import Item


@dataclass(frozen=True)
class Match:
    item: Item      # 来源引用（指向具体 item）
    score: int      # 匹配的 token 数


@dataclass(frozen=True)
class SearchResult:
    matches: tuple[Match, ...]

    @property
    def found(self) -> bool:
        return len(self.matches) > 0


def _tokens(query: str) -> list[str]:
    """中文分词简化：2-gram + 单字（无需 jieba）。"""
    q = query.strip()
    bigrams = [q[i:i + 2] for i in range(len(q) - 1)]
    chars = [c for c in q if c.strip()]
    return [t for t in bigrams + chars if t.strip()]


def search(items, query: str) -> SearchResult:
    """在 item 库里按查询匹配，返回带来源的匹配项（按 score 降序）。"""
    tokens = set(_tokens(query))
    matches: list[Match] = []
    for item in items:
        score = sum(1 for t in tokens if t in item.title or t in item.text)
        if score > 0:
            matches.append(Match(item, score))
    matches.sort(key=lambda m: -m.score)
    return SearchResult(tuple(matches))
