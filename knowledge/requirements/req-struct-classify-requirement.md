---
kind: requirement
id: REQ-STRUCT-CLASSIFY
title: "自动结构化分类"
status: proposed
liveness: auto
tags: [structure, core]
---

## Problem
一条捕获需要自动归类为笔记/任务/日程，并提取 action items。

## Requirements
[REQ-STRUCT-CLASSIFY] 系统 MUST 把一条捕获自动归类到笔记/任务/日程之一，并可同时产出多项。

## Scenarios
Scenario: 一条捕获产出笔记与任务
  Given 一段转写文本
  When 结构化处理
  Then 输出含至少一条笔记或任务，并标注标题与标签

## Dependencies
- REQ-CAP-VOICE


## Source Trace

- prd:Kite-5.2
## Open Questions
None.
