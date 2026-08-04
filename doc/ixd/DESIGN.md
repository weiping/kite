<!--
  doc/ixd/DESIGN.md
  设计系统单一事实源。上半 YAML 设计令牌给精确值，下半散文说明为什么是这些值。
  格式遵循 google-labs-code/design.md。
  CI 门禁：
    npx -y @google/design.md lint doc/ixd/DESIGN.md            # 结构、引用、对比度
    npx -y @google/design.md diff /tmp/base.md DESIGN.md        # 回归检测，退出码 1 阻断
    npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json
  导出的令牌由 tools/dtcg2flutter 编译为 Flutter 主题（packages/design/）。
  本文件为占位，落地时由 ixd-design 技能第四至六阶段产出。
-->
# Kite Design System

<!-- TODO: tokens + prose -->
