---
id: REQ-SYNC-CONFLICT
level: MUST
status: accepted
provenance:
  stated: []
  inferred: []
---

# REQ-SYNC-CONFLICT 离线笔记冲突合并

同一条笔记在两台设备并发修改后，合并结果 MUST 与到达顺序无关，且 MUST NOT 丢失正文。

## Notes
- 服务端与客户端各实现一份行为等价的合并函数，两者 MUST 通过差分测试比对一致性。
- 正文冲突保留两份并标记冲突；元数据按字段级最后写入优先，比较依据是记录自带的时间戳。
- 受 `REQ-INV-003`（合并逻辑是纯函数）约束：MUST NOT 读取系统时钟。
