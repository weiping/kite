"""把页面规约的「状态」段编译成契约的 golden 测试义务。

方案界面章：ixd-design 第四阶段的七种状态（默认/加载/空数据/报错/无权限/离线/超长文本）
恰好是 AI 写 UI 时最常漏的，编译成契约场景后每种绑一个 golden，就从文档变成机器可检查的义务。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

STANDARD_STATES = {
    "默认", "加载", "空数据", "报错", "无权限", "离线", "超长文本",
}

STATE_SLUG = {
    "默认": "default", "加载": "loading", "空数据": "empty",
    "报错": "error", "无权限": "forbidden", "离线": "offline", "超长文本": "overflow",
}


@dataclass
class PageSpec:
    name: str
    states: list[tuple[str, str]]

    def missing_standard(self) -> list[str]:
        return sorted(STANDARD_STATES - {name for name, _ in self.states})


def parse_page(text: str) -> PageSpec:
    name = ""
    for ln in text.splitlines():
        if ln.startswith("# "):
            name = ln[2:].strip()
            break
    return PageSpec(name=name, states=_parse_states(text))


def _parse_states(text: str) -> list[tuple[str, str]]:
    m = re.search(r"^##\s*状态\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return []
    states: list[tuple[str, str]] = []
    for ln in m.group(1).splitlines():
        s = ln.strip()
        if not s.startswith("-"):
            continue
        item = s.lstrip("- ").strip()
        key, sep, val = item.partition(":") if ":" in item else item.partition("：")
        states.append((key.strip(), val.strip()))
    return states


def to_scenarios(page: PageSpec, dart_test_dir: str, lib_path: str) -> list[str]:
    stem = Path(lib_path).stem
    blocks: list[str] = []
    for i, (state, desc) in enumerate(page.states):
        slug = STATE_SLUG.get(state, f"state{i}")
        filt = f"{dart_test_dir}/{stem}_{slug}_test.dart::test_{slug}_golden"
        blocks.append(
            f"Scenario: {page.name}-{state}\n"
            f"  Test:\n"
            f"    Package: dart\n"
            f"    Filter: {filt}\n"
            f"    Level: golden\n"
            f"    Targets: {lib_path}\n"
            f"  Given {state} {desc}\n"
            f"  When 渲染\n"
            f"  Then 匹配 golden 截图"
        )
    return blocks
