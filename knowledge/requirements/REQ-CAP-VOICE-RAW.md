---
kind: requirement
id: REQ-CAP-VOICE-RAW
title: "转写原文可追溯"
status: accepted
liveness: auto
tags: [capture, ai-governance, m0]
---

## Problem
转写经 AI 清洗/重写后，用户与审计需要能回到原始转写，否则 AI 生成内容不可追溯。

## Requirements
[REQ-CAP-VOICE-RAW-a] 转写清洗后 MUST 保留原始转写副本，与清洗后文本并存。
[REQ-CAP-VOICE-RAW-b] 每条 AI 生成内容 MUST 可追溯到来源（原始转写、模型版本、提示词版本）。

## Scenarios
Scenario: 查看原始转写
  Given 一条经清洗的语音笔记
  When 用户查看来源
  Then 能看到原始转写副本与生成元信息

## Dependencies
None.

## Source Trace
- stated: charter 第4条「AI 生成内容必须可追溯到来源」
- inferred(高): 原始转写与清洗文本并存（非二选一）
