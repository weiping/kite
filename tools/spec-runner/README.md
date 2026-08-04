# spec-runner

agent-spec 执行器适配与五态门禁。方案「契约怎么绑定测试」「退出码到五态的映射」的落地实现，是 L1 的承重墙。

## 命令

```bash
spec-runner run specs/ --out .out/                    # 执行契约绑定的测试
spec-runner gate .out/evidence.json --level L1        # 五态门禁
spec-runner affected --format json                    # 受影响路径（供策略门禁）
spec-runner allowed-changes <contract> [--only-impl]  # 契约允许的变更路径
spec-runner assert-no-boundary-violation <lifecycle.json>
```

## 五态

`pass | fail | skip | uncertain | pendingreview`

跳过永远阻断；不确定在 L2/L3 升级为人审级阻断。
