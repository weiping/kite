---
kind: requirement
id: REQ-INV-003
title: "合并逻辑是纯函数"
status: accepted
liveness: auto
tags: [invariant, sync]
---

## Problem
合并逻辑若读取系统时钟，结果将不可复现、与到达顺序相关，破坏交换律。

## Requirements
[REQ-INV-003] 合并逻辑 MUST 是纯函数，MUST NOT 读取系统时钟。
比较依据是记录自带的时间戳。

## Scenarios
Scenario: 合并不读系统时钟
  Given 合并函数实现
  When 静态扫描规则 no-system-clock-in-merge
  Then 无系统时钟调用

## Dependencies
None.

## Source Trace
- invariant:INV-003

## Open Questions
None.
