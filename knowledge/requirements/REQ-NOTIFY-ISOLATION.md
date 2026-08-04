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
[REQ-NOTIFY-ISOLATION] 两服务的离线通知存储 MUST NOT 互相覆盖。

## Scenarios
Scenario: 同一序列打两个服务结果一致
  Given 两服务共享离线通知存储
  When 同一通知序列分别送达两服务
  Then 两者响应与副作用一致，无互相覆盖

## Dependencies
None.

## Source Trace
- prd:Kite §5.5 Sync

## Open Questions
None.
