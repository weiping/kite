package kite.reversibility

import data.reversibility as registry

# 找到匹配的登记项，多条匹配取最严的
matched[entry] {
  some f in input.changed_files
  some entry in registry
  glob.match(entry.pattern, ["/"], f)
}

ceiling := min([rank[e.ceiling] | some e in matched])

# 未登记路径落到最严档
deny contains msg if {
  some f in input.changed_files
  not covered(f)
  msg := sprintf("路径未登记撤销成本，请先补 reversibility.yaml: %s", [f])
}

covered(f) {
  some entry in registry
  glob.match(entry.pattern, ["/"], f)
}

# 副作用不可撤销的变更必须带影响面上限
deny contains msg if {
  some e in matched
  e.side_effects_reversible == false
  not e.blast_radius_cap
  msg := sprintf("副作用不可撤销但未设影响面上限: %s", [e.pattern])
}
