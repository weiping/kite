package kite.risk

# R3：能修改自己门禁配置的 Agent 等于没有门禁，这四个目录永久最严档
r3 if { some f in input.changed_files; startswith(f, "charter/") }
r3 if { some f in input.changed_files; startswith(f, ".github/workflows/") }
r3 if { some f in input.changed_files; startswith(f, ".claude/skills/") }
r3 if { some f in input.changed_files; startswith(f, "policy/") }
r3 if { some f in input.changed_files; startswith(f, "knowledge/invariants/") }

# R2：同步协议、认证、计费、数据迁移、渲染器
r2 if {
  some f in input.changed_files
  regex.match(`(sync|auth|billing|migrations|sdui_render)`, f)
}

level := "R3" if r3
else := "R2" if r2
else := "R1" if { input.changed_lines > 50 }
else := "R0"

# 悬空选择器与边界越界，任何等级下都阻断
deny contains msg if {
  some s in input.dangling_selectors
  msg := sprintf("测试选择器不存在: %s", [s])
}
deny contains msg if {
  input.boundary_violations > 0
  msg := "存在契约边界之外的改动"
}
