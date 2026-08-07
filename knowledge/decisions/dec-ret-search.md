---
kind: decision
id: DEC-RET-SEARCH
title: "M0 检索用本地关键词"
status: accepted
tags: [retrieve, m0]
---

# M0 检索用本地关键词

## Context
REQ-RET-NLSEARCH 要一句话找回。需定检索方式。

## Alternatives Considered
- **A 本地关键词**（字符 n-gram 匹配）：纯测、离线、零撤销；无语义理解
- **B embedding 语义检索**（向量）：语义强；需模型/算力、可追溯成本
- **C 混合**（本地兜底 + 语义增强）：兼顾；M0 过复杂

## Decision
M0 选 **A 本地关键词检索**。

## Consequences
- 正：纯函数可测（合入 L2）；离线（charter 第3条）；无模型、可追溯（规则显式）
- 负：无语义（同义词/记不住原话找不到）；中文分词简化
- 失败模式：查询无关 → 未找到（不编造）
- 等级上限：纯逻辑 `services/capture/search.py`，合入 L2
- 后续：embedding 语义检索作为增强（需端侧模型 + 可追溯），L2 后
