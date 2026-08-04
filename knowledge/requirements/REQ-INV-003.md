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
[REQ-INV-003a] 合并逻辑 MUST 是纯函数。
[REQ-INV-003b] 合并逻辑 MUST NOT 读取系统时钟；时间戳比较依据 MUST 为记录自带字段。

## Scenarios
Scenario: 合并不读系统时钟
  Given 合并函数实现 services/api/sync.py
  When 对其运行 semgrep 规则 rules/no-system-clock-in-merge.yaml
  Then 规则报告 0 个命中

## Dependencies
None.

## Source Trace
- invariant:INV-003

## Open Questions
None.
