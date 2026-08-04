spec: task
name: "离线通知存储隔离"
satisfies: [REQ-NOTIFY-ISOLATION]
risk: B
---

## Intent
Agent 编排层与 API Server 的离线通知存储不互相覆盖。

## Decisions
- 两服务写不同库位（按服务名分键）
- 用差分测试：同一序列打两服务，比对副作用

## Boundaries

### Allowed Changes
- services/orchestrator/notify.py
- services/api/notify.py
- tests/notify/test_isolation.py

### Forbidden
- 不让两服务共享同一默认库位

## Completion Criteria

Scenario: 同一序列打两个服务不互相覆盖
  Test:
    Package: py
    Filter: tests/notify/test_isolation.py::test_two_services_do_not_overwrite
    Level: property
    Targets: services/orchestrator/notify.py
  Given 两服务共享离线通知存储、同一用户 U
  When 同一通知序列分别送达两服务
  Then 两服务写入不同库位，U 的通知在各自库位均完整保留
