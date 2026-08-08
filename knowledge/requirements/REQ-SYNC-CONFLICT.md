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
[REQ-SYNC-CONFLICT-a] 合并结果 MUST 与到达顺序无关（交换律）。
[REQ-SYNC-CONFLICT-b] 合并 MUST NOT 丢失任一版本的正文。
[REQ-SYNC-CONFLICT-c] 客户端与服务端各实现一份行为等价的合并函数，两者 MUST 通过差分测试比对一致性。

## Scenarios
Scenario: 合并与到达顺序无关
  Given 任意一对内容不同的笔记版本 A 与 B
  When 分别计算 merge(A,B) 与 merge(B,A)
  Then 两次输出的正文与元数据按值完全相等
Scenario: 冲突时两份正文都保留
  Given 一条笔记的两个版本正文不同
  When 合并
  Then 输出含 CONFLICT 标记，且两份正文均原样保留

## Dependencies
- REQ-INV-003（合并逻辑是纯函数）

## Source Trace
- stated: prd:Kite §5.5 Sync

## Open Questions
None.
