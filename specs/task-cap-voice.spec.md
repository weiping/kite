spec: task
name: "语音速记：转写清洗与离线排队"
satisfies: [REQ-CAP-VOICE, REQ-CAP-VOICE-RAW, REQ-CAP-VOICE-OFFLINE, REQ-INV-006]
risk: B
---

## Intent
语音速记的纯逻辑层：转写清洗（保留原文副本 + 元信息可追溯）与离线捕获排队。
端侧录音 / whisper 调用是平台层（dart），本契约聚焦可在 Python 属性测试的纯逻辑。

## Decisions
- 清洗为纯函数：clean(raw, meta) -> {clean, raw, meta}，不丢原文（INV-006）
- 离线队列为纯数据结构：入队/出队/补传，不丢、按序
- 端侧转写（Flutter + whisper-small）见 dec-cap-transcription，非本契约

## Boundaries

### Allowed Changes
- services/capture/transcribe.py
- services/capture/queue.py
- tests/capture/test_transcribe.py
- tests/capture/test_queue.py

### Forbidden
- 不在清洗中丢弃原始转写
- 不在排队中丢失或乱序捕获

## Completion Criteria

Scenario: 清洗后保留原始转写副本
  Test:
    Package: py
    Filter: tests/capture/test_transcribe.py::test_clean_keeps_raw
    Level: property
    Targets: services/capture/transcribe.py
  Given 任意原始转写文本与模型元信息
  When 清洗
  Then 输出同时含清洗文本与原始转写副本

Scenario: 转写元信息可追溯
  Test:
    Package: py
    Filter: tests/capture/test_transcribe.py::test_meta_traceable
    Level: unit
    Targets: services/capture/transcribe.py
  Given 模型版本与提示词版本
  When 清洗
  Then 输出 meta 含 model_version 与 prompt_version

Scenario: 离线排队不丢失不乱序
  Test:
    Package: py
    Filter: tests/capture/test_queue.py::test_offline_queue_preserves_order
    Level: property
    Targets: services/capture/queue.py
  Given 一串离线捕获
  When 入队后逐条出队（模拟联网补传）
  Then 出队顺序与入队一致且无丢失

Scenario: 长按入口录音
  Test:
    Package: dart
    Filter: apps/mobile/test/capture/voice_entry_test.dart::test_long_press_records
    Level: unit
    Targets: apps/mobile/lib/capture/voice_entry.dart
  Given 用户长按语音入口
  When 松手
  Then 录音提交转写
