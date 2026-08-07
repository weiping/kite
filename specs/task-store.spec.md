spec: task
name: "item 本地持久化（JSON）"
satisfies: [REQ-ORG-PERSIST]
risk: B
---

## Intent
item 持久化到本地 JSON 文件，跨会话可读、不丢失、可导出。M0 无依赖。

## Decisions
- JSON 文件（items.json），全量读写
- 纯 Python，无 SQLite/Hive 依赖
- 文件损坏 → 读空兜底（不崩）

## Boundaries

### Allowed Changes
- services/store/store.py
- tests/store/test_store.py

### Forbidden
- 不引入 SQLite/Hive 依赖（M0）

## Completion Criteria

Scenario: add 后跨实例可读
  Test:
    Package: py
    Filter: tests/store/test_store.py::test_persist_across_instances
    Level: unit
    Targets: services/store/store.py
  Given ItemStore(path)
  When add(item) 后新建 ItemStore(path).list()
  Then 返回含该 item

Scenario: 多次 add 不丢失
  Test:
    Package: py
    Filter: tests/store/test_store.py::test_multiple_add_no_loss
    Level: property
    Targets: services/store/store.py
  Given 空 store
  When add 多个 item
  Then list 返回全部、顺序保留

Scenario: 导出可读 JSON
  Test:
    Package: py
    Filter: tests/store/test_store.py::test_export_readable_json
    Level: unit
    Targets: services/store/store.py
  Given 有 item 的 store
  When 读取存储文件
  Then 为合法 JSON、含 item 字段
