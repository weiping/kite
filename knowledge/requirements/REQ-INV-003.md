---
id: REQ-INV-003
level: MUST
status: accepted
invariant: INV-003
---

# REQ-INV-003 合并逻辑是纯函数

合并逻辑 MUST 是纯函数，MUST NOT 读取系统时钟。

## Test
- Package: semgrep
- Filter: rules/no-system-clock-in-merge.yaml
- Level: static

> 将不变量写成需求条款，使静态规则被注释掉时需求追溯会变红，
> 防止架构约束在无人察觉的情况下消失。
