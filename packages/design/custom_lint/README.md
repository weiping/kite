# kite_design_lint

Kite 设计系统的 custom_lint 规则。方案「界面」章：**Flutter 侧禁止任何硬编码样式值**，
用 `custom_lint` 拦截裸颜色值与裸间距——这条消灭了 AI 生成 UI 最常见的不一致来源。

## 规则

| 规则 | 拦截 | 正确做法 |
| --- | --- | --- |
| `kite_no_hardcoded_color` | 裸 `Color(0xFF...)` | 用 `AppColors.xxx` |
| `kite_no_hardcoded_spacing` | `EdgeInsets` 等里的裸 `double` | 用 `AppSpacing.xxx` |

样式值的单一事实源是 `packages/design/app_tokens.dart`（由 `tools/dtcg2flutter` 从 `docs/ixd/tokens.json` 生成）。
令牌文件本身允许字面量（豁免）。

## 状态

骨架。`custom_lint_builder` 的注册 API 与 `analyzer` 版本会变，接入 dart 环境时：

```bash
cd packages/design/custom_lint
dart pub add custom_lint analyzer
dart pub get
# 在客户端 analysis_options.yaml 启用：
#   custom_lint:
#     rules:
#       - kite_no_hardcoded_color
#       - kite_no_hardcoded_spacing
```
