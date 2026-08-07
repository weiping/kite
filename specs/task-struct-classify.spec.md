spec: task
name: "结构化分类（规则）"
satisfies: [REQ-STRUCT-CLASSIFY]
risk: B
---

## Intent
把转写文本按规则归类为笔记/任务/日程，提取 action items，生成标题。M0 不用 AI。

## Decisions
- 规则分类（触发词/日期），纯函数，可属性测试
- 触发词表可维护（services/capture/classify.py）
- 无触发词兜底笔记

## Boundaries

### Allowed Changes
- services/capture/classify.py
- tests/capture/test_classify.py

### Forbidden
- 不引入 AI/模型依赖（M0 规则）

## Completion Criteria

Scenario: 触发词产出任务
  Test:
    Package: py
    Filter: tests/capture/test_classify.py::test_action_word_produces_task
    Level: property
    Targets: services/capture/classify.py
  Given 一段含任务触发词的文本
  When 分类
  Then 产出至少一条任务

Scenario: 无触发词归笔记
  Test:
    Package: py
    Filter: tests/capture/test_classify.py::test_plain_text_becomes_note
    Level: property
    Targets: services/capture/classify.py
  Given 一段不含触发词的叙述文本
  When 分类
  Then 仅产出笔记、不出任务

Scenario: 一条文本产出多类
  Test:
    Package: py
    Filter: tests/capture/test_classify.py::test_multi_category
    Level: unit
    Targets: services/capture/classify.py
  Given 一段同时含任务触发词与日期的文本
  When 分类
  Then 同时产出任务与日程

Scenario: 生成标题
  Test:
    Package: py
    Filter: tests/capture/test_classify.py::test_title_generated
    Level: unit
    Targets: services/capture/classify.py
  Given 一段文本
  When 分类
  Then 每条产出含非空标题
