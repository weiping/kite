---
kind: requirement
id: REQ-CAP-VOICE
title: "语音速记入口"
status: accepted
liveness: auto
tags: [capture, voice, m0]
---

## Problem
用户在路上或忙时想到点子，需要零摩擦捕获。语音是最低摩擦的输入方式。

## Requirements
[REQ-CAP-VOICE-a] 系统 MUST 提供语音速记入口：长按或点按开始录音，松手即提交转写。
[REQ-CAP-VOICE-b] 从入口触发到开始录音 MUST ≤ 3 秒（P50），避免捕获摩擦。
[REQ-CAP-VOICE-c] 录音 MUST 可中途取消，取消不产生任何持久化记录。

## Scenarios
Scenario: 长按语音速记
  Given 用户在应用内或通过快捷入口
  When 长按开始录音并说话后松手
  Then 录音提交并开始转写为文字
Scenario: 中途取消不留存
  Given 用户正在录音
  When 用户取消录音
  Then 不保留任何录音与转写产物

## Dependencies
- REQ-CAP-VOICE-OFFLINE
- REQ-CAP-VOICE-RAW

## Source Trace
- stated: prd:Kite §5.1（长按/点按/松手提交）
- stated: prd:Kite G1（捕获零摩擦 ≤3s）
- inferred(高): 中途取消不持久化——隐私默认（charter 第1条数据属用户）

## Open Questions
None.
