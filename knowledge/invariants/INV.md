# 架构不变量

> 从 `knowledge/decisions/` 抽取，必须写成能被静态检查的形式。
> 写不成检查的，说明它还停留在愿望阶段——要么细化成规则，要么承认它只是指导原则，不要在这里充数。
> 每条不变量同时作为需求条款落在 `knowledge/requirements/REQ-INV-*.md`，与功能需求共用同一套三态追溯。

| 编号 | 不变量 | 检查手段 |
| --- | --- | --- |
| INV-001 | 客户端 MUST NOT 直接访问数据库 | Semgrep 规则 |
| INV-002 | Agent 编排层 MUST NOT 对外暴露端口 | 部署配置检查 |
| INV-003 | 合并逻辑 MUST 是纯函数 | Semgrep：禁用系统时钟调用（`rules/no-system-clock-in-merge.yaml`） |
| INV-004 | 用户数据出站 MUST 经过脱敏层 | Semgrep + OPA |
| INV-005 | 下发内容 MUST 只接受白名单组件 | 三方对齐脚本 |
| INV-006 | 转写清洗后 MUST 保留原始转写副本 | 属性测试（services/capture，REQ-INV-006） |

> 触及不变量的变更一律走最高风险档（R3），强制人审加双人批准，任何等级下都不放松。
