"""ixd2spec：页面规约的状态流转 → 契约 golden 测试义务。"""
from ixd2spec.page import STANDARD_STATES, PageSpec, parse_page, to_scenarios


PAGE = """\
# 笔记详情页

## 状态

- 默认: 显示笔记正文
- 加载: 骨架屏
- 空数据: 空状态插画
- 报错: 错误提示与重试按钮
- 无权限: 无权限提示
- 离线: 离线提示
- 超长文本: 折叠并支持展开
"""


def test_parse_page_解析页面名与状态():
    page = parse_page(PAGE)
    assert page.name == "笔记详情页"
    assert len(page.states) == 7
    assert page.states[0] == ("默认", "显示笔记正文")


def test_parse_page_无状态段返回空():
    page = parse_page("# 某页\n\n只有正文\n")
    assert page.states == []


def test_standard_states_七种齐全():
    assert STANDARD_STATES == {
        "默认", "加载", "空数据", "报错", "无权限", "离线", "超长文本",
    }


def test_missing_states_指出缺失的标准状态():
    page = PageSpec(name="x", states=[("默认", "a"), ("加载", "b")])
    missing = page.missing_standard()
    assert "空数据" in missing
    assert "离线" in missing
    assert "默认" not in missing


def test_to_scenarios_每个状态生成一个dart_golden场景():
    page = parse_page(PAGE)
    blocks = to_scenarios(page, dart_test_dir="apps/mobile/test",
                          lib_path="apps/mobile/lib/note_detail.dart")
    assert len(blocks) == 7
    # 每块都是可被契约解析的 Scenario 文本
    assert blocks[0].startswith("Scenario: 笔记详情页-默认")
    assert "Package: dart" in blocks[0]
    assert "Level: golden" in blocks[0]
    assert "apps/mobile/lib/note_detail.dart" in blocks[0]


def test_to_scenarios_生成的场景能被contract解析回来():
    from spec_runner.contract import parse_contract

    page = parse_page(PAGE)
    blocks = to_scenarios(page, dart_test_dir="apps/mobile/test",
                          lib_path="apps/mobile/lib/note_detail.dart")
    contract_text = "---\nspec: task\nname: t\nsatisfies: []\n---\n\n## Completion Criteria\n\n" + "\n\n".join(blocks) + "\n"
    c = parse_contract(contract_text)
    assert len(c.scenarios) == 7
    assert c.scenarios[0].test.package == "dart"
    assert c.scenarios[0].test.level == "golden"
