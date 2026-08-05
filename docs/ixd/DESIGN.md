# Kite Design System

> **单一事实源**。上半 YAML 令牌（DTCG 风格 `$value` + `$type`），下半散文说明**为什么**是这些值。
> 由 ixd-design **phase6** 产出；与 `phase5-components.md` 的 CSS 变量 token **同源双写**。
> CI 门禁：`npx -y @google/design.md lint/diff docs/ixd/DESIGN.md`；导出 DTCG 喂 `tools/dtcg2flutter`。

---
$schema: https://design-tokens.org/schema.json
color:
  primary:
    $value: "#3b82f6"
    $type: color
    $description: 主色，主操作/链接/选中态
  surface:
    $value: "#ffffff"
    $type: color
    $description: 卡片/组件背景
  onSurface:
    $value: "#1a1a1a"
    $type: color
    $description: 正文文字
  danger:
    $value: "#ef4444"
    $type: color
    $description: 错误/删除，不作装饰
space:
  sm:
    $value: "8px"
    $type: dimension
  md:
    $value: "16px"
    $type: dimension
  lg:
    $value: "24px"
    $type: dimension
---

## Color
主色是沉稳的蓝 #3B82F6，匹配「最低心智负担」的产品调性——可信、不刺激，适合速记优先的界面。
品牌色面积控制在 5-15%，避免喧宾夺主。`danger` 仅用于错误与删除，绝不作装饰用。

## Spacing
基于 4px 网格：sm=8 / md=16 / lg=24，覆盖紧凑 / 标准 / 宽松三档，保证跨页面视觉节奏一致。

## Typography
> 待 phase6 完整定义。倾向：中文 PingFang SC，正文 Body-M 14px / 22px 行高；数字用 tabular figures。

## Dark Mode
> 待 phase6 定义。策略倾向「跟随系统」；不用纯黑/纯白，主色在暗色下调整明度。
