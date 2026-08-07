"""item 本地持久化（JSON 文件）。

M0 用 JSON 全量读写（DEC-STORE）。零依赖、可读可导出、离线。
文件损坏 → 读空兜底（不崩）。charter 第1条数据属用户：开放格式。
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from services.capture.classify import Item


class ItemStore:
    def __init__(self, path: str | Path):
        self._path = Path(path)

    def add(self, item: Item) -> None:
        items = self.list()
        items.append(item)
        self._save(items)

    def list(self) -> list[Item]:
        if not self._path.exists():
            return []
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []  # 文件损坏兜底：读空，不崩
        return [Item(**d) for d in raw]

    def clear(self) -> None:
        self._save([])

    def _save(self, items: list[Item]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
