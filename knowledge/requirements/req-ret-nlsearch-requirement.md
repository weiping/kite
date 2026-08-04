---
kind: requirement
id: REQ-RET-NLSEARCH
title: "自然语言检索"
status: proposed
liveness: auto
tags: [retrieve, core]
---

## Problem
用户要一句话找回过去的想法，不能只靠关键词。

## Requirements
[REQ-RET-NLSEARCH] 系统 MUST 提供自然语言检索，返回语义相关结果并附来源引用。

## Scenarios
Scenario: 自然语言检索带来源
  Given 用户的历史笔记、任务、日程
  When 用户用一句话提问
  Then 返回语义相关结果，每条附来源引用；无依据时回答未找到

## Dependencies
None.


## Source Trace

- prd:Kite-5.4
## Open Questions
None.
