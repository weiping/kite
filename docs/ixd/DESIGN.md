# Kite Design System

> **单一事实源**。上半 YAML 令牌（DTCG），下半散文说明**为什么**。
> 与 `phase5-components.md` 的 CSS 变量 token **同源双写**。
> CI 门禁：`npx -y @google/design.md lint docs/ixd/DESIGN.md`；导出 DTCG 喂 `tools/dtcg2flutter`。

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
  primaryDark:
    $value: "#60a5fa"
    $type: color
    $description: 主色暗色态（提亮以适应深背景）
  surfaceDark:
    $value: "#141414"
    $type: color
    $description: 暗色卡片背景（非纯黑）
  onSurfaceDark:
    $value: "#e8e8e8"
    $type: color
    $description: 暗色正文（非纯白）
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
typography:
  fontFamily:
    zh:
      $value: "PingFang SC"
      $type: fontFamily
      $description: 中文字体（iOS 系统字体，零加载，符合离线优先）
    en:
      $value: "Inter"
      $type: fontFamily
      $description: 英文字体，与中文节奏互补
  fontSize:
    body:
      $value: "14"
      $type: dimension
      $description: 正文 Body-M（移动端默认）
    h1:
      $value: "24"
      $type: dimension
      $description: 页面标题
---

## Color
主色 #3B82F6 是沉稳的蓝，匹配「最低心智负担」调性——可信、不刺激，适合速记优先的界面。
品牌色面积控制在 5-15%。`danger` 仅用于错误与删除。暗色态：主色提亮为 #60A5FA，背景用
#141414（非纯黑）、文字 #E8E8E8（非纯白），避免刺眼——符合 charter「安静」原则。

## Spacing
基于 4px 网格：sm=8 / md=16 / lg=24，覆盖紧凑 / 标准 / 宽松三档，保证跨页面视觉节奏一致。

## Typography
中文 PingFang SC（iOS 系统字体，零加载成本，契合离线优先）；英文 Inter。正文 Body-M 14px、
H1 24px。数字待补 tabular figures。

## Dark Mode
策略：**跟随系统**（契合 charter 不打扰）。不用纯黑/纯白，主色提亮；映射见 color tokens 的
`*Dark` 变体。
