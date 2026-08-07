---
kind: requirement
id: REQ-RET-NLSEARCH
title: "自然语言检索"
status: accepted
liveness: auto
tags: [retrieve, core, m0]
---

## Problem
用户要一句话找回过去的想法。纯关键词记不住原话，但 M0 离线优先，语义检索需 embedding（后续）。

## Requirements
[REQ-RET-NLSEARCH-a] 系统 MUST 提供本地检索，输入查询返回匹配的笔记/任务/日程。
[REQ-RET-NLSEARCH-b] 每条结果 MUST 附来源引用（指向具体 item）。
[REQ-RET-NLSEARCH-c] 无匹配时 MUST 返回「未找到」，不得编造（charter 第4条）。
[REQ-RET-NLSEARCH-d] 检索 MUST 离线可用（纯函数，不依赖网络/模型）。
[REQ-RET-NLSEARCH-e] 语义检索（embedding）SHOULD 为后续增强，M0 用关键词。

## Scenarios
Scenario: 关键词匹配带来源
  Given 笔记库含「买牛奶」
  When 查询「牛奶」
  Then 返回匹配项，附来源（指向该笔记）
Scenario: 无匹配回答未找到
  Given 笔记库不含查询相关内容
  When 查询
  Then 返回「未找到」，不编造
Scenario: 离线检索可用
  Given 设备离线
  When 查询
  Then 仍返回本地匹配结果

## Dependencies
- REQ-STRUCT-CLASSIFY（检索的 item 来自分类）

## Source Trace
- stated: prd:Kite §5.4（自然语言检索 + 来源引用）
- stated: charter 第4条（不冒充确定、可追溯）
- inferred(高): M0 本地关键词（离线优先），语义 embedding 后续
