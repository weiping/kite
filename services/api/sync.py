"""离线笔记冲突合并。

设计依据 specs/task-sync-conflict.spec.md 的 Decisions：
- 正文冲突不做自动截断或三方合并，保留两份并标记冲突
- 元数据按字段级最后写入优先，比较依据是记录自带时间戳，不读系统时钟（INV-003）

合并结果与到达顺序无关：正文按字典序稳定拼接、字段按 (ts, value) 取最大值，
两类 tie-break 都确定且与参数顺序无关，故 merge(a,b) == merge(b,a)。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Field:
    value: str
    ts: int


@dataclass(frozen=True)
class Note:
    id: str
    body: str
    metadata: dict[str, Field] = field(default_factory=dict)


def merge_notes(local: Note, remote: Note) -> Note:
    return Note(
        id=local.id,
        body=_merge_body(local.body, remote.body),
        metadata=_merge_metadata(local.metadata, remote.metadata),
    )


def _merge_body(x: str, y: str) -> str:
    if x == y:
        return x
    first, second = sorted((x, y))
    return f"<<CONFLICT>>\n- {first}\n- {second}\n<<END>>"


def _merge_metadata(a: dict[str, Field], b: dict[str, Field]) -> dict[str, Field]:
    merged: dict[str, Field] = {}
    for key in a.keys() | b.keys():
        fa = a.get(key)
        fb = b.get(key)
        merged[key] = fa if fb is None else fb if fa is None else _pick(fa, fb)
    return merged


def _pick(fa: Field, fb: Field) -> Field:
    # 字段级 LWW：ts 大者；ts 相同取 value 字典序大者（确定性 + 与顺序无关）
    return fa if (fa.ts, fa.value) >= (fb.ts, fb.value) else fb
