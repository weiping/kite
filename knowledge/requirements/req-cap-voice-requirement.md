---
kind: requirement
id: REQ-CAP-VOICE
title: "语音速记"
status: proposed
liveness: auto
tags: [capture, core]
---

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


## Source Trace

- prd:Kite-5.1
## Open Questions
None.
