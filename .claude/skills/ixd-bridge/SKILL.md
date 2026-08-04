---
name: ixd-bridge
description: 把逐页交互说明（doc/ixd/pages）的状态流转编译成契约的 golden 测试义务。
allowed-tools: Read, Write
---

# 交互设计 → 契约桥接

ixd-design 第四阶段的逐页说明里有一节专讲状态流转。那七种状态——默认、加载、空数据、报错、
无权限、离线、超长文本——恰好是 AI 写 UI 时最常漏掉的。你的工作是把它们从文档变成机器可检查的义务。

## 输入
- `doc/ixd/pages/*.md` 逐页规约，尤其状态矩阵那节
- `doc/ixd/sdui-components.json` 组件白名单（产出只能引用白名单组件）
- 已有契约 `specs/*.spec.md`（决定是新增场景还是追加到既有契约）

## 规则
1. 每种状态生成一条 Scenario，绑定一个 golden 测试选择器（`Package: dart`）
2. 场景名要可读：`详情页-离线态-显示离线提示` 而非 `state_6`
3. 状态矩阵从 N 种变 N+1 种时，必须产出对应的新义务，不能只在文档里加一行
4. 下发内容只能引用 `sdui-components.json` 白名单组件——这是 INV-005，三方对齐脚本会检查
5. 不写实现、不写 Flutter 代码；你产出的是「要被满足的验收」，不是「怎么画」

## 输出
- 契约 Scenario 片段（追加进 specs，或由 contract-author 合入）
- 对应的 golden 截图路径登记

第八阶段的 HTML 原型是**验收标准，不是要翻译成 Flutter 的源**。三方对照（页面规约 / 原型 / golden）
不一致时优先怀疑实现。落盘与提交由编排层执行。
