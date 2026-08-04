// 两条规则：拦截裸 Color(...) 与裸间距（EdgeInsets 里的 double 字面量）。
// 命中时提示改用 packages/design/app_tokens.dart 里的令牌（AppColors / AppSpacing）。
//
// 状态：骨架。仅当硬编码出现在「app_tokens.dart 之外」才算违规——令牌文件本身允许字面量。
// 完整的文件路径豁免与 AST 细节需在 dart 环境对齐 analyzer 版本后验证。
import 'package:analyzer/dart/ast/ast.dart';
import 'package:analyzer/dart/ast/visitor.dart';
import 'package:custom_lint_builder/custom_lint_builder.dart';

class NoHardcodedColorRule extends LintRule {
  NoHardcodedColorRule()
      : super(
          code: const LintCode(
            name: 'kite_no_hardcoded_color',
            problemMessage: '禁止硬编码颜色，请使用 AppColors 的令牌（packages/design）。',
          ),
        );
}

class NoHardcodedSpacingRule extends LintRule {
  NoHardcodedSpacingRule()
      : super(
          code: const LintCode(
            name: 'kite_no_hardcoded_spacing',
            problemMessage: '禁止硬编码间距，请使用 AppSpacing 的令牌（packages/design）。',
          ),
        );
}

// 规则的 visit 逻辑示意（实际实现需注册 LintRuleNodeRegistry 回调）：
//   registry.addInstanceCreationExpression((node, reporter) {
//     final type = node.constructorName.type.type;
//     if (type?.name == 'Color' && !_inTokensFile(node)) {
//       reporter.reportNode(node);
//     }
//   });
