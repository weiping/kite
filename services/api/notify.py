"""API Server 的离线通知存储。

与 Agent 编排层共享底层 storage，但按服务名 "api" 分库位，互不覆盖。
"""
from __future__ import annotations

NAME = "api"


class ApiNotify:
    def __init__(self, storage: dict):
        self._storage = storage

    def store_notify(self, user: str, payload) -> None:
        self._storage[(NAME, user)] = payload

    def get(self, user: str):
        return self._storage.get((NAME, user))
