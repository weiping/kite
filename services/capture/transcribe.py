"""语音转写清洗：保留原始转写副本（INV-006）+ 元信息可追溯。

清洗为纯函数：clean_transcript(raw, meta) -> {clean, raw, meta}。
端侧 whisper-small 的调用是平台层，本模块只管清洗纯逻辑。
"""
from __future__ import annotations

from dataclasses import dataclass

_FILLERS = {"嗯", "啊", "那个", "这个", "然后", "就是"}


@dataclass(frozen=True)
class TranscriptResult:
    clean: str
    raw: str
    meta: dict


def clean_transcript(raw: str, meta: dict) -> TranscriptResult:
    cleaned = " ".join(w for w in raw.split() if w not in _FILLERS)
    return TranscriptResult(clean=cleaned.strip(), raw=raw, meta=dict(meta))
