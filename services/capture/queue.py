"""离线捕获队列：入队/出队/补传，不丢失、不乱序。

纯数据结构，离线时本地排队，联网后 drain 按序补传（REQ-CAP-VOICE-OFFLINE）。
"""
from __future__ import annotations


class CaptureQueue:
    def __init__(self) -> None:
        self._items: list = []

    def enqueue(self, capture) -> None:
        self._items.append(capture)

    def drain(self) -> list:
        items = list(self._items)
        self._items.clear()
        return items

    def __len__(self) -> int:
        return len(self._items)
