"""结构化分类（规则）：文本 → 笔记/任务/日程 + 标题。

M0 用触发词/日期规则（DEC-STRUCT-CLASSIFY）。纯函数，可属性测试。
无 AI/模型依赖。charter 第4条可追溯：规则显式，非黑箱。
"""
from __future__ import annotations

from dataclasses import dataclass

ACTION_WORDS = frozenset({
    "要做", "记得", "别忘了", "计划", "打算", "完成", "办", "买",
    "联系", "回复", "提交", "整理", "准备", "确认",
})
DATE_WORDS = frozenset({
    "明天", "今天", "后天", "下周一", "下周二", "下周三", "下次",
    "周一", "周二", "周三", "周四", "周五", "周六", "周日",
})


@dataclass(frozen=True)
class Item:
    kind: str   # note / task / event
    title: str
    text: str


@dataclass(frozen=True)
class ClassifyResult:
    items: tuple[Item, ...]

    @property
    def notes(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.kind == "note")

    @property
    def tasks(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.kind == "task")

    @property
    def events(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.kind == "event")


def _sentences(text: str) -> list[str]:
    for sep in ("。", "！", "？", "!", "?", "\n"):
        text = text.replace(sep, sep + "\n")
    return [s.strip() for s in text.split("\n") if s.strip()]


def _title(s: str, n: int = 20) -> str:
    return s[:n].strip()


def classify(text: str) -> ClassifyResult:
    """把文本按规则分类。action 词 → task；日期 → event；都无 → 兜底 note。"""
    items: list[Item] = []
    for s in _sentences(text):
        if any(w in s for w in ACTION_WORDS):
            items.append(Item("task", _title(s), s))
        elif any(w in s for w in DATE_WORDS):
            items.append(Item("event", _title(s), s))
    if not items:
        items.append(Item("note", _title(text), text))
    return ClassifyResult(tuple(items))
