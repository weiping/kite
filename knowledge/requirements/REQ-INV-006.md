---
kind: requirement
id: REQ-INV-006
title: "转写清洗保留原始转写副本"
status: accepted
liveness: auto
tags: [invariant, capture, ai-governance]
---

## Problem
转写经清洗/重写后，若丢弃原始转写，AI 生成内容将不可追溯（违反 charter 第4条）。

## Requirements
[REQ-INV-006] 转写清洗后 MUST 保留原始转写副本，与清洗文本并存。

## Scenarios
Scenario: 清洗不丢原文
  Given 任意原始转写文本
  When 清洗
  Then 输出同时含清洗文本与原始转写副本

## Dependencies
None.

## Source Trace
- invariant:INV-006（from dec-cap-transcription）
- stated: charter 第4条
