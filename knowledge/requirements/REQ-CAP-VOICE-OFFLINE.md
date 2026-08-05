---
kind: requirement
id: REQ-CAP-VOICE-OFFLINE
title: "语音速记离线可用"
status: accepted
liveness: auto
tags: [capture, voice, offline, m0]
---

## Problem
用户常在地铁等无网环境捕获想法，离线不可用即违背"最低心智负担"。

## Requirements
[REQ-CAP-VOICE-OFFLINE-a] 当设备离线时，系统 MUST 仍接受语音捕获并本地排队。
[REQ-CAP-VOICE-OFFLINE-b] 联网后系统 MUST 自动将排队的捕获提交转写。
[REQ-CAP-VOICE-OFFLINE-c] 离线期间 MUST NOT 因无网而拒绝录音或丢失录音。

## Scenarios
Scenario: 离线录音排队
  Given 设备离线
  When 用户长按录音并提交
  Then 录音本地排队，不报错、不丢失

## Dependencies
None.

## Source Trace
- stated: charter 第3条「离线可用性优先于新功能」
- stated: prd:Kite §5.1「离线排队」
- inferred(高): 联网自动补传，无需人触发
