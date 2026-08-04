# Kite

一个个人 AI 助理：语音或文字速记，自动结构化为笔记、任务、日程；本地优先，离线可写；自然语言检索与追问。客户端 Flutter 双端，后端 Python（Agent 编排层 + API Server）。

本仓库同时承载一套 **AI 自主开发分级方案**（合入自主 L1→L3 / 发布自主 D1→D3），方案原文见 [`docs/`](docs/)。

## 目录速查

| 路径 | 作用 | 方案出处 |
| --- | --- | --- |
| `reversibility.yaml` | 撤销成本登记表，门禁的输入 | 让撤销成本变成会阻断构建的东西 |
| `charter/MISSION.md` | 使命宪章（人写、Agent 只读），L3 锚 | L3：使命宪章 |
| `knowledge/` | 需求中间表示（requirements / invariants / decisions / standards） | 架构：不变量必须能被机器检查 |
| `specs/*.spec.md` | 任务契约，L1 的人审对象 | 规约 |
| `policy/*.rego` | 门禁策略（risk / boundary / reversibility） | 门禁怎么写 |
| `rules/*.yaml` | 静态检查规则，被不变量绑定 | 架构 |
| `doc/ixd/` | 交互设计产物（逐页规约 / DESIGN.md / SDUI 组件白名单） | 界面 |
| `packages/design/` | 由 DESIGN.md 编译出的 Flutter 主题 | 界面 |
| `apps/mobile/` `services/` | Flutter 客户端 / Python 后端 | 仓库长什么样 |
| `tools/spec-runner/` | 执行器适配与五态门禁 | 契约怎么绑定测试 |
| `tools/dtcg2flutter/` `tools/ixd2spec/` `tools/audit-seal/` `tools/orchestrator/` | 自研工具 | 技能编排工作流 / 自研清单 |
| `evals/skills/` | 技能回归样本 | 一条贯穿全篇的阶梯 |
| `state/fingerprints.json` | 跨运行缺陷指纹库（随 PR 提交） | 状态存在哪 |
| `.claude/agents.json` `.claude/skills/` | 角色权限与技能定义 | 角色隔离靠权限 |
| `.github/workflows/` | 验证流水线（spec-gate / verify / e2e / nightly） | 测试：分层与四条工作流 |

## 三条摆放原则

1. **能入库的一律入库** —— 契约、策略、登记表、指纹、技能、评测样本都是文本文件走版本控制。
2. **规则与它的检查手段放在一起** —— `knowledge/invariants/` 指向 `rules/`，一起改、一起评审。
3. **跨运行的可变状态单独放 `state/`，并且尽量少。**

## 等级路线图

- **L1** 人审契约与 PR，一键发布加自动回滚（地基：契约体系 + 执行器适配）
  - ✅ `tools/spec-runner` 已落地（退出码→五态、五态门禁、边界强制、CLI；48 测试通过）
  - ✅ 6 个角色技能齐备（intent-compile / contract-author / ixd-bridge / impl-mobile / impl-service / test-author）
  - ✅ `tools/ixd2spec`（页面规约→契约 golden 义务）已落地
  - ✅ `tools/dtcg2flutter`（DTCG→Flutter 主题）已落地 + `custom_lint` 规则骨架
  - ⬜ evals 样本待填充；custom_lint 规则待 dart 环境验证
- **L1.5** 风险分级抽审，R0 自动合并，审计包归档
- **L2** 限定范围无人评审代码，反自洽四柱 + 确定性探索
- **L3**（仅试点）Agent 发起需求候选，宪章一致性 + 变更预算 + 月度漂移审计

详见 [方案原文](docs/)。
