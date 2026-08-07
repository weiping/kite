---
kind: decision
id: DEC-STRUCT-CLASSIFY
title: "M0 结构化分类用规则"
status: accepted
tags: [structure, m0]
---

# M0 结构化分类用规则

## Context
REQ-STRUCT-CLASSIFY 要把转写文本归类笔记/任务/日程。需定分类方式。

## Alternatives Considered
- **A 规则分类**（触发词/日期）：纯测、零撤销、离线；准确率中、需维护词表
- **B AI 分类**（LLM）：准确率高、泛化；需模型/联网、可追溯成本（charter 第4条）、撤销成本高
- **C 混合**（规则兜底 + AI 增强）：兼顾；M0 过复杂（YAGNI）

## Decision
M0 选 **A 规则分类**。

## Consequences
- 正：纯函数可属性测试（合入 L2）；离线（charter 第3条）；可追溯（规则显式，非 AI 黑箱）
- 负：准确率依赖词表；中文口语多变可能漏
- 失败模式：无触发词 → 兜底笔记；多义句 → 多类产出
- 等级上限：纯逻辑 `services/capture/classify.py`，合入 L2；无模型，发布侧不涉及
- 后续：AI 分类作为增强（需可追溯 + 置信标注），L2 后
