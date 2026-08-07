"""本地检索契约测试：关键词匹配+来源、无匹配未找到、离线纯函数。"""
from hypothesis import given, strategies as st

from services.capture.classify import Item
from services.capture.search import search


def test_keyword_match_with_source():
    """含查询词的 item 被匹配，且结果附来源（item 本身）。"""
    item = Item("note", "买牛奶", "明天要买牛奶")
    r = search([item], "牛奶")
    assert r.found
    assert r.matches[0].item is item  # 来源引用


@given(
    needles=st.lists(st.text(min_size=2, max_size=4, alphabet="abcdef"), min_size=1, max_size=4),
)
def test_no_match_returns_not_found(needles):
    """查询词与 item 无关 → found 为 False，不编造。"""
    items = [Item("note", "天气晴朗", "今天天气不错")]
    # needles 用 abcdef 字母表，不会命中中文 item
    query = "".join(needles)
    r = search(items, query)
    assert r.found is False


def test_offline_pure():
    """检索是纯函数：同输入同输出，不依赖网络/模型。"""
    items = [Item("task", "写报告", "要写季度报告")]
    r1 = search(items, "报告")
    r2 = search(items, "报告")
    assert r1 == r2
    assert r1.found
