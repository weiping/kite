---
spec: task
name: "离线笔记冲突合并"
satisfies: [REQ-SYNC-CONFLICT]
risk: A
---

## Intent
在客户端与服务端各实现一份行为等价的合并函数，
使同一条笔记在两台设备并发修改后，结果与到达顺序无关，且不丢失正文。

## Decisions
- 正文冲突不做自动截断或三方合并，保留两份并标记冲突
- 元数据按字段级最后写入优先，比较依据是记录自带的时间戳，不读系统时钟

## Boundaries

### Allowed Changes
- services/api/sync.py
- apps/mobile/lib/sync/merge.dart
- tests/sync/test_merge.py
- apps/mobile/test/sync/merge_test.dart

### Forbidden
- 不读取系统时间
- 不在合并中发起网络或数据库访问

## Completion Criteria

Scenario: 合并与到达顺序无关
  Test:
    Package: py
    Filter: tests/sync/test_merge.py::test_merge_is_commutative
    Level: property
    Targets: services/api/sync.py
  Given 任意一对笔记版本
  When 以两种顺序分别合并
  Then 两次结果相等

Scenario: 冲突时两份正文都保留
  Test:
    Package: py
    Filter: tests/sync/test_merge.py::test_keeps_both_bodies_and_marks_conflict
    Level: unit
    Targets: services/api/sync.py
  Given 一条笔记的两个版本正文不同
  When 合并
  Then 两份正文都保留并标记冲突
