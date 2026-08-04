// Kite 设计系统 custom_lint 入口。
// 方案：Flutter 侧禁止任何硬编码样式值，用 custom_lint 拦截裸颜色值与裸间距。
// 这是消灭 AI 生成 UI 最常见不一致来源的关键规则。
//
// 状态：骨架。custom_lint_builder 的 API 随版本变动，需在 dart 环境跑通后微调。
import 'package:custom_lint_builder/custom_lint_builder.dart';

import 'no_hardcoded_style.dart';

PluginBase createPlugin() => _KiteDesignPlugin();

class _KiteDesignPlugin extends PluginBase {
  @override
  List<LintRule> getLintRules(CustomLintConfigs configs) => [
        NoHardcodedColorRule(),
        NoHardcodedSpacingRule(),
      ];
}
