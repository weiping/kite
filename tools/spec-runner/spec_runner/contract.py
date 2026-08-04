"""任务契约解析：把 specs/*.spec.md 解析成结构化的 Contract。

契约格式见方案「规约：用现成的，不要自己造」。一个契约含：
frontmatter（spec/name/satisfies/risk）+ Boundaries（Allowed Changes / Forbidden）
+ Completion Criteria（若干 Scenario，每个绑定一个测试选择器）。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

_FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
_TEST_KEYS = ("Package", "Filter", "Level", "Targets")
_GWT_KEYS = ("Given", "When", "Then")


@dataclass(frozen=True)
class TestSelector:
    package: str          # py | dart | semgrep
    filter: str           # 测试选择器，如 tests/x.py::test_y
    level: str            # unit | property | static
    targets: tuple[str, ...]


@dataclass(frozen=True)
class Scenario:
    name: str
    test: TestSelector
    given: str
    when: str
    then: str


@dataclass(frozen=True)
class Contract:
    spec: str
    name: str
    satisfies: tuple[str, ...]
    risk: str | None
    allowed_changes: tuple[str, ...]
    forbidden: tuple[str, ...]
    scenarios: tuple[Scenario, ...]


def parse_contract(text: str) -> Contract:
    m = _FRONT_RE.match(text)
    if not m:
        raise ValueError("契约缺少 frontmatter（--- ... ---）")
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    allowed, forbidden = _parse_boundaries(body)
    return Contract(
        spec=meta.get("spec", ""),
        name=meta.get("name", ""),
        satisfies=tuple(meta.get("satisfies") or ()),
        risk=meta.get("risk"),
        allowed_changes=tuple(allowed),
        forbidden=tuple(forbidden),
        scenarios=tuple(_parse_scenarios(body)),
    )


def parse_contract_file(path: str | Path) -> Contract:
    return parse_contract(Path(path).read_text(encoding="utf-8"))


def _section(body: str, heading: str) -> str | None:
    m = re.search(
        rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)",
        body, re.M | re.S,
    )
    return m.group(1) if m else None


def _list_under(parent: str, subheading: str) -> list[str]:
    m = re.search(
        rf"^###\s+{re.escape(subheading)}\s*\n(.*?)(?=^###\s|^##\s|\Z)",
        parent, re.M | re.S,
    )
    if not m:
        return []
    return [
        ln.lstrip("- ").strip()
        for ln in m.group(1).splitlines()
        if ln.strip().startswith("-")
    ]


def _parse_boundaries(body: str) -> tuple[list[str], list[str]]:
    sec = _section(body, "Boundaries") or ""
    return _list_under(sec, "Allowed Changes"), _list_under(sec, "Forbidden")


def _parse_scenarios(body: str) -> list[Scenario]:
    crit = _section(body, "Completion Criteria")
    if not crit:
        return []
    # 按 `Scenario:` 行切分，首块是标题前的内容，丢弃。
    blocks = re.split(r"^Scenario:\s*", crit, flags=re.M)
    return [_parse_scenario_block(b) for b in blocks[1:] if b.strip()]


def _parse_scenario_block(block: str) -> Scenario:
    lines = block.splitlines()
    name = lines[0].strip()
    fields: dict[str, object] = {k: "" for k in _TEST_KEYS if k != "Targets"}
    fields["Targets"] = []
    gwt: dict[str, str] = {k: "" for k in _GWT_KEYS}
    for raw in lines[1:]:
        s = raw.strip()
        if not s or s == "Test:":
            continue
        head = s.split(None, 1)
        key = head[0].rstrip(":")
        val = head[1].strip() if len(head) > 1 else ""
        if key in _GWT_KEYS:
            gwt[key] = val
        elif key == "Targets":
            fields["Targets"].extend(t.strip() for t in val.split(",") if t.strip())
        elif key in fields:
            fields[key] = val
    selector = TestSelector(
        package=fields["Package"],
        filter=fields["Filter"],
        level=fields["Level"],
        targets=tuple(fields["Targets"]),
    )
    return Scenario(name=name, test=selector, given=gwt["Given"], when=gwt["When"], then=gwt["Then"])
