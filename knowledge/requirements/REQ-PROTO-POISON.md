---
kind: requirement
id: REQ-PROTO-POISON
title: "协议抗毒化"
status: accepted
liveness: auto
tags: [proto, robustness]
---

## Problem
非法或乱序报文若导致连接挂死或波及其他会话，会破坏服务可用性。

## Requirements
[REQ-PROTO-POISON-a] 非法包或乱序包 MUST NOT 导致连接挂死。
[REQ-PROTO-POISON-b] 非法包或乱序包 MUST NOT 影响其他会话的状态。

## Scenarios
Scenario: 乱序非法报文不挂死不波及
  Given 一个在线会话 S1 及另一个无关会话 S2
  When 向 S1 发送一串乱序、非法、边界的报文序列
  Then S1 在阈值内返回响应或关闭，S2 的已有状态保持不变

## Dependencies
None.

## Source Trace
- prd:Kite 架构不变量

## Open Questions
None.
