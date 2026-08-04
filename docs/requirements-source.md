# Kite 需求 intake 源

从 PRD（prd.md §5）抽取的核心需求块，供 `agent-spec requirements import` 编译进
`knowledge/requirements/`。import 后为 `proposed`，人评审接受后才进 plan 覆盖。

<!-- agent-spec:requirement id=REQ-CAP-VOICE title="语音速记" tags=capture,core source=prd:Kite-5.1 -->
## Problem
用户在路上或忙时想到点子，需要零摩擦捕获。

## Requirements
[REQ-CAP-VOICE] 系统 MUST 提供语音速记入口：长按或点按开始录音，松手即提交转写。

## Scenarios
Scenario: 语音速记
  Given 用户在应用内或通过快捷入口
  When 长按开始录音并说话后松手
  Then 录音提交并开始转写为文字

## Dependencies
None.

## Open Questions
None.
<!-- /agent-spec:requirement -->

<!-- agent-spec:requirement id=REQ-STRUCT-CLASSIFY title="自动结构化分类" tags=structure,core source=prd:Kite-5.2 -->
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

## Open Questions
None.
<!-- /agent-spec:requirement -->

<!-- agent-spec:requirement id=REQ-RET-NLSEARCH title="自然语言检索" tags=retrieve,core source=prd:Kite-5.4 -->
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

## Open Questions
None.
<!-- /agent-spec:requirement -->
