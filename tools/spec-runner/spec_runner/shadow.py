"""影子运行观测（L1.5→L2 切换准入）。

读 `.out/shadow.jsonl`（risk 评估每次追加），算 level 分布 + deny 率 + 一致性。
一致性规则：R0→auto（自动合）/ R1-R3→review（人审）算 match；其他 mismatch。
`human_decision` 为 null 的不比（未回填）。一致性 ≥90% 是 L1.5→L2 切换准入（index.md）。
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def shadow_report(jsonl_path) -> dict:
    """读 shadow.jsonl，算 level 分布 + deny 率 + 一致性（human_decision 非 null 的）。"""
    total = 0
    by_level: Counter = Counter()
    deny_count = 0
    compared = 0
    match = 0
    for line in Path(jsonl_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        total += 1
        level = rec.get("level", "?")
        by_level[level] += 1
        if rec.get("deny"):
            deny_count += 1
        hd = rec.get("human_decision")
        if hd is not None:
            compared += 1
            expected = "auto" if level == "R0" else "review"
            if hd == expected:
                match += 1
    return {
        "total": total,
        "by_level": dict(by_level),
        "deny_rate": deny_count / total if total else 0,
        "consistency": {
            "compared": compared,
            "match": match,
            "rate": match / compared if compared else None,
        },
    }
