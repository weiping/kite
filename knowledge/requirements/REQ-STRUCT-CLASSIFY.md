---
kind: requirement
id: REQ-STRUCT-CLASSIFY
title: "自动结构化分类"
status: accepted
liveness: auto
tags: [structure, core, m0]
---

## Problem
一条捕获（转写文本）需自动归类为笔记/任务/日程、提取 action items、生成标题与标签。否则用户要手动整理，违背「最低心智负担」。

## Requirements
[REQ-STRUCT-CLASSIFY-a] 系统 MUST 把一条捕获归类，可同时产出笔记/任务/日程多项。
[REQ-STRUCT-CLASSIFY-b] 含 action-item 触发词的句子 MUST 提取为任务（要做/记得/别忘了/计划/打算…）。
[REQ-STRUCT-CLASSIFY-c] 含日期时间的句子 SHOULD 提取为日程（明天/下周一/3点…）。
[REQ-STRUCT-CLASSIFY-d] 每条产出 MUST 生成非空标题（首句或前 N 字）。
[REQ-STRUCT-CLASSIFY-e] 规则分类 MUST 是纯函数、可属性测试；AI 分类为后续。

## Scenarios
Scenario: 触发词产出任务
  Given 一段含「明天要做报告」的文本
  When 分类
  Then 产出至少一条任务，标题含原句要点
Scenario: 无触发词归笔记
  Given 一段不含触发词的叙述文本
  When 分类
  Then 产出笔记、不出任务
Scenario: 一条文本产出多类
  Given 一段同时含任务与日期的文本
  When 分类
  Then 同时产出任务与日程

## Dependencies
- REQ-CAP-VOICE（上游文本来自转写）

## Source Trace
- stated: prd:Kite §5.2（归类/action item/标题/标签）
- stated: prd:Kite G1（最低心智负担）
- inferred(高): M0 用规则分类（纯函数可测），AI 后续（charter 第4条可追溯）
