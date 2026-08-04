spec: task
name: "协议抗毒化"
satisfies: [REQ-PROTO-POISON]
risk: B
---

## Intent
后端协议处理对乱序、非法、边界报文健壮，不挂死、不波及其他会话。

## Decisions
- 用属性状态机（Hypothesis）自动生成乱序/非法报文序列遍历协议层
- 失败自动收缩到最小复现序列

## Boundaries

### Allowed Changes
- services/api/proto.py
- tests/proto/test_poison.py

### Forbidden
- 不在协议处理中持有跨会话可变全局状态

## Completion Criteria

Scenario: 乱序非法报文不挂死不波及
  Test:
    Package: py
    Filter: tests/proto/test_poison.py::test_poison_does_not_hang_or_leak
    Level: property
    Targets: services/api/proto.py
  Given 一个在线会话 S1 及另一个无关会话 S2
  When 向 S1 发送一串乱序、非法、边界的报文序列
  Then S1 在阈值内返回响应或关闭，S2 的已有状态保持不变
