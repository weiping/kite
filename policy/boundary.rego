package kite.boundary

# 边界与悬空选择器策略。
# TODO: 契约边界（Allowed Changes 之外的改动）与悬空测试选择器的具体规则集。
# 说明：本文 risk.rego 已含 boundary_violations / dangling_selectors 的 deny 兜底，
# 本文件用于承载更细粒度的边界判定规则（按路径前缀、按语言适配等），待落地时补全。
