---
id: REQ-PROTO-POISON
level: MUST
status: accepted
---

# REQ-PROTO-POISON 协议抗毒化

非法包或乱序包 MUST NOT 导致连接挂死或影响其他会话。

## Test
- 确定性探索引擎：属性与状态机（Hypothesis state machines），自动生成乱序、非法、边界报文序列。
- 失败自动收缩到最小复现序列。
