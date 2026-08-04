"""Agent 编排层的离线通知存储。

两服务共享一个底层 storage（依赖注入），但按各自服务名分库位（key = (service, user)），
因此同一用户的通知不会被另一服务覆盖——满足 REQ-NOTIFY-ISOLATION。
"""
from __future__ import annotations

NAME = "orchestrator"


class OrchestratorNotify:
    def __init__(self, storage: dict):
        self._storage = storage

    def store_notify(self, user: str, payload) -> None:
        self._storage[(NAME, user)] = payload

    def get(self, user: str):
        return self._storage.get((NAME, user))
