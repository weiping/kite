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
[REQ-PROTO-POISON] 非法包或乱序包 MUST NOT 导致连接挂死或影响其他会话。

## Scenarios
Scenario: 乱序非法报文不挂死
  Given 一个在线会话
  When 收到一串乱序、非法、边界的报文序列
  Then 该会话不挂死，且其他会话不受影响

## Dependencies
None.

## Source Trace
- prd:Kite 架构不变量

## Open Questions
None.
