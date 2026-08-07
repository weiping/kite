---
kind: requirement
id: REQ-ORG-PERSIST
title: "item 本地持久化"
status: accepted
liveness: auto
tags: [organize, storage, m0]
---

## Problem
classify 产出的笔记/任务/日程需持久化，否则重启丢失、search 无法跨会话。本地优先（charter 第3条）。

## Requirements
[REQ-ORG-PERSIST-a] item MUST 持久化到本地，add 后跨进程/会话可读。
[REQ-ORG-PERSIST-b] 持久化 MUST 离线可用（本地文件，不依赖网络）。
[REQ-ORG-PERSIST-c] 存储 MUST 不丢失（多次 add，list 返回全部、顺序保留）。
[REQ-ORG-PERSIST-d] 存储格式 MUST 可读、可导出（JSON 开放格式，charter 数据属用户）。

## Scenarios
Scenario: add 后跨实例可读
  Given 一个 ItemStore(path)
  When add(item) 后新建 ItemStore(path).list()
  Then 返回含该 item
Scenario: 多次 add 不丢失
  Given 空 store
  When add 多个 item
  Then list 返回全部、顺序保留
Scenario: 导出可读 JSON
  Given 有 item 的 store
  When 读取存储文件
  Then 为合法 JSON、含 item 字段

## Dependencies
- REQ-STRUCT-CLASSIFY（存的是 classify 产出的 item）

## Source Trace
- stated: prd:Kite §5.3（笔记/任务/日程一等公民）
- stated: charter 第1条（数据属用户）、第3条（离线优先）
- inferred(高): M0 JSON 文件（无依赖、可读、可测），SQLite 后续
