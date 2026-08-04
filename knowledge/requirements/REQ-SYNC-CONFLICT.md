---
kind: requirement
id: REQ-SYNC-CONFLICT
title: "离线笔记冲突合并"
status: accepted
liveness: auto
tags: [sync, core]
---

## Problem
同一条笔记在两台设备并发修改后合并，结果必须与到达顺序无关、且不丢失正文。

## Requirements
[REQ-SYNC-CONFLICT] 合并结果 MUST 与到达顺序无关，且 MUST NOT 丢失正文。
客户端与服务端各实现一份行为等价的合并函数，两者 MUST 通过差分测试比对一致性。

## Scenarios
Scenario: 合并与到达顺序无关
  Given 任意一对笔记版本
  When 以两种顺序分别合并
  Then 两次结果相等
Scenario: 冲突时两份正文都在
  Given 一条笔记的两个版本正文不同
  When 合并
  Then 两份正文都保留并标记冲突

## Dependencies
- REQ-INV-003（合并逻辑是纯函数）

## Source Trace
- prd:Kite §5.5 Sync

## Open Questions
None.
