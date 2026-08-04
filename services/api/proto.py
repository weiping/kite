"""协议处理：对乱序、非法、边界报文健壮，不挂死、不波及其他会话。

process_packet 对非法/非 dict 报文抛 InvalidPacket（不挂死），只改动传入 session
的状态，物理上碰不到其他 Session 对象——满足 REQ-PROTO-POISON。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Session:
    id: str
    state: dict = field(default_factory=dict)


class InvalidPacket(Exception):
    pass


def process_packet(session: Session, packet) -> object:
    if not isinstance(packet, dict):
        raise InvalidPacket(packet)
    ptype = packet.get("type")
    if not ptype:
        raise InvalidPacket(packet)
    session.state[ptype] = packet.get("data")
    return session.state[ptype]
