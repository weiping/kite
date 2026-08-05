---
kind: decision
id: DEC-CAP-TRANSCRIPTION
title: "语音转写层架构决策"
status: accepted
tags: [capture, architecture]
---

# 语音转写层架构决策

## Context
REQ-CAP-VOICE 系列需要语音转文字能力，需定转写层位置与模型。
charter 第1条（数据不出站）与第3条（离线优先）是硬约束。

## Alternatives Considered
- **A 端侧**（Flutter + whisper-onnx / sherpa-onnx）：不出站 ✓、离线 ✓；模型 50-200MB、质量中、首次需下载
- **B 服务端**（Python faster-whisper，上传音频）：质量好、客户端轻；音频出站（违反 charter 1）、离线不可用（违反 charter 3）
- **C 混合**（端侧默认 + 用户同意后单条送服务端）：兼顾离线与质量；M0 过复杂（YAGNI）

## Decision
选 **A 端侧**，模型 **whisper-small**（平衡质量与体积）。

## Consequences
- 正：满足 charter 第1、3条；端侧可离线；转写纯逻辑放 `services/capture/` 可属性测试（合入 L2）；模型下发秒级回退（发布 D2 试点）
- 负：客户端体积增大；首次需下载模型
- 失败模式：模型未下载 / 性能不足 → 离线降级：允许录音排队，联网后补模型再转写（REQ-CAP-VOICE-OFFLINE）
- 客户端二进制（含模型/录音）撤销成本天级 → 发布 D1（永久）
- 抽出不变量：**INV-006**（转写清洗后 MUST 保留原始转写副本）
