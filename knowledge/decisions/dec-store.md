---
kind: decision
id: DEC-STORE
title: "M0 存储用 JSON 文件"
status: accepted
tags: [storage, m0]
---

# M0 存储用 JSON 文件

## Context
REQ-ORG-PERSIST 要持久化 item。需定存储方式。

## Alternatives Considered
- **A JSON 文件**：无依赖、可读、可测、离线；无索引/查询、量大后慢
- **B SQLite**（sqflite/drift）：结构化查询、索引；需依赖、移动端 native
- **C Hive/对象库**：快、对象化；需依赖、非开放格式

## Decision
M0 选 **A JSON 文件**。

## Consequences
- 正：零依赖（纯 Python）、可读可导出（charter 数据属用户）、可属性测试、离线
- 负：全量读写（量大慢）、无事务/并发
- 失败模式：文件损坏 → 读空兜底（不崩）；并发写可能丢（M0 单用户无并发）
- 等级上限：纯逻辑 `services/store/`，合入 L2
- 后续：量大或需查询 → SQLite（drift/sqflite），L2 后；导出格式保持开放
