spec: task
name: "合并逻辑纯函数静态保证"
satisfies: [REQ-INV-003]
risk: A
---

## Intent
用静态扫描保证合并逻辑不读取系统时钟，满足 REQ-INV-003b。

## Decisions
- 用 semgrep 规则 rules/no-system-clock-in-merge.yaml 在合并模块路径上拦截系统时钟调用

## Boundaries

### Allowed Changes
- rules/no-system-clock-in-merge.yaml
- services/api/sync.py

### Forbidden
- 不放宽规则覆盖范围以绕过检查

## Completion Criteria

Scenario: 合并不读系统时钟
  Test:
    Package: semgrep
    Filter: rules/no-system-clock-in-merge.yaml
    Level: static
    Targets: services/api/sync.py
  Given 合并函数实现 services/api/sync.py
  When 对其运行 semgrep 规则 rules/no-system-clock-in-merge.yaml
  Then 规则报告 0 个命中
