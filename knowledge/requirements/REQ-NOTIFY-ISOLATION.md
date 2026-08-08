---
kind: requirement
id: REQ-NOTIFY-ISOLATION
title: "离线通知存储隔离"
status: accepted
liveness: auto
tags: [sync, isolation]
---

## Problem
Agent 编排层与 API Server 共用离线通知存储时，默认写同一库位会互相覆盖。

## Requirements
[REQ-NOTIFY-ISOLATION-a] 两服务的离线通知存储 MUST 写入不同库位。
[REQ-NOTIFY-ISOLATION-b] 同一用户的通知 MUST NOT 被另一服务覆盖。

## Scenarios
Scenario: 同一序列打两个服务不互相覆盖
  Given 两服务共享离线通知存储、同一用户 U
  When 同一通知序列分别送达两服务
  Then 两服务写入不同库位，U 的通知在各自库位均完整保留

## Dependencies
None.

## Source Trace
- stated: prd:Kite §5.5 Sync

## Open Questions
None.
