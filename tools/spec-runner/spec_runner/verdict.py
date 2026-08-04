"""五态判定：通过、失败、跳过、不确定、待复核。

跳过不等于通过；不确定在 L2/L3 升级为人审级阻断。

序列化规则（方案「退出码到五态的映射」末尾的坑）：
待复核这个状态在常见实现里序列化成全小写无下划线的形式，写成带下划线会被静默忽略。
所以统一序列化为小写无下划线：pendingreview。
"""
from __future__ import annotations

from enum import Enum


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    UNCERTAIN = "uncertain"
    PENDING_REVIEW = "pendingreview"

    def __str__(self) -> str:
        return self.value
