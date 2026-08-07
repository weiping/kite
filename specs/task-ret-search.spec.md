spec: task
name: "本地关键词检索"
satisfies: [REQ-RET-NLSEARCH]
risk: B
---

## Intent
输入查询，返回匹配的笔记/任务/日程 + 来源引用。无匹配「未找到」。M0 本地关键词。

## Decisions
- 字符 n-gram 匹配（中文分词简化，无需 jieba）
- 纯函数，离线，无模型
- 来源 = 匹配的 item 本身

## Boundaries

### Allowed Changes
- services/capture/search.py
- tests/capture/test_search.py

### Forbidden
- 不引入 embedding/模型（M0）

## Completion Criteria

Scenario: 关键词匹配带来源
  Test:
    Package: py
    Filter: tests/capture/test_search.py::test_keyword_match_with_source
    Level: unit
    Targets: services/capture/search.py
  Given 笔记库含查询词
  When 检索
  Then 返回匹配项，附来源（item）

Scenario: 无匹配回答未找到
  Test:
    Package: py
    Filter: tests/capture/test_search.py::test_no_match_returns_not_found
    Level: property
    Targets: services/capture/search.py
  Given 笔记库不含查询相关内容
  When 检索
  Then found 为 False（不编造）

Scenario: 离线检索可用
  Test:
    Package: py
    Filter: tests/capture/test_search.py::test_offline_pure
    Level: unit
    Targets: services/capture/search.py
  Given 任意本地 item 库与查询
  When 检索（无网络）
  Then 返回结果（纯函数，不依赖网络）
