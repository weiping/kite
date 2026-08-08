# spec-runner

agent-spec 执行器适配与五态门禁。方案「契约怎么绑定测试」「退出码到五态的映射」的落地实现，是 L1 的承重墙。

## 命令

```bash
spec-runner run specs/ --out .out/                    # 执行契约绑定的测试
spec-runner gate .out/evidence.json --level L1        # 五态门禁
spec-runner affected --format json                    # 受影响路径（供策略门禁）
spec-runner allowed-changes <contract> [--only-impl]  # 契约允许的变更路径
spec-runner assert-no-boundary-violation <lifecycle.json>
spec-runner risk                                       # L1.5 风险分级 → {level, deny}
spec-runner audit-seal [--archive]                    # L1.5 审计包 → .out/audit/<commit>.json
spec-runner regression-check <spec>                    # L2 回归有效性验证
```

## regression-check（L2 回归有效性验证）

验证修复真的让测试从红变绿、且测试确实在测这个修复（反自洽链层 3）。

    spec-runner regression-check <spec>

假设工作区含修复（git diff 有改动）。`stash` 还原跑测试（期望红）→ `pop` 恢复跑（期望绿）。
`before=FAIL + after=PASS` 才有效；`before=PASS` 说明测试没测这个 bug（自洽但不正确）→ 退 1。

主要给 Agent 修复任务用：修完跑一遍再 commit。CI 接线（commit-ref 模式，HEAD vs HEAD~1）留后续。

## 五态

`pass | fail | skip | uncertain | pendingreview`

跳过永远阻断；不确定在 L2/L3 升级为人审级阻断。
